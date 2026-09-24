#!/usr/bin/env python3
"""Local, dependency-free storage and media server for the mobile preview tool."""
from __future__ import annotations

import argparse
import copy
import filecmp
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import sys
import tempfile
import threading
import uuid
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parent
STATIC_FILES = {"index.html", "app.js", "style.css", "preview.js", "preview.css"}
MIME_EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "video/mp4": ".mp4"}
ASSET_CATEGORIES = ("main", "aplus")
ID_RE = re.compile(r"^[a-f0-9]{32}$")
FOLDER_NAME_LIMIT = 60
WINDOWS_RESERVED_RE = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.IGNORECASE)
JSON_LIMIT = 5 * 1024 * 1024
IMAGE_LIMIT = 50 * 1024 * 1024
VIDEO_LIMIT = 1024 * 1024 * 1024


class StoreLock:
    """Serialize threads and separately launched servers sharing one data folder."""
    def __init__(self, path: Path):
        self.path = path
        self.thread_lock = threading.RLock()
        self.local = threading.local()

    def __enter__(self):
        self.thread_lock.acquire()
        stream = None
        try:
            depth = getattr(self.local, "depth", 0)
            if not depth:
                stream = self.path.open("a+b")
                stream.seek(0, os.SEEK_END)
                if stream.tell() == 0:
                    stream.write(b"\0")
                    stream.flush()
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                self.local.stream = stream
            self.local.depth = depth + 1
            return self
        except BaseException:
            if stream is not None:
                stream.close()
            self.thread_lock.release()
            raise

    def __exit__(self, *args):
        try:
            self.local.depth -= 1
            if not self.local.depth:
                stream = self.local.stream
                try:
                    stream.seek(0)
                    if os.name == "nt":
                        import msvcrt
                        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
                finally:
                    stream.close()
                    del self.local.stream
        finally:
            self.thread_lock.release()


class APIError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def require_id(value: str) -> str:
    if not ID_RE.fullmatch(value):
        raise APIError(404, "找不到此项目或素材。")
    return value


def project_folder_name(name: str) -> str:
    """Keep a recognizable project title that is also a safe Windows folder name."""
    result = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "", name).strip().rstrip(". ")
    result = result[:FOLDER_NAME_LIMIT].rstrip(". ") or "未命名产品"
    if WINDOWS_RESERVED_RE.match(result) or ID_RE.fullmatch(result):
        result = ("项目 " + result)[:FOLDER_NAME_LIMIT].rstrip(". ")
    return result


def atomic_json(path: Path, value: dict) -> None:
    """Do not replace a good document until the complete new one is on disk."""
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".saving-", suffix=".tmp", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as stream:
            result = json.load(stream)
        if not isinstance(result, dict):
            raise ValueError("Expected object")
        return result
    except FileNotFoundError:
        raise APIError(404, "找不到此项目。") from None
    except (json.JSONDecodeError, UnicodeError, ValueError):
        raise APIError(500, "本地项目文件无法读取。原文件已保留，请检查数据目录。") from None


def text_field(value, label: str, limit: int = 20000) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise APIError(400, f"{label}必须是文本，且不能超过 {limit} 个字符。")
    return value


