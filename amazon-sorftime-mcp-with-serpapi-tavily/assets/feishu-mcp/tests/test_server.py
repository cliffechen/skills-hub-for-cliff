import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server import (  # noqa: E402
    FeishuClient,
    extract_document_id,
    markdown_to_blocks,
    parse_bitable_reference,
)


class FeishuMcpTests(unittest.TestCase):
    def test_extract_document_id_from_url(self):
        self.assertEqual(
            extract_document_id("https://example.feishu.cn/docx/doxcn1234567890AbCdEfGhIjKl?from=from_copylink"),
            "doxcn1234567890AbCdEfGhIjKl",
        )

    def test_reject_wiki_url_with_actionable_message(self):
        with self.assertRaisesRegex(ValueError, "原始文档"):
            extract_document_id("https://example.feishu.cn/wiki/wikcn123456789")

    def test_markdown_to_blocks(self):
        blocks = markdown_to_blocks("# 标题\n正文\n- 要点\n1. 步骤")
        self.assertEqual([item["block_type"] for item in blocks], [3, 2, 12, 13])
        self.assertEqual(blocks[0]["heading1"]["elements"][0]["text_run"]["content"], "标题")

    def test_parse_base_bitable_url(self):
        parsed = parse_bitable_reference(
            "https://example.feishu.cn/base/bascnExampleToken?table=tblExample123&view=vew1"
        )
        self.assertEqual(parsed["source_type"], "base")
        self.assertEqual(parsed["app_token"], "bascnExampleToken")
        self.assertEqual(parsed["table_id"], "tblExample123")

    def test_parse_wiki_bitable_url(self):
        parsed = parse_bitable_reference(
            "https://example.feishu.cn/wiki/wikcnExampleToken?table=tblExample123"
        )
        self.assertEqual(parsed["source_type"], "wiki")
        self.assertEqual(parsed["wiki_token"], "wikcnExampleToken")
        self.assertEqual(parsed["table_id"], "tblExample123")

    def test_reject_non_bitable_url(self):
        with self.assertRaisesRegex(ValueError, "多维表格"):
            parse_bitable_reference("https://example.feishu.cn/docx/doxcn123456789")

    def test_append_record_validates_schema_and_calls_create(self):
        class FakeClient(FeishuClient):
            def __init__(self):
                pass

            def resolve_bitable(self, bitable, table_id=""):
                return {
                    "app_token": "bascnExampleToken",
                    "table_id": "tblExample123",
                    "source_type": "base",
                    "tables": [],
                }

            def list_bitable_fields(self, app_token, table_id):
                return [
                    {"field_name": "关键词", "field_id": "fld1", "type": 1},
                    {"field_name": "决策", "field_id": "fld2", "type": 1},
                ]

            def _request_json(self, method, path, body=None, authenticated=True):
                self.last_request = (method, path, body)
                return {
                    "data": {
                        "record": {
                            "record_id": "recExample",
                            "fields": body["fields"],
                        }
                    }
                }

        client = FakeClient()
        result = client.append_bitable_record(
            "bascnExampleToken", {"关键词": "algae calcium", "决策": "VERIFY"}
        )
        self.assertEqual(result["record_id"], "recExample")
        self.assertEqual(client.last_request[0], "POST")
        self.assertIn("/records", client.last_request[1])

    def test_append_record_rejects_unknown_field(self):
        class FakeClient(FeishuClient):
            def __init__(self):
                pass

            def resolve_bitable(self, bitable, table_id=""):
                return {
                    "app_token": "bascnExampleToken",
                    "table_id": "tblExample123",
                    "source_type": "base",
                    "tables": [],
                }

            def list_bitable_fields(self, app_token, table_id):
                return [{"field_name": "关键词", "field_id": "fld1", "type": 1}]

        with self.assertRaisesRegex(ValueError, "不存在"):
            FakeClient().append_bitable_record(
                "bascnExampleToken", {"并不存在的列": "value"}
            )

    def test_append_record_uploads_attachment_field(self):
        class FakeClient(FeishuClient):
            def __init__(self):
                pass

            def resolve_bitable(self, bitable, table_id=""):
                return {
                    "app_token": "bascnExampleToken",
                    "table_id": "tblExample123",
                    "source_type": "base",
                    "tables": [],
                }

            def list_bitable_fields(self, app_token, table_id):
                return [
                    {"field_name": "关键词", "field_id": "fld1", "type": 1},
                    {"field_name": "HTML报告", "field_id": "fld2", "type": 17},
                ]

            def _upload_media(self, parent_node, file_path):
                self.upload_request = (parent_node, file_path)
                return "boxExampleToken"

            def _request_json(self, method, path, body=None, authenticated=True):
                self.last_request = (method, path, body)
                return {"data": {"record": {"record_id": "recExample"}}}

        client = FakeClient()
        result = client.append_bitable_record(
            "bascnExampleToken",
            {"关键词": "algae calcium"},
            attachments={"HTML报告": "report.html"},
        )
        self.assertEqual(client.upload_request[1], "report.html")
        self.assertEqual(
            client.last_request[2]["fields"]["HTML报告"],
            [{"file_token": "boxExampleToken"}],
        )
        self.assertEqual(result["uploaded_attachment_fields"], ["HTML报告"])

    def test_stdio_initialize_list_and_unconfigured_check(self):
        env = os.environ.copy()
        for key in ("FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_USER_ACCESS_TOKEN"):
            env.pop(key, None)
        env["FEISHU_SKIP_DOTENV"] = "1"
        requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {}},
            },
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "feishu_connection_check", "arguments": {}},
            },
        ]
        process = subprocess.run(
            [sys.executable, str(ROOT / "server.py")],
            input="".join(json.dumps(item) + "\n" for item in requests),
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            check=True,
        )
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "feishu-docs-bitable")
        self.assertEqual(len(responses[1]["result"]["tools"]), 7)
        check_payload = json.loads(responses[2]["result"]["content"][0]["text"])
        self.assertFalse(check_payload["configured"])


if __name__ == "__main__":
    unittest.main()
