#!/usr/bin/env python3
"""Dependency-free MCP server for Feishu docx and Bitable workflows."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SERVER_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_URL = "https://open.feishu.cn"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"
SERVER_VERSION = "0.2.0"


def load_dotenv(path: Path) -> None:
    """Load a small .env file without overwriting existing environment variables."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


if os.getenv("FEISHU_SKIP_DOTENV", "").strip() != "1":
    load_dotenv(SERVER_DIR / ".env")


class FeishuError(RuntimeError):
    """A readable Feishu API error."""


def extract_document_id(value: str) -> str:
    """Accept either a raw docx document ID or a Feishu document URL."""
    value = (value or "").strip()
    if not value:
        raise ValueError("请提供飞书文档链接或 document_id。")

    parsed = urllib.parse.urlparse(value)
    if parsed.scheme and parsed.netloc:
        match = re.search(r"/docx/([A-Za-z0-9_-]+)", parsed.path)
        if match:
            return match.group(1)
        if "/wiki/" in parsed.path:
            raise ValueError(
                "当前版本暂不直接解析知识库 /wiki/ 链接。请打开知识库中的原始文档，"
                "复制包含 /docx/ 的链接。"
            )
        raise ValueError("链接中未找到 /docx/{document_id}。请复制新版飞书文档链接。")

    if re.fullmatch(r"[A-Za-z0-9_-]{8,128}", value):
        return value
    raise ValueError("document_id 格式不正确。可直接粘贴完整的飞书 docx 链接。")


def parse_bitable_reference(value: str, table_id: str = "") -> Dict[str, str]:
    """Parse a Feishu Bitable URL or raw app_token without making a network request."""
    value = (value or "").strip()
    table_id = (table_id or "").strip()
    if not value:
        raise ValueError("请提供飞书多维表格链接或 app_token。")

    result = {
        "source_type": "token",
        "source_token": "",
        "app_token": "",
        "wiki_token": "",
        "table_id": table_id,
    }
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme and parsed.netloc:
        base_match = re.search(r"/base/([A-Za-z0-9_-]+)", parsed.path)
        wiki_match = re.search(r"/wiki/([A-Za-z0-9_-]+)", parsed.path)
        query = urllib.parse.parse_qs(parsed.query)
        url_table_id = (query.get("table") or query.get("table_id") or [""])[0].strip()
        if not result["table_id"]:
            result["table_id"] = url_table_id
        if base_match:
            result.update(
                {
                    "source_type": "base",
                    "source_token": base_match.group(1),
                    "app_token": base_match.group(1),
                }
            )
        elif wiki_match:
            result.update(
                {
                    "source_type": "wiki",
                    "source_token": wiki_match.group(1),
                    "wiki_token": wiki_match.group(1),
                }
            )
        else:
            raise ValueError(
                "链接中未找到 /base/{app_token} 或 /wiki/{wiki_token}。"
                "请复制多维表格当前页面的完整链接。"
            )
    elif re.fullmatch(r"[A-Za-z0-9_-]{8,128}", value):
        result["source_token"] = value
        result["app_token"] = value
    else:
        raise ValueError("app_token 格式不正确。可直接粘贴完整的飞书多维表格链接。")

    if result["table_id"] and not re.fullmatch(r"[A-Za-z0-9_-]{4,128}", result["table_id"]):
        raise ValueError("table_id 格式不正确。请从链接的 table= 参数复制。")
    return result


def chunk_text(text: str, limit: int = 1800) -> Iterable[str]:
    """Split long text into conservative block sizes."""
    remaining = text
    while len(remaining) > limit:
        split_at = max(
            remaining.rfind("\n", 0, limit),
            remaining.rfind("。", 0, limit),
            remaining.rfind(" ", 0, limit),
        )
        if split_at < limit // 2:
            split_at = limit
        else:
            split_at += 1
        yield remaining[:split_at]
        remaining = remaining[split_at:]
    if remaining:
        yield remaining


def _text_block(block_type: int, field: str, content: str) -> Dict[str, Any]:
    return {
        "block_type": block_type,
        field: {
            "elements": [{"text_run": {"content": content}}],
            "style": {},
        },
    }