def finite_number(value, minimum: float, maximum: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and minimum <= value <= maximum


def image_dimensions(path: Path, mime: str) -> tuple[int, int]:
    """Check file structure/signature and obtain image dimensions without packages."""
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(32)
        if mime == "image/png":
            if len(header) < 29 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[8:16] != b"\x00\x00\x00\rIHDR":
                raise APIError(400, "PNG 文件损坏或文件格式不匹配。")
            stream.seek(-12, os.SEEK_END)
            if stream.read(12) != b"\x00\x00\x00\x00IEND\xaeB`\x82":
                raise APIError(400, "PNG 文件不完整，请重新导出。")
            dimensions = struct.unpack(">II", header[16:24])
        elif mime == "image/jpeg":
            if not header.startswith(b"\xff\xd8\xff") or size < 10:
                raise APIError(400, "JPG 文件损坏或文件格式不匹配。")
            stream.seek(-2, os.SEEK_END)
            if stream.read(2) != b"\xff\xd9":
                raise APIError(400, "JPG 文件不完整，请重新导出。")
            stream.seek(2)
            dimensions = None
            sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
            while stream.tell() < size:
                if stream.read(1) != b"\xff":
                    break
                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if not marker or marker[0] in (0xDA, 0xD9):
                    break
                if marker[0] in (0x01, *range(0xD0, 0xD9)):
                    continue
                raw_length = stream.read(2)
                if len(raw_length) != 2:
                    break
                length = int.from_bytes(raw_length, "big")
                if length < 2 or stream.tell() + length - 2 > size:
                    break
                if marker[0] in sof:
                    data = stream.read(5)
                    if len(data) == 5:
                        height, width = struct.unpack(">HH", data[1:])
                        dimensions = (width, height)
                    break
                stream.seek(length - 2, os.SEEK_CUR)
            if dimensions is None:
                raise APIError(400, "无法读取 JPG 尺寸，请重新导出。")
        else:
            if len(header) < 30 or header[:4] != b"RIFF" or header[8:12] != b"WEBP" or int.from_bytes(header[4:8], "little") + 8 != size:
                raise APIError(400, "WebP 文件损坏或文件格式不匹配。")
            kind = header[12:16]
            if kind == b"VP8X":
                dimensions = (1 + int.from_bytes(header[24:27], "little"), 1 + int.from_bytes(header[27:30], "little"))
            elif kind == b"VP8 " and header[23:26] == b"\x9d\x01\x2a":
                dimensions = (int.from_bytes(header[26:28], "little") & 0x3FFF, int.from_bytes(header[28:30], "little") & 0x3FFF)
            elif kind == b"VP8L" and header[20] == 0x2F:
                bits = int.from_bytes(header[21:25], "little")
                dimensions = ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
            else:
                raise APIError(400, "无法读取 WebP 尺寸，请重新导出。")
    if not all(0 < item <= 65535 for item in dimensions):
        raise APIError(400, "图片尺寸无效。")
    return dimensions


def verify_mp4(path: Path) -> None:
    """Require a valid ftyp box and media/movie boxes; decoding stays in browser."""
    size = path.stat().st_size
    seen = set()
    with path.open("rb") as stream:
        while stream.tell() < size:
            start = stream.tell()
            header = stream.read(8)
            if len(header) != 8:
                raise APIError(400, "MP4 文件不完整，请重新导出。")
            length, kind = struct.unpack(">I4s", header)
            minimum = 8
            if length == 1:
                extended = stream.read(8)
                if len(extended) != 8:
                    raise APIError(400, "MP4 文件不完整。")
                length = int.from_bytes(extended, "big")
                minimum = 16
            elif length == 0:
                length = size - start
            if length < minimum or start + length > size:
                raise APIError(400, "MP4 文件损坏或尚未导出完成。")
            if kind == b"ftyp" and length < minimum + 8:
                raise APIError(400, "MP4 文件格式无效。")
            seen.add(kind)
            stream.seek(start + length)
    if not {b"ftyp", b"moov", b"mdat"}.issubset(seen):
        raise APIError(400, "文件不是完整的 MP4 视频，请重新导出。")


class ProjectStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = StoreLock(self.root / ".preview.lock")

    def check_directory(self, directory: Path) -> Path:
        """Accept only an immediate, contained project directory and its own files."""
        if (directory.parent != self.root or directory.is_symlink()
                or directory.resolve().parent != self.root
                or (hasattr(directory, "is_junction") and directory.is_junction())):
            raise APIError(404, "找不到此项目。")
        for path in (directory / "assets", directory / "project.json", directory / "assets" / "catalog.json"):
            if (path.is_symlink() or not path.resolve().is_relative_to(directory.resolve())
                    or (hasattr(path, "is_junction") and path.is_junction())):
                raise APIError(404, "找不到此项目。")
        return directory

    def project_record(self, directory: Path) -> dict:
        self.check_directory(directory)
        project = read_json(directory / "project.json")
        project_id = project.get("id")
        if not isinstance(project_id, str) or not ID_RE.fullmatch(project_id):
            raise APIError(500, "本地项目 ID 无效，原文件已保留，请检查数据目录。")
        if ID_RE.fullmatch(directory.name) and directory.name != project_id:
            raise APIError(500, "旧项目目录与项目 ID 不一致，原文件已保留，请检查数据目录。")
        return project

    def project_entries(self):
        for entry in self.root.iterdir():
            if entry.is_dir() and ((entry / "project.json").exists() or ID_RE.fullmatch(entry.name)):
                yield entry

    def directory(self, project_id: str) -> Path:
        """Resolve stable API IDs through metadata, independently of folder names."""
        require_id(project_id)
        with self.lock:
            matches = []
            for entry in self.project_entries():
                try:
                    project = self.project_record(entry)
                except APIError:
                    if entry.name == project_id:
                        raise
                    continue
                if project["id"] == project_id:
                    matches.append(entry)
            if len(matches) > 1:
                raise APIError(500, "发现重复项目 ID，原文件已保留，请检查数据目录中的重复项目文件夹。")
            if not matches:
                raise APIError(404, "找不到此项目。")
            return matches[0]

    def available_directory(self, name: str) -> Path:
        base = project_folder_name(name)
        occupied = {entry.name.casefold() for entry in self.root.iterdir()}
        number = 1
        candidate = base
        while candidate.casefold() in occupied:
            number += 1
            suffix = f" ({number})"
            candidate = base[:FOLDER_NAME_LIMIT - len(suffix)].rstrip(". ") + suffix
        return self.check_directory(self.root / candidate)

    def migrate_project_folders(self) -> dict:
        """Rename old UUID folders atomically; project IDs and file bytes stay intact."""
        report = {"migrated": 0, "errors": []}
        with self.lock:
            for entry in list(self.project_entries()):
                if not ID_RE.fullmatch(entry.name):
                    continue
                try:
                    project = self.project_record(entry)
                    # Resolve again to reject duplicate IDs before moving either copy.
                    source = self.directory(project["id"])
                    destination = self.available_directory(text_field(project.get("name"), "项目名称", 180))
                    # Verify the final absolute paths immediately before the rename.
                    if (source.resolve().parent != self.root or destination.resolve().parent != self.root
                            or destination.exists() or destination.is_symlink()):
                        raise APIError(500, "项目目录整理目标无效或已存在，原目录已保留。")
                    source.rename(destination)
                    report["migrated"] += 1
                except (APIError, OSError, RuntimeError) as error:
                    report["errors"].append({"projectId": entry.name, "error": str(error)})
        return report

    def catalog(self, directory: Path) -> dict:
        path = directory / "assets" / "catalog.json"
        return read_json(path) if path.exists() else {}

    def asset_directory(self, directory: Path, category: str, create: bool = False) -> Path:
        if category not in ASSET_CATEGORIES:
            raise APIError(400, "素材分类必须是 main 或 aplus。")
        assets = directory / "assets"
        target = assets / category
        if target.is_symlink() or not target.resolve().is_relative_to(assets.resolve()):
            raise APIError(404, "素材目录无效。")
        if create:
            target.mkdir(exist_ok=True)
        return target

    def asset_path(self, directory: Path, asset_id: str, metadata: dict) -> Path:
        filename = require_id(asset_id) + MIME_EXTENSIONS[metadata["mime"]]
        assets = directory / "assets"
        candidates = []
        if metadata.get("category") is not None:
            candidates.append(self.asset_directory(directory, metadata["category"]) / filename)
        # Unclassified files from earlier versions remain readable by the same URL.
        candidates.append(assets / filename)
        for path in candidates:
            if path.is_symlink() or not path.resolve().is_relative_to(assets.resolve()):
                raise APIError(404, "素材文件路径无效。")
            if path.is_file():
                return path
        raise APIError(404, "素材文件缺失，请重新导入。")

    def migrate_assets(self) -> dict:
        """Organize referenced legacy media without changing IDs or project revisions.

        A complete copy and catalog update precede removal of each old copy. An
        interrupted run leaves the original or the catalog's new file intact and
        can be retried. Unreferenced legacy media stays in its original location.
        """
        report = {"migrated": 0, "unassigned": 0, "errors": []}
        with self.lock:
            for entry in self.project_entries():
                project_id = entry.name
                try:
                    project = self.project_record(entry)
                    project_id = project["id"]
                    directory = self.directory(project_id)
                    catalog = self.catalog(directory)
                    uses = {category: set() for category in ASSET_CATEGORIES}
                    for item in project.get("gallery", []):
                        uses["main"].add(item.get("assetId"))
                    for module in project.get("modules", []):
                        for key in ("assetId", "videoAssetId", "posterAssetId", "backgroundAssetId", "logoAssetId"):
                            uses["aplus"].add(module.get(key))
                        for slide in module.get("slides", []):
                            uses["aplus"].add(slide.get("assetId"))
                    pending = []
                    changed = False
                    for asset_id, metadata in catalog.items():
                        filename = require_id(asset_id) + MIME_EXTENSIONS[metadata["mime"]]
                        legacy = directory / "assets" / filename
                        if legacy.is_symlink() or not legacy.resolve().is_relative_to(directory.resolve()):
                            raise APIError(404, "素材文件路径无效。")
                        if not legacy.is_file():
                            continue
                        categories = [category for category in ASSET_CATEGORIES if asset_id in uses[category]]
                        if metadata.get("category") in ASSET_CATEGORIES:
                            categories = list(dict.fromkeys([metadata["category"], *categories]))
                        if not categories:
                            report["unassigned"] += 1
                            continue
                        for category in categories:
                            destination = self.asset_directory(directory, category, create=True) / filename
                            if destination.is_symlink():
                                raise APIError(404, "素材文件路径无效。")
                            if destination.exists():
                                if not destination.is_file() or not filecmp.cmp(legacy, destination, shallow=False):
                                    raise APIError(500, "素材整理目标已存在不同文件，原文件已保留。")
                            else:
                                temporary = None
                                try:
                                    with tempfile.NamedTemporaryFile(prefix=".migrating-", suffix=".tmp", dir=destination.parent, delete=False) as stream:
                                        temporary = Path(stream.name)
                                        with legacy.open("rb") as source:
                                            shutil.copyfileobj(source, stream)
                                        stream.flush()
                                        os.fsync(stream.fileno())
                                    os.replace(temporary, destination)
                                finally:
                                    if temporary is not None:
                                        temporary.unlink(missing_ok=True)
                        metadata["category"] = categories[0]
                        changed = True
                        pending.append(legacy)
                    if changed:
                        atomic_json(directory / "assets" / "catalog.json", catalog)
                        for legacy in pending:
                            legacy.unlink()
                            report["migrated"] += 1
                except (APIError, OSError, KeyError, TypeError, AttributeError) as error:
                    report["errors"].append({"projectId": project_id, "error": str(error)})
        return report

    def list(self) -> list[dict]:
        with self.lock:
            projects = []
            seen = set()
            for directory in self.project_entries():
                try:
                    project = self.project_record(directory)
                    item = {"id": project["id"], "name": project["name"], "updatedAt": project["updatedAt"]}
                except (APIError, KeyError):
                    continue
                if project["id"] in seen:
                    raise APIError(500, "发现重复项目 ID，原文件已保留，请检查数据目录中的重复项目文件夹。")
                seen.add(project["id"])
                projects.append(item)
            return sorted(projects, key=lambda item: item["updatedAt"], reverse=True)

    def create(self, name: str) -> dict:
        name = text_field(name, "项目名称", 180).strip() or "未命名产品"
        with self.lock:
            project_id = uuid.uuid4().hex
            timestamp = now()
            project = {
                "schemaVersion": 1, "id": project_id, "name": name, "revision": 0,
                "createdAt": timestamp, "updatedAt": timestamp,
                "product": {"brand": "", "title": "", "price": ""},
                "gallery": [], "modules": [], "assets": {},
                "settings": {"viewport": "390x844", "zoom": "fit", "shell": True, "editorCollapsed": False},
                "view": {"galleryIndex": 0, "carouselIndices": {}, "scrollTop": 0},
            }
            directory = self.available_directory(name)
            directory.mkdir()
            try:
                (directory / "assets").mkdir()
                for category in ASSET_CATEGORIES:
                    self.asset_directory(directory, category, create=True)
                atomic_json(directory / "project.json", project)
            except OSError:
                for category in ASSET_CATEGORIES:
                    category_directory = directory / "assets" / category
                    if category_directory.exists():
                        category_directory.rmdir()
                (directory / "assets").rmdir()
                directory.rmdir()
                raise
            return project

    def get(self, project_id: str) -> dict:
        with self.lock:
            directory = self.directory(project_id)
            project = read_json(directory / "project.json")
            project["assets"] = self.catalog(directory)
            return project

    def validate(self, incoming: dict, current: dict, catalog: dict) -> dict:
        if incoming.get("id") != current["id"] or incoming.get("schemaVersion") != 1:
            raise APIError(400, "项目 ID 或版本不匹配。")
        revision = incoming.get("revision")
        if type(revision) is not int or revision != current["revision"]:
            raise APIError(409, "项目已在另一个窗口更新。当前修改仍在浏览器中，请先保留修改，再重新加载项目。")
        result = copy.deepcopy(incoming)
        result["name"] = text_field(incoming.get("name"), "项目名称", 180).strip() or "未命名产品"
        product = incoming.get("product")
        if not isinstance(product, dict):
            raise APIError(400, "商品信息格式无效。")
        result["product"] = {key: text_field(product.get(key, ""), "商品信息") for key in ("brand", "title", "price")}
        all_ids = set()

        def item_id(item):
            value = item.get("id")
            if not isinstance(value, str) or not value or len(value) > 100 or value in all_ids:
                raise APIError(400, "模块或图片槽 ID 缺失或重复。")
            all_ids.add(value)

        def asset_ref(item, key, mime_prefix):
            value = item.get(key, "")
            if value in ("", None):
                return
            if not isinstance(value, str) or value not in catalog or not catalog[value]["mime"].startswith(mime_prefix):
                raise APIError(400, "引用的素材不存在或格式不匹配，请重新导入。")

        gallery = result.get("gallery")
        if not isinstance(gallery, list) or len(gallery) > 2000:
            raise APIError(400, "主副图列表无效或过长。")
        for item in gallery:
            if not isinstance(item, dict):
                raise APIError(400, "图片槽格式无效。")
            item_id(item)
            asset_ref(item, "assetId", "image/")
        modules = result.get("modules")
        if not isinstance(modules, list) or len(modules) > 200:
            raise APIError(400, "A+ 模块列表无效或过长。")
        for module in modules:
            if not isinstance(module, dict) or module.get("type") not in ("image", "carousel", "video", "brand-story"):
                raise APIError(400, "不支持的 A+ 模块。")
            item_id(module)
            for key in ("title", "body"):
                text_field(module.get(key, ""), "模块文字")
            if module["type"] == "image":
                asset_ref(module, "assetId", "image/")
            elif module["type"] == "video":
                asset_ref(module, "videoAssetId", "video/")
                asset_ref(module, "posterAssetId", "image/")
            else:
                if module["type"] == "brand-story":
                    text_field(module.get("brandName", ""), "品牌名称")
                    asset_ref(module, "backgroundAssetId", "image/")
                    asset_ref(module, "logoAssetId", "image/")
                slides = module.get("slides", [])
                if not isinstance(slides, list) or len(slides) > 200:
                    raise APIError(400, "轮播项列表无效或过长。")
                for slide in slides:
                    if not isinstance(slide, dict):
                        raise APIError(400, "轮播项格式无效。")
                    item_id(slide)
                    asset_ref(slide, "assetId", "image/")
                    for key in ("label", "title", "body"):
                        text_field(slide.get(key, ""), "轮播文字")
        settings = result.get("settings")
        if not isinstance(settings, dict) or settings.get("viewport") not in ("360x780", "390x844", "430x932"):
            raise APIError(400, "手机视口设置无效。")
        if settings.get("zoom") != "fit" and not finite_number(settings.get("zoom"), 0.1, 3):
            raise APIError(400, "显示缩放必须是适应窗口或 10%–300%。")
        if any(type(settings.get(key)) is not bool for key in ("shell", "editorCollapsed")):
            raise APIError(400, "预览设置无效。")
        view = result.get("view")
        if not isinstance(view, dict) or not finite_number(view.get("galleryIndex"), 0, 100000) or not finite_number(view.get("scrollTop"), 0, 100000000):
            raise APIError(400, "预览位置格式无效。")
        indices = view.get("carouselIndices")
        if not isinstance(indices, dict) or len(indices) > 200 or any(not finite_number(value, 0, 100000) for value in indices.values()):
            raise APIError(400, "轮播预览位置无效。")
        result.update({"createdAt": current["createdAt"], "updatedAt": now(), "revision": current["revision"] + 1, "assets": catalog})
        return result

    def save(self, project_id: str, incoming: dict) -> dict:
        with self.lock:
            directory = self.directory(project_id)
            current = read_json(directory / "project.json")
            result = self.validate(incoming, current, self.catalog(directory))
            # Asset metadata has one independent source of truth.
            stored = {**result, "assets": {}}
            atomic_json(directory / "project.json", stored)
            return result

    def import_asset(self, project_id: str, temporary: Path, name: str, mime: str, properties: dict, category: str = "main") -> dict:
        if category not in ASSET_CATEGORIES:
            raise APIError(400, "素材分类必须是 main 或 aplus。")
        if mime.startswith("image/"):
            width, height = image_dimensions(temporary, mime)
        else:
            verify_mp4(temporary)
            width, height = properties.get("width", 0), properties.get("height", 0)
        metadata = {"id": uuid.uuid4().hex, "name": name, "mime": mime, "size": temporary.stat().st_size, "width": width, "height": height, "category": category}
        if mime == "video/mp4" and "duration" in properties:
            metadata["duration"] = properties["duration"]
        with self.lock:
            directory = self.directory(project_id)
            read_json(directory / "project.json")
            catalog = self.catalog(directory)
            destination = self.asset_directory(directory, category, create=True) / (metadata["id"] + MIME_EXTENSIONS[mime])
            catalog[metadata["id"]] = metadata
            os.replace(temporary, destination)
            try:
                atomic_json(directory / "assets" / "catalog.json", catalog)
            except OSError:
                destination.unlink(missing_ok=True)
                raise
            return metadata

    def asset(self, project_id: str, asset_id: str) -> tuple[Path, dict]:
        with self.lock:
            directory = self.directory(project_id)
            metadata = self.catalog(directory).get(require_id(asset_id))
            if metadata is None:
                raise APIError(404, "找不到此素材。")
            return self.asset_path(directory, asset_id, metadata), metadata


class PreviewServer(ThreadingHTTPServer):
    daemon_threads = True
    # SO_REUSEADDR lets a second Windows process silently steal a live port.
    allow_reuse_address = os.name != "nt"

    def __init__(self, address: tuple[str, int], store: ProjectStore):
        self.store = store
        super().__init__(address, PreviewHandler)

    def server_bind(self):
        if os.name == "nt" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class PreviewHandler(BaseHTTPRequestHandler):
    server_version = "CanvaMobilePreview/0.1"
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Avoid logging user-controlled names and document data.
        if len(args) >= 2 and str(args[1]).startswith("5"):
            print("[preview] Request failed:", args[1], file=sys.stderr)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def send_json(self, status: int, value: dict):
        content = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(content)

    def guard(self):
        port = self.server.server_address[1]
        allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if port == 80:
            allowed_hosts |= {"127.0.0.1", "localhost"}
        if self.headers.get("Host", "").lower() not in allowed_hosts:
            raise APIError(403, "仅允许通过本机地址访问预览工具。")
        origin = self.headers.get("Origin")
        if origin is not None and origin.lower() not in {"http://" + host for host in allowed_hosts}:
            raise APIError(403, "请在预览工具窗口中执行此操作。")
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            raise APIError(403, "不允许其他网站访问本地项目。")

    def body_size(self, limit: int) -> int:
        if self.headers.get("Transfer-Encoding"):
            raise APIError(400, "不支持此上传方式。")
        try:
            size = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            raise APIError(400, "文件长度无效。") from None
        if size < 0:
            raise APIError(411, "请求缺少文件长度。")
        if size > limit:
            raise APIError(413, f"文件太大，本次上限为 {limit // (1024 * 1024)} MB。")
        return size

    def read_body_json(self) -> dict:
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
            raise APIError(415, "请使用 JSON 格式保存项目。")
        size = self.body_size(JSON_LIMIT)
        body = self.rfile.read(size)
        if len(body) != size:
            raise APIError(400, "请求未接收完整，请重试。")
        try:
            result = json.loads(body, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (ValueError, UnicodeError):
            raise APIError(400, "项目数据格式无效。") from None
        if not isinstance(result, dict):
            raise APIError(400, "项目数据必须是对象。")
        return result

    def upload(self, project_id: str, query: dict):
        store = self.server.store
        store.get(project_id)
        mime = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if mime not in MIME_EXTENSIONS:
            raise APIError(415, "支持 PNG、JPG、WebP 图片和 MP4 视频。")
        size = self.body_size(VIDEO_LIMIT if mime == "video/mp4" else IMAGE_LIMIT)
        if size == 0:
            raise APIError(400, "文件为空，请重新选择。")
        name = text_field(query.get("name", ["素材" + MIME_EXTENSIONS[mime]])[0], "素材名称", 255)
        # Names are display-only; no user-provided filename becomes a disk path.
        name = name.replace("\\", "/").split("/")[-1] or "素材" + MIME_EXTENSIONS[mime]
        category = query.get("category", ["main"])[0]
        if category not in ASSET_CATEGORIES:
            raise APIError(400, "素材分类必须是 main 或 aplus。")
        properties = {}
        for key in ("width", "height", "duration"):
            if key in query:
                try:
                    value = float(query[key][0])
                except ValueError:
                    raise APIError(400, "素材尺寸或时长无效。") from None
                if not finite_number(value, 0, 10000000 if key == "duration" else 65535):
                    raise APIError(400, "素材尺寸或时长无效。")
                properties[key] = value if key == "duration" else int(value)
        directory = store.directory(project_id) / "assets"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(prefix=".upload-", suffix=".tmp", dir=directory, delete=False) as stream:
                temporary = Path(stream.name)
                remaining = size
                while remaining:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise APIError(400, "上传中断，请重试。")
                    stream.write(chunk)
                    remaining -= len(chunk)
                stream.flush()
                os.fsync(stream.fileno())
            metadata = store.import_asset(project_id, temporary, name, mime, properties, category)
            self.send_json(201, metadata)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def send_file(self, path: Path, mime: str, immutable: bool = False):
        size = path.stat().st_size
        first, last, status = 0, size - 1, 200
        range_header = self.headers.get("Range") if immutable else None
        if range_header:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
            valid = bool(match and (match[1] or match[2]) and size > 0)
            if valid:
                if match[1]:
                    first = int(match[1])
                    last = min(int(match[2]), size - 1) if match[2] else size - 1
                else:
                    suffix = int(match[2])
                    first, last = max(0, size - suffix), size - 1
                    valid = suffix > 0
                valid = valid and 0 <= first <= last < size
            if not valid:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                return
            status = 206
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(last - first + 1))
        self.send_header("Cache-Control", "private, max-age=31536000, immutable" if immutable else "no-store")
        if immutable:
            self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {first}-{last}/{size}")
        self.end_headers()
        if self.command == "HEAD":
            return
        with path.open("rb") as stream:
            stream.seek(first)
            remaining = last - first + 1
            while remaining:
                chunk = stream.read(min(256 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def handle_request(self):
        try:
            self.guard()
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            parts = path.strip("/").split("/")
            store = self.server.store
            read_method = self.command in ("GET", "HEAD")
            if path == "/api/projects":
                if read_method:
                    self.send_json(200, {"projects": store.list()})
                elif self.command == "POST":
                    self.send_json(201, store.create(self.read_body_json().get("name", "未命名产品")))
                else:
                    raise APIError(405, "不支持此操作。")
            elif len(parts) >= 3 and parts[:2] == ["api", "projects"]:
                project_id = require_id(parts[2])
                if len(parts) == 3 and read_method:
                    self.send_json(200, store.get(project_id))
                elif len(parts) == 3 and self.command == "PUT":
                    self.send_json(200, store.save(project_id, self.read_body_json()))
                elif len(parts) == 4 and parts[3] == "assets" and self.command == "POST":
                    self.upload(project_id, parse_qs(parsed.query))
                elif len(parts) == 5 and parts[3] == "assets" and read_method:
                    asset, metadata = store.asset(project_id, parts[4])
                    self.send_file(asset, metadata["mime"], immutable=True)
                else:
                    raise APIError(404, "找不到此接口。")
            elif read_method and (path == "/" or path.lstrip("/") in STATIC_FILES):
                filename = "index.html" if path == "/" else path.lstrip("/")
                target = ROOT / filename
                if not target.is_file() or target.is_symlink():
                    raise APIError(404, "工具页面文件缺失，请检查安装目录。")
                mime = {".js": "text/javascript", ".css": "text/css", ".html": "text/html"}.get(target.suffix, "application/octet-stream")
                self.send_file(target, mime + "; charset=utf-8")
            else:
                raise APIError(404, "找不到此页面。")
        except APIError as error:
            self.close_connection = True
            self.send_json(error.status, {"error": error.message})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True
        except OSError:
            self.close_connection = True
            self.send_json(500, {"error": "本地文件读写失败。原项目已保留，请检查磁盘空间或文件权限后重试。"})
        except Exception as error:
            self.close_connection = True
            print(f"[preview] {type(error).__name__}", file=sys.stderr)
            self.send_json(500, {"error": "操作未完成，已保留原项目，请重试。"})

    do_GET = handle_request
    do_HEAD = handle_request
    do_POST = handle_request
    do_PUT = handle_request
    do_OPTIONS = handle_request
    do_DELETE = handle_request


def make_server(store: ProjectStore, port: int, auto_port: bool = True) -> PreviewServer:
    candidates = [port] if not auto_port or port == 0 else range(port, min(port + 30, 65536))
    last_error = None
    for candidate in candidates:
        try:
            return PreviewServer(("127.0.0.1", candidate), store)
        except OSError as error:
            if error.errno not in (48, 98, 10048) and getattr(error, "winerror", None) != 10048:
                raise
            last_error = error
    raise last_error or OSError("No available local port")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Canva → 亚马逊手机预览工具（仅本机访问）")
    parser.add_argument("--port", type=int, default=None, help="指定本机端口；默认从 8877 自动选择可用端口")
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data", help="项目数据目录")
    parser.add_argument("--migrate-project-folders", action="store_true", help="将旧项目的随机编号文件夹改为项目名称后退出；项目 ID 和素材地址保持不变")
    parser.add_argument("--migrate-assets", action="store_true", help="按主图 / A+ 整理已引用的旧素材后退出；未引用的旧素材保留原位置")
    args = parser.parse_args()
    if args.port is not None and not 0 <= args.port <= 65535:
        parser.error("端口必须介于 0 和 65535 之间。")
    store = ProjectStore(args.data_dir)
    folder_migration = store.migrate_project_folders()
    if args.migrate_project_folders:
        print(json.dumps(folder_migration, ensure_ascii=False, indent=2))
        return 1 if folder_migration["errors"] else 0
    if folder_migration["errors"]:
        print("部分旧项目目录暂未改名，原目录已保留。可使用 --migrate-project-folders 查看详情。", file=sys.stderr)
    migration = store.migrate_assets()
    if args.migrate_assets:
        print(json.dumps(migration, ensure_ascii=False, indent=2))
        return 1 if migration["errors"] else 0
    if migration["errors"]:
        print("部分旧素材暂未整理，原文件已保留。可使用 --migrate-assets 查看详情。", file=sys.stderr)
    try:
        server = make_server(store, args.port if args.port is not None else 8877, auto_port=args.port is None)
    except OSError:
        parser.exit(1, "无法启动本地服务，请关闭占用端口的程序，或使用 --port 选择其他端口。\n")
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"\nCanva → 亚马逊手机预览\n\n打开地址：{url}\n数据目录：{store.root}\n\n保留此窗口以继续使用。按 Ctrl+C 停止。\n", flush=True)
    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n预览服务已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    sys.exit(main())