def markdown_to_blocks(content: str) -> List[Dict[str, Any]]:
    """Convert a safe Markdown subset into Feishu text blocks."""
    if not content or not content.strip():
        raise ValueError("写入内容不能为空。")
    if len(content) > 200_000:
        raise ValueError("单次写入内容过长，请拆成不超过 20 万字符的多次操作。")

    blocks: List[Dict[str, Any]] = []
    for raw_line in content.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            continue

        block_type, field, text = 2, "text", line
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        bullet = re.match(r"^\s*[-*+]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            block_type, field, text = 2 + level, f"heading{level}", heading.group(2)
        elif bullet:
            block_type, field, text = 12, "bullet", bullet.group(1)
        elif ordered:
            block_type, field, text = 13, "ordered", ordered.group(1)

        for piece in chunk_text(text):
            blocks.append(_text_block(block_type, field, piece))
    if not blocks:
        raise ValueError("没有可写入的文本内容。")
    return blocks


class FeishuClient:
    def __init__(self) -> None:
        self.app_id = os.getenv("FEISHU_APP_ID", "").strip()
        self.app_secret = os.getenv("FEISHU_APP_SECRET", "").strip()
        self.user_access_token = os.getenv("FEISHU_USER_ACCESS_TOKEN", "").strip()
        self.base_url = os.getenv("FEISHU_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        self._tenant_token = ""
        self._tenant_token_expires_at = 0.0

    @property
    def auth_mode(self) -> str:
        return "user_access_token" if self.user_access_token else "tenant_access_token"

    @property
    def configured(self) -> bool:
        return bool(self.user_access_token or (self.app_id and self.app_secret))

    def _request_json(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        authenticated: bool = True,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self.access_token()}"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                log_id = response.headers.get("X-Tt-Logid", "")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            log_id = exc.headers.get("X-Tt-Logid", "") if exc.headers else ""
            try:
                detail = json.loads(raw)
                message = detail.get("msg") or detail.get("message") or raw
                code = detail.get("code", exc.code)
            except json.JSONDecodeError:
                message, code = raw or exc.reason, exc.code
            suffix = f"，X-Tt-Logid: {log_id}" if log_id else ""
            raise FeishuError(f"飞书接口失败（{code}）：{message}{suffix}") from exc
        except urllib.error.URLError as exc:
            raise FeishuError(f"无法连接飞书开放平台：{exc.reason}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FeishuError("飞书返回了无法解析的响应。") from exc
        if payload.get("code", 0) != 0:
            suffix = f"，X-Tt-Logid: {log_id}" if log_id else ""
            raise FeishuError(
                f"飞书接口失败（{payload.get('code')}）：{payload.get('msg', '未知错误')}{suffix}"
            )
        return payload

    def _upload_media(self, parent_node: str, file_path: str) -> str:
        """Upload one <=20 MB attachment to a Bitable app and return its file_token."""
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"附件文件不存在：{path}")
        size = path.stat().st_size
        if size > 20 * 1024 * 1024:
            raise ValueError("单个附件超过 20 MB；当前连接器只使用飞书整文件上传接口。")
        if len(path.name) > 250:
            raise ValueError("附件文件名超过飞书允许的 250 个字符。")

        boundary = f"----CodexFeishu{secrets.token_hex(16)}"
        chunks: List[bytes] = []

        def add_text_field(name: str, value: str) -> None:
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode("ascii"),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
                    value.encode("utf-8"),
                    b"\r\n",
                ]
            )

        add_text_field("file_name", path.name)
        add_text_field("parent_type", "bitable_file")
        add_text_field("parent_node", parent_node)
        add_text_field("size", str(size))
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        safe_name = path.name.replace('"', "_")
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                (
                    f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("ascii"),
                path.read_bytes(),
                b"\r\n",
                f"--{boundary}--\r\n".encode("ascii"),
            ]
        )
        request = urllib.request.Request(
            f"{self.base_url}/open-apis/drive/v1/medias/upload_all",
            data=b"".join(chunks),
            headers={
                "Authorization": f"Bearer {self.access_token()}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read().decode("utf-8")
                log_id = response.headers.get("X-Tt-Logid", "")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            log_id = exc.headers.get("X-Tt-Logid", "") if exc.headers else ""
            try:
                detail = json.loads(raw)
                message = detail.get("msg") or detail.get("message") or raw
                code = detail.get("code", exc.code)
            except json.JSONDecodeError:
                message, code = raw or exc.reason, exc.code
            suffix = f"，X-Tt-Logid: {log_id}" if log_id else ""
            raise FeishuError(f"飞书附件上传失败（{code}）：{message}{suffix}") from exc
        except urllib.error.URLError as exc:
            raise FeishuError(f"无法连接飞书开放平台：{exc.reason}") from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FeishuError("飞书附件上传返回了无法解析的响应。") from exc
        if payload.get("code", 0) != 0:
            suffix = f"，X-Tt-Logid: {log_id}" if log_id else ""
            raise FeishuError(
                f"飞书附件上传失败（{payload.get('code')}）："
                f"{payload.get('msg', '未知错误')}{suffix}"
            )
        file_token = payload.get("data", {}).get("file_token")
        if not file_token:
            raise FeishuError("飞书附件上传成功响应中没有 file_token。")
        return str(file_token)

    def access_token(self) -> str:
        if self.user_access_token:
            return self.user_access_token
        if not self.app_id or not self.app_secret:
            raise FeishuError(
                "尚未配置飞书凭证。请把 feishu-mcp/.env.example 复制为 .env，"
                "再填写 FEISHU_APP_ID 和 FEISHU_APP_SECRET。"
            )
        if self._tenant_token and time.time() < self._tenant_token_expires_at:
            return self._tenant_token
        payload = self._request_json(
            "POST",
            "/open-apis/auth/v3/tenant_access_token/internal",
            {"app_id": self.app_id, "app_secret": self.app_secret},
            authenticated=False,
        )
        self._tenant_token = payload["tenant_access_token"]
        expires_in = int(payload.get("expire", 7200))
        self._tenant_token_expires_at = time.time() + max(60, expires_in - 300)
        return self._tenant_token

    def connection_check(self) -> Dict[str, Any]:
        if not self.configured:
            return {
                "ok": False,
                "configured": False,
                "message": "连接器已运行，但尚未填写飞书凭证。",
                "next_step": "复制 .env.example 为 .env，并填写 App ID 与 App Secret。",
            }
        token = self.access_token()
        return {
            "ok": True,
            "configured": True,
            "auth_mode": self.auth_mode,
            "token_received": bool(token),
            "message": "已成功取得飞书访问凭证。文档读写权限仍需用目标文档验证。",
        }

    def document_info(self, document: str) -> Dict[str, Any]:
        document_id = extract_document_id(document)
        payload = self._request_json(
            "GET", f"/open-apis/docx/v1/documents/{urllib.parse.quote(document_id)}"
        )
        return payload.get("data", {}).get("document", payload.get("data", {}))

    def read_document(self, document: str) -> Dict[str, Any]:
        document_id = extract_document_id(document)
        encoded = urllib.parse.quote(document_id)
        payload = self._request_json(
            "GET", f"/open-apis/docx/v1/documents/{encoded}/raw_content?lang=0"
        )
        data = payload.get("data", {})
        return {
            "document_id": document_id,
            "content": data.get("content", ""),
            "revision_id": data.get("revision_id"),
        }

    def create_document(
        self, title: str, folder_token: str = "", content: str = ""
    ) -> Dict[str, Any]:
        title = (title or "").strip()
        if not title:
            raise ValueError("文档标题不能为空。")
        body: Dict[str, Any] = {"title": title[:800]}
        if folder_token.strip():
            body["folder_token"] = folder_token.strip()
        payload = self._request_json("POST", "/open-apis/docx/v1/documents", body)
        document = payload.get("data", {}).get("document", {})
        document_id = document.get("document_id")
        if not document_id:
            raise FeishuError("文档创建成功响应中没有 document_id。")
        result: Dict[str, Any] = {
            "document_id": document_id,
            "title": document.get("title", title),
            "url": f"https://feishu.cn/docx/{document_id}",
        }
        if content.strip():
            result["write_result"] = self.append_document(document_id, content)
        return result

    def append_document(self, document: str, content: str) -> Dict[str, Any]:
        document_id = extract_document_id(document)
        blocks = markdown_to_blocks(content)
        created = 0
        revision_id: Optional[int] = None
        encoded = urllib.parse.quote(document_id)
        for start in range(0, len(blocks), 50):
            batch = blocks[start : start + 50]
            payload = self._request_json(
                "POST",
                f"/open-apis/docx/v1/documents/{encoded}/blocks/{encoded}/children",
                {"children": batch, "index": -1},
            )
            data = payload.get("data", {})
            created += len(data.get("children", batch))
            revision_id = data.get("document_revision_id", revision_id)
        return {
            "document_id": document_id,
            "created_blocks": created,
            "document_revision_id": revision_id,
            "url": f"https://feishu.cn/docx/{document_id}",
        }

    def _list_bitable_tables_by_token(self, app_token: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        page_token = ""
        encoded_app = urllib.parse.quote(app_token, safe="")
        while True:
            query = {"page_size": "100"}
            if page_token:
                query["page_token"] = page_token
            payload = self._request_json(
                "GET",
                f"/open-apis/bitable/v1/apps/{encoded_app}/tables?{urllib.parse.urlencode(query)}",
            )
            data = payload.get("data", {})
            items.extend(data.get("items") or [])
            if not data.get("has_more"):
                return items
            page_token = str(data.get("page_token") or "")
            if not page_token:
                raise FeishuError("飞书返回 has_more=true，但没有 page_token。")

    def resolve_bitable(self, bitable: str, table_id: str = "") -> Dict[str, Any]:
        reference = parse_bitable_reference(bitable, table_id)
        app_token = reference["app_token"]
        if reference["source_type"] == "wiki":
            query = urllib.parse.urlencode({"token": reference["wiki_token"]})
            payload = self._request_json(
                "GET", f"/open-apis/wiki/v2/spaces/get_node?{query}"
            )
            node = payload.get("data", {}).get("node", {})
            if node.get("obj_type") != "bitable" or not node.get("obj_token"):
                raise ValueError("该知识库链接指向的不是多维表格，无法写入记录。")
            app_token = str(node["obj_token"])

        selected_table_id = reference["table_id"]
        tables: List[Dict[str, Any]] = []
        if not selected_table_id:
            tables = self._list_bitable_tables_by_token(app_token)
            if len(tables) == 1:
                selected_table_id = str(tables[0].get("table_id") or "")
            elif not tables:
                raise ValueError("该多维表格中没有可用的数据表。")
            else:
                choices = "、".join(
                    f"{item.get('name', '未命名')} ({item.get('table_id', '')})"
                    for item in tables[:10]
                )
                raise ValueError(
                    "这个多维表格包含多个数据表，请使用带 table= 参数的完整链接，"
                    f"或单独提供 table_id。可选数据表：{choices}"
                )
        return {
            "app_token": app_token,
            "table_id": selected_table_id,
            "source_type": reference["source_type"],
            "tables": tables,
        }

    def list_bitable_fields(self, app_token: str, table_id: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        page_token = ""
        encoded_app = urllib.parse.quote(app_token, safe="")
        encoded_table = urllib.parse.quote(table_id, safe="")
        while True:
            query = {"page_size": "100"}
            if page_token:
                query["page_token"] = page_token
            payload = self._request_json(
                "GET",
                f"/open-apis/bitable/v1/apps/{encoded_app}/tables/{encoded_table}/fields?"
                f"{urllib.parse.urlencode(query)}",
            )
            data = payload.get("data", {})
            items.extend(data.get("items") or [])
            if not data.get("has_more"):
                return items
            page_token = str(data.get("page_token") or "")
            if not page_token:
                raise FeishuError("飞书返回 has_more=true，但没有 page_token。")

    def inspect_bitable(self, bitable: str, table_id: str = "") -> Dict[str, Any]:
        resolved = self.resolve_bitable(bitable, table_id)
        fields = self.list_bitable_fields(resolved["app_token"], resolved["table_id"])
        return {
            "app_token": resolved["app_token"],
            "table_id": resolved["table_id"],
            "source_type": resolved["source_type"],
            "fields": [
                {
                    "field_id": item.get("field_id"),
                    "field_name": item.get("field_name"),
                    "type": item.get("type"),
                    "ui_type": item.get("ui_type"),
                    "is_primary": item.get("is_primary", False),
                }
                for item in fields
            ],
            "url": (
                f"https://feishu.cn/base/{resolved['app_token']}"
                f"?table={resolved['table_id']}"
            ),
        }

    def append_bitable_record(
        self,
        bitable: str,
        fields: Dict[str, Any],
        table_id: str = "",
        attachments: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        attachments = attachments or {}
        if not isinstance(fields, dict):
            raise ValueError("fields 必须是对象，键为多维表格中的列名。")
        if not isinstance(attachments, dict):
            raise ValueError("attachments 必须是对象，键为附件列名，值为本机文件路径。")
        if not fields and not attachments:
            raise ValueError("fields 和 attachments 不能同时为空。")
        if len(fields) > 500:
            raise ValueError("单条记录的字段过多，请控制在 500 个以内。")

        resolved = self.resolve_bitable(bitable, table_id)
        schema = self.list_bitable_fields(resolved["app_token"], resolved["table_id"])
        schema_by_name = {
            str(item.get("field_name")): item for item in schema if item.get("field_name")
        }
        known_names = set(schema_by_name)
        unknown_names = sorted((set(fields) | set(attachments)) - known_names)
        if unknown_names:
            available = "、".join(sorted(known_names))
            raise ValueError(
                f"以下字段在目标数据表中不存在：{'、'.join(unknown_names)}。"
                f"可用字段：{available}"
            )

        outgoing_fields = dict(fields)
        uploaded: Dict[str, List[Dict[str, str]]] = {}
        for field_name, raw_paths in attachments.items():
            field_meta = schema_by_name[field_name]
            if int(field_meta.get("type") or 0) != 17:
                raise ValueError(f"字段“{field_name}”不是附件类型，不能上传文件。")
            paths = raw_paths if isinstance(raw_paths, list) else [raw_paths]
            if not paths or not all(isinstance(item, str) and item.strip() for item in paths):
                raise ValueError(f"附件字段“{field_name}”必须提供一个或多个本机文件路径。")
            uploaded[field_name] = [
                {"file_token": self._upload_media(resolved["app_token"], item)}
                for item in paths
            ]
            outgoing_fields[field_name] = uploaded[field_name]

        encoded_app = urllib.parse.quote(resolved["app_token"], safe="")
        encoded_table = urllib.parse.quote(resolved["table_id"], safe="")
        payload = self._request_json(
            "POST",
            f"/open-apis/bitable/v1/apps/{encoded_app}/tables/{encoded_table}/records",
            {"fields": outgoing_fields},
        )
        record = payload.get("data", {}).get("record", {})
        return {
            "app_token": resolved["app_token"],
            "table_id": resolved["table_id"],
            "record_id": record.get("record_id"),
            "created_time": record.get("created_time"),
            "fields": record.get("fields", outgoing_fields),
            "uploaded_attachment_fields": sorted(uploaded),
            "url": (
                f"https://feishu.cn/base/{resolved['app_token']}"
                f"?table={resolved['table_id']}"
            ),
        }


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "feishu_connection_check",
        "description": "检查飞书凭证是否已配置，并验证能否取得访问凭证。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "feishu_get_document_info",
        "description": "获取飞书新版文档的标题、版本和基本信息。可传完整 docx 链接或 document_id。",
        "inputSchema": {
            "type": "object",
            "properties": {"document": {"type": "string", "description": "飞书 docx 链接或 document_id"}},
            "required": ["document"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "feishu_read_document",
        "description": "读取飞书新版文档的纯文本内容。可传完整 docx 链接或 document_id。",
        "inputSchema": {
            "type": "object",
            "properties": {"document": {"type": "string", "description": "飞书 docx 链接或 document_id"}},
            "required": ["document"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "feishu_create_document",
        "description": "创建飞书新版文档，可同时写入初始内容。内容支持标题、无序列表和有序列表的简单 Markdown。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "文档标题"},
                "folder_token": {"type": "string", "description": "可选的目标文件夹 token"},
                "content": {"type": "string", "description": "可选的初始内容"},
            },
            "required": ["title"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False},
    },
    {
        "name": "feishu_append_document",
        "description": "把内容追加到飞书新版文档末尾。不会删除或覆盖原内容。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {"type": "string", "description": "飞书 docx 链接或 document_id"},
                "content": {"type": "string", "description": "要追加的内容，支持简单 Markdown"},
            },
            "required": ["document", "content"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False},
    },
    {
        "name": "feishu_bitable_inspect",
        "description": (
            "读取飞书多维表格的数据表和字段结构。支持 /base/ 或 /wiki/ 完整链接；"
            "不会修改表格。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bitable": {
                    "type": "string",
                    "description": "飞书多维表格完整链接或 app_token",
                },
                "table_id": {
                    "type": "string",
                    "description": "可选；链接没有 table= 参数时可单独提供",
                },
            },
            "required": ["bitable"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    {
        "name": "feishu_bitable_append_record",
        "description": (
            "向飞书多维表格追加一条记录。写入前会读取字段结构并拒绝不存在的列名；"
            "不会覆盖或删除原记录。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bitable": {
                    "type": "string",
                    "description": "飞书多维表格完整链接或 app_token",
                },
                "table_id": {
                    "type": "string",
                    "description": "可选；链接没有 table= 参数时可单独提供",
                },
                "fields": {
                    "type": "object",
                    "description": "一条记录；键必须是目标数据表中的真实列名",
                    "additionalProperties": True,
                },
                "attachments": {
                    "type": "object",
                    "description": (
                        "可选；键为附件类型列名，值为本机文件路径或路径数组。"
                        "连接器会先上传文件再写入 file_token"
                    ),
                    "additionalProperties": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}, "minItems": 1},
                        ]
                    },
                },
            },
            "required": ["bitable", "fields"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False},
    },
]


def tool_result(value: Any, is_error: bool = False) -> Dict[str, Any]:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    result: Dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def call_tool(client: FeishuClient, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "feishu_connection_check":
        return tool_result(client.connection_check())
    if name == "feishu_get_document_info":
        return tool_result(client.document_info(arguments.get("document", "")))
    if name == "feishu_read_document":
        return tool_result(client.read_document(arguments.get("document", "")))
    if name == "feishu_create_document":
        return tool_result(
            client.create_document(
                arguments.get("title", ""),
                arguments.get("folder_token", ""),
                arguments.get("content", ""),
            )
        )
    if name == "feishu_append_document":
        return tool_result(
            client.append_document(arguments.get("document", ""), arguments.get("content", ""))
        )
    if name == "feishu_bitable_inspect":
        return tool_result(
            client.inspect_bitable(arguments.get("bitable", ""), arguments.get("table_id", ""))
        )
    if name == "feishu_bitable_append_record":
        return tool_result(
            client.append_bitable_record(
                arguments.get("bitable", ""),
                arguments.get("fields") or {},
                arguments.get("table_id", ""),
                arguments.get("attachments") or {},
            )
        )
    raise ValueError(f"未知工具：{name}")


def dispatch(message: Dict[str, Any], client: FeishuClient) -> Optional[Dict[str, Any]]:
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        return None
    try:
        if method == "initialize":
            requested = message.get("params", {}).get("protocolVersion")
            result = {
                "protocolVersion": requested or DEFAULT_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "feishu-docs-bitable", "version": SERVER_VERSION},
                "instructions": (
                    "Use read tools freely. Creating or appending changes Feishu cloud documents "
                    "or Bitable records; confirm the target when the user's wording is ambiguous. "
                    "This server appends content and does not overwrite existing content."
                ),
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = message.get("params", {})
            result = call_tool(client, params.get("name", ""), params.get("arguments") or {})
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except (FeishuError, ValueError, KeyError) as exc:
        if method == "tools/call":
            return {"jsonrpc": "2.0", "id": request_id, "result": tool_result(str(exc), True)}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(exc)},
        }


def main() -> None:
    client = FeishuClient()
    for raw_line in sys.stdin.buffer:
        if not raw_line.strip():
            continue
        try:
            message = json.loads(raw_line.decode("utf-8"))
            response = dispatch(message, client)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        except Exception as exc:  # Keep the server alive after malformed input.
            error = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(error, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
