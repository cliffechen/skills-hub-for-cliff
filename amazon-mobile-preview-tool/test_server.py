"""Run with: python -m unittest discover -s . -p test_server.py -v"""
import concurrent.futures
import copy
import http.client
import json
from pathlib import Path
import shutil
import struct
import tempfile
import threading
import unittest
from unittest import mock
import zlib

import server


def png(width=4, height=3):
    def chunk(kind, content):
        return struct.pack(">I", len(content)) + kind + content + struct.pack(">I", zlib.crc32(kind + content) & 0xFFFFFFFF)
    pixels = (b"\0" + b"\x80\xa0\xc0" * width) * height
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


def mp4():
    # Structurally valid boxes for byte-range tests, not a playable fixture.
    def box(kind, data):
        return struct.pack(">I", len(data) + 8) + kind + data
    return box(b"ftyp", b"isom\0\0\0\0isom") + box(b"mdat", b"0123456789" * 16) + box(b"moov", b"")


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="preview-tests-")
        self.store = server.ProjectStore(Path(self.temporary.name))
        self.server = server.make_server(self.store, 0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary.cleanup()

    def request(self, method, path, body=None, headers=None):
        headers = dict(headers or {})
        if isinstance(body, dict):
            body = json.dumps(body).encode()
            headers.setdefault("Content-Type", "application/json")
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request(method, path, body, headers)
            response = connection.getresponse()
            raw = response.read()
            result = json.loads(raw) if raw and "application/json" in response.getheader("Content-Type", "") else raw
            return response.status, dict(response.getheaders()), result
        finally:
            connection.close()

    def create(self, name="草稿产品"):
        status, _, project = self.request("POST", "/api/projects", {"name": name})
        self.assertEqual(status, 201)
        return project

    def upload(self, project, data=None, mime="image/png", name="same.png", category=None):
        category_query = "" if category is None else f"&category={category}"
        return self.request("POST", f"/api/projects/{project['id']}/assets?name={name}&width=4&height=3&duration=5{category_query}", data if data is not None else png(), {"Content-Type": mime})

    def make_legacy(self, project, *assets):
        directory = self.store.directory(project["id"]) / "assets"
        catalog = self.store.catalog(directory.parent)
        for asset in assets:
            filename = asset["id"] + server.MIME_EXTENSIONS[asset["mime"]]
            (directory / asset["category"] / filename).rename(directory / filename)
            catalog[asset["id"]].pop("category")
        server.atomic_json(directory / "catalog.json", catalog)
        return directory

    def test_create_and_persist_empty_draft(self):
        project = self.create()
        self.assertEqual(project["schemaVersion"], 1)
        self.assertEqual(project["revision"], 0)
        self.assertEqual(project["modules"], [])
        self.assertEqual(project["settings"]["viewport"], "390x844")
        project["modules"] = [
            {"id": "empty-image", "type": "image", "assetId": "", "title": "半成品", "body": ""},
            {"id": "empty-carousel", "type": "carousel", "slides": []},
            {"id": "empty-brand", "type": "brand-story", "title": "", "body": "", "brandName": "", "backgroundAssetId": "", "logoAssetId": "", "slides": []},
        ]
        status, _, saved = self.request("PUT", f"/api/projects/{project['id']}", project)
        self.assertEqual(status, 200)
        self.assertEqual(saved["revision"], 1)
        reopened = server.ProjectStore(Path(self.temporary.name)).get(project["id"])
        self.assertEqual(reopened, saved)
        status, _, listing = self.request("GET", "/api/projects")
        self.assertEqual(status, 200)
        self.assertEqual(listing["projects"][0]["name"], "草稿产品")

    def test_brand_story_round_trip_preserves_existing_product_and_modules(self):
        project = self.create()
        main = self.upload(project, category="main")[2]
        background, logo, card = [self.upload(project, category="aplus")[2] for _ in range(3)]
        video = self.upload(project, mp4(), "video/mp4", category="aplus")[2]
        project["product"] = {"brand": "原商品品牌", "title": "原商品标题", "price": "$19.99"}
        project["gallery"] = [{"id": "main-slot", "assetId": main["id"]}]
        project["modules"] = [
            {"id": "image", "type": "image", "assetId": card["id"], "title": "原单图", "body": "原说明"},
            {"id": "carousel", "type": "carousel", "slides": [{"id": "original-slide", "assetId": card["id"], "label": "原标签"}]},
            {"id": "video", "type": "video", "videoAssetId": video["id"], "posterAssetId": card["id"]},
        ]
        original = self.store.save(project["id"], project)
        project = copy.deepcopy(original)
        brand_story = {
            "id": "brand-story", "type": "brand-story", "title": "From the brand", "body": "品牌介绍",
            "brandName": "OLENPHOGY", "backgroundAssetId": background["id"], "logoAssetId": logo["id"],
            "slides": [
                {"id": "brand-mission", "assetId": card["id"], "label": "Our Mission", "title": "Our Mission", "body": "Something that works."},
                {"id": "brand-draft", "assetId": "", "label": "", "title": "下一张草稿", "body": ""},
            ],
        }
        project["modules"].append(brand_story)
        project["view"]["carouselIndices"][brand_story["id"]] = 1
        status, _, saved = self.request("PUT", f"/api/projects/{project['id']}", project)
        self.assertEqual(status, 200)
        reopened = server.ProjectStore(Path(self.temporary.name)).get(project["id"])
        self.assertEqual(reopened, saved)
        self.assertEqual(reopened["modules"][-1], brand_story)
        self.assertEqual(reopened["modules"][:-1], original["modules"])
        for key in ("product", "gallery", "assets", "settings", "createdAt"):
            self.assertEqual(reopened[key], original[key])
        self.assertEqual(reopened["view"]["carouselIndices"][brand_story["id"]], 1)
        for asset in (background, logo, card):
            self.assertEqual(self.store.asset(project["id"], asset["id"])[0].parent.name, "aplus")

    def test_brand_story_rejects_missing_or_non_image_assets_without_changing_project(self):
        project = self.create()
        video = self.upload(project, mp4(), "video/mp4", category="aplus")[2]
        original = self.store.get(project["id"])
        for field in ("backgroundAssetId", "logoAssetId", "slide"):
            for asset_id in ("a" * 32, video["id"]):
                with self.subTest(field=field, asset_id=asset_id):
                    module = {"id": "brand-story", "type": "brand-story", "brandName": "Example", "slides": []}
                    if field == "slide":
                        module["slides"] = [{"id": "brand-card", "assetId": asset_id}]
                    else:
                        module[field] = asset_id
                    project["modules"] = [module]
                    self.assertEqual(self.request("PUT", f"/api/projects/{project['id']}", project)[0], 400)
                    self.assertEqual(self.store.get(project["id"]), original)

    def test_brand_story_rejects_invalid_text_slides_and_duplicate_ids(self):
        project = self.create()
        project["gallery"] = [{"id": "main-slot", "assetId": ""}]
        invalid_fields = [
            {"brandName": 42}, {"brandName": "a" * 20001}, {"slides": {}}, {"slides": [None]},
            {"slides": [{"id": "card", "title": []}]},
            {"slides": [{"id": "card", "label": False}]},
            {"slides": [{"id": "card", "body": 42}]},
            {"slides": [{"assetId": ""}]},
            {"slides": [{"id": "card"}, {"id": "card"}]},
            {"slides": [{"id": "brand-story"}]},
            {"slides": [{"id": "main-slot"}]},
        ]
        for fields in invalid_fields:
            with self.subTest(fields=repr(fields)[:120]):
                project["modules"] = [{"id": "brand-story", "type": "brand-story", "brandName": "", "slides": [], **fields}]
                self.assertEqual(self.request("PUT", f"/api/projects/{project['id']}", project)[0], 400)
                self.assertEqual(self.store.get(project["id"])["revision"], 0)

    def test_same_filename_is_independent_and_stale_assets_cannot_erase_uploads(self):
        project = self.create()
        first = self.upload(project)[2]
        second = self.upload(project)[2]
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual((first["width"], first["height"]), (4, 3))
        self.assertEqual(self.store.get(project["id"])["revision"], 0)
        project["gallery"] = [{"id": "slot-a", "assetId": first["id"]}, {"id": "slot-b", "assetId": second["id"]}]
        status, _, saved = self.request("PUT", f"/api/projects/{project['id']}", project)
        self.assertEqual(status, 200)
        self.assertEqual(set(saved["assets"]), {first["id"], second["id"]})
        reloaded = server.ProjectStore(Path(self.temporary.name)).get(project["id"])
        self.assertEqual(reloaded["assets"], saved["assets"])

    def test_readable_project_folders_and_name_collisions(self):
        first = self.create("示例 · 现有设计稿")
        second = self.create("示例 · 现有设计稿")
        self.assertEqual(self.store.directory(first["id"]).name, "示例 · 现有设计稿")
        self.assertEqual(self.store.directory(second["id"]).name, "示例 · 现有设计稿 (2)")
        self.assertNotEqual(first["id"], second["id"])
        asset = self.upload(first, category="aplus")[2]
        first["name"] = "修改显示名称"
        self.assertEqual(self.request("PUT", f"/api/projects/{first['id']}", first)[0], 200)
        reopened = server.ProjectStore(self.store.root)
        self.assertEqual(reopened.get(first["id"])["name"], "修改显示名称")
        self.assertEqual(reopened.directory(first["id"]).name, "示例 · 现有设计稿")
        self.assertEqual(reopened.asset(first["id"], asset["id"])[0].read_bytes(), png())
        self.assertEqual({item["id"] for item in reopened.list()}, {first["id"], second["id"]})

    def test_project_folder_names_are_windows_safe(self):
        for name in ("../../产品:测试?*<>|", "CON", "NUL.txt", "...", "产品" * 90):
            with self.subTest(name=name):
                project = self.create(name)
                folder = self.store.directory(project["id"])
                self.assertEqual(folder.resolve().parent, self.store.root)
                self.assertNotRegex(folder.name, r'[<>:"/\\|?*\x00-\x1f]')
                self.assertFalse(folder.name.endswith((".", " ")))
                self.assertNotIn(folder.name.split(".")[0].upper(), {"CON", "NUL"})
                self.assertLessEqual(len(folder.name), 65)
                self.assertEqual(self.store.get(project["id"])["name"], name)

    def test_legacy_project_folder_migration_keeps_ids_and_all_files(self):
        project = self.create("现有设计稿")
        asset = self.upload(project, category="aplus")[2]
        named = self.store.directory(project["id"])
        legacy = self.store.root / project["id"]
        self.assertEqual(named.resolve().parent, self.store.root)
        self.assertEqual(legacy.resolve().parent, self.store.root)
        named.rename(legacy)
        named.mkdir()
        (named / "keep.txt").write_text("existing folder", encoding="utf-8")
        before = {path.relative_to(legacy).as_posix(): path.read_bytes() for path in legacy.rglob("*") if path.is_file()}
        self.assertEqual(self.request("GET", f"/api/projects/{project['id']}")[0], 200)
        self.assertEqual(self.store.migrate_project_folders(), {"migrated": 1, "errors": []})
        migrated = self.store.directory(project["id"])
        self.assertEqual(migrated.name, "现有设计稿 (2)")
        self.assertFalse(legacy.exists())
        self.assertEqual((named / "keep.txt").read_text(encoding="utf-8"), "existing folder")
        after = {path.relative_to(migrated).as_posix(): path.read_bytes() for path in migrated.rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        self.assertEqual(self.request("GET", f"/api/projects/{project['id']}/assets/{asset['id']}")[2], png())
        self.assertEqual(self.store.migrate_project_folders(), {"migrated": 0, "errors": []})

    def test_failed_project_folder_migration_keeps_original_readable(self):
        project = self.create("迁移失败草稿")
        named = self.store.directory(project["id"])
        legacy = self.store.root / project["id"]
        self.assertEqual(named.resolve().parent, self.store.root)
        self.assertEqual(legacy.resolve().parent, self.store.root)
        named.rename(legacy)
        with mock.patch.object(Path, "rename", side_effect=PermissionError("blocked")):
            report = self.store.migrate_project_folders()
        self.assertEqual(report["migrated"], 0)
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(self.store.get(project["id"]), project)
        self.assertEqual(self.store.migrate_project_folders(), {"migrated": 1, "errors": []})

    def test_duplicate_project_ids_are_not_silently_resolved(self):
        project = self.create("原项目")
        shutil.copytree(self.store.directory(project["id"]), self.store.root / "重复项目")
        status, _, result = self.request("GET", f"/api/projects/{project['id']}")
        self.assertEqual(status, 500)
        self.assertIn("error", result)

    def test_concurrent_saves_allow_exactly_one_writer(self):
        project = self.create()
        def update(name):
            incoming = copy.deepcopy(project)
            incoming["name"] = name
            return self.request("PUT", f"/api/projects/{project['id']}", incoming)[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(update, ("A", "B")))
        self.assertEqual(sorted(statuses), [200, 409])
        self.assertEqual(self.store.get(project["id"])["revision"], 1)

    def test_separate_store_instances_share_the_save_lock(self):
        project = self.create()
        separate_store = server.ProjectStore(Path(self.temporary.name))
        def update(store):
            try:
                store.save(project["id"], project)
                return 200
            except server.APIError as error:
                return error.status
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(update, (self.store, separate_store)))
        self.assertEqual(sorted(statuses), [200, 409])

    def test_failed_atomic_save_preserves_previous_document(self):
        project = self.create()
        path = self.store.directory(project["id"]) / "project.json"
        original = path.read_bytes()
        project["name"] = "无法保存的修改"
        with mock.patch.object(server.os, "replace", side_effect=PermissionError("blocked")):
            status, _, error = self.request("PUT", f"/api/projects/{project['id']}", project)
        self.assertEqual(status, 500)
        self.assertIn("error", error)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.glob(".saving-*")), [])

    def test_invalid_upload_leaves_project_and_catalog_unchanged(self):
        project = self.create()
        good = self.upload(project)[2]
        previous = self.store.get(project["id"])
        for content, mime in [(b"not-an-image", "image/png"), (png()[:-8], "image/png"), (mp4()[:-1], "video/mp4"), (png(), "application/x-msdownload")]:
            with self.subTest(mime=mime, size=len(content)):
                status, _, result = self.upload(project, content, mime)
                self.assertIn(status, (400, 415))
                self.assertIn("error", result)
                self.assertEqual(self.store.get(project["id"]), previous)
        assets = self.store.directory(project["id"]) / "assets"
        self.assertEqual(set(item.name for item in assets.iterdir()), {"main", "aplus", "catalog.json"})
        self.assertEqual([item.name for item in (assets / "main").iterdir()], [good["id"] + ".png"])
        self.assertEqual(list((assets / "aplus").iterdir()), [])

    def test_catalog_failure_rolls_back_uploaded_file(self):
        project = self.create()
        original_replace = server.os.replace
        def fail_catalog(source, target):
            if Path(target).name == "catalog.json":
                raise OSError("disk full")
            return original_replace(source, target)
        with mock.patch.object(server.os, "replace", side_effect=fail_catalog):
            status, _, _ = self.upload(project)
        self.assertEqual(status, 500)
        self.assertEqual(self.store.get(project["id"])["assets"], {})
        assets = self.store.directory(project["id"]) / "assets"
        self.assertEqual(set(item.name for item in assets.iterdir()), {"main", "aplus"})
        self.assertEqual(list(assets.rglob("*.png")), [])

    def test_upload_categories_have_separate_paths_and_stable_asset_urls(self):
        project = self.create()
        for category, content, mime in [("main", png(), "image/png"), ("aplus", png(6, 5), "image/png"), ("aplus", mp4(), "video/mp4")]:
            with self.subTest(category=category, mime=mime):
                status, _, asset = self.upload(project, content, mime, category=category)
                self.assertEqual(status, 201)
                self.assertEqual(asset["category"], category)
                path, metadata = self.store.asset(project["id"], asset["id"])
                self.assertEqual(path.parent.name, category)
                self.assertEqual(metadata, asset)
                self.assertEqual(path.read_bytes(), content)
                status, _, result = self.request("GET", f"/api/projects/{project['id']}/assets/{asset['id']}")
                self.assertEqual((status, result), (200, content))
        for category in ("unknown", "..%2F..", "%2Ftmp"):
            self.assertEqual(self.upload(project, category=category)[0], 400)

    def test_migration_classifies_all_used_media_and_preserves_unassigned_files(self):
        project = self.create()
        main, image, slide, poster, shared, unused = [self.upload(project)[2] for _ in range(6)]
        video = self.upload(project, mp4(), "video/mp4")[2]
        project["gallery"] = [{"id": "main-slot", "assetId": main["id"]}, {"id": "shared-slot", "assetId": shared["id"]}]
        project["modules"] = [
            {"id": "image", "type": "image", "assetId": image["id"]},
            {"id": "shared", "type": "image", "assetId": shared["id"]},
            {"id": "carousel", "type": "carousel", "slides": [{"id": "slide", "assetId": slide["id"]}]},
            {"id": "video", "type": "video", "videoAssetId": video["id"], "posterAssetId": poster["id"]},
        ]
        self.store.save(project["id"], project)
        directory = self.make_legacy(project, main, image, slide, poster, shared, unused, video)
        original_project = (directory.parent / "project.json").read_bytes()
        self.assertEqual(self.store.asset(project["id"], main["id"])[0].parent, directory)
        report = self.store.migrate_assets()
        self.assertEqual(report, {"migrated": 6, "unassigned": 1, "errors": []})
        self.assertEqual((directory.parent / "project.json").read_bytes(), original_project)
        for asset, category in [(main, "main"), (shared, "main"), (image, "aplus"), (slide, "aplus"), (poster, "aplus"), (video, "aplus")]:
            path, metadata = self.store.asset(project["id"], asset["id"])
            self.assertEqual(path.parent, directory / category)
            self.assertEqual(metadata["category"], category)
            self.assertFalse((directory / path.name).exists())
        self.assertEqual((directory / "aplus" / (shared["id"] + ".png")).read_bytes(), png())
        self.assertEqual(self.store.asset(project["id"], unused["id"])[0].parent, directory)
        self.assertEqual(self.store.migrate_assets(), {"migrated": 0, "unassigned": 1, "errors": []})

    def test_migration_classifies_brand_story_background_logo_and_cards_as_aplus(self):
        project = self.create()
        background, logo, card = [self.upload(project)[2] for _ in range(3)]
        project["modules"] = [{
            "id": "brand-story", "type": "brand-story", "brandName": "Example",
            "backgroundAssetId": background["id"], "logoAssetId": logo["id"],
            "slides": [{"id": "brand-card", "assetId": card["id"]}],
        }]
        self.store.save(project["id"], project)
        directory = self.make_legacy(project, background, logo, card)
        original_project = (directory.parent / "project.json").read_bytes()
        self.assertEqual(self.store.migrate_assets(), {"migrated": 3, "unassigned": 0, "errors": []})
        self.assertEqual((directory.parent / "project.json").read_bytes(), original_project)
        for asset in (background, logo, card):
            path, metadata = self.store.asset(project["id"], asset["id"])
            self.assertEqual(path.parent, directory / "aplus")
            self.assertEqual(metadata["category"], "aplus")
            self.assertEqual(path.read_bytes(), png())
            self.assertFalse((directory / path.name).exists())
        self.assertEqual(self.store.migrate_assets(), {"migrated": 0, "unassigned": 0, "errors": []})

    def test_interrupted_migration_preserves_legacy_files_and_can_be_retried(self):
        project = self.create()
        asset = self.upload(project)[2]
        project["modules"] = [{"id": "image", "type": "image", "assetId": asset["id"]}]
        self.store.save(project["id"], project)
        directory = self.make_legacy(project, asset)
        before = (directory / "catalog.json").read_bytes()
        with mock.patch.object(server, "atomic_json", side_effect=OSError("disk full")):
            report = self.store.migrate_assets()
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual((directory / "catalog.json").read_bytes(), before)
        self.assertEqual(self.store.asset(project["id"], asset["id"])[0].read_bytes(), png())
        self.assertEqual((directory / (asset["id"] + ".png")).read_bytes(), png())
        self.assertEqual(self.store.migrate_assets()["migrated"], 1)
        self.assertEqual(self.store.asset(project["id"], asset["id"])[0].parent.name, "aplus")

    def test_migration_does_not_overwrite_conflicting_destination(self):
        project = self.create()
        asset = self.upload(project)[2]
        project["gallery"] = [{"id": "slot", "assetId": asset["id"]}]
        self.store.save(project["id"], project)
        directory = self.make_legacy(project, asset)
        destination = directory / "main" / (asset["id"] + ".png")
        destination.write_bytes(b"existing different file")
        self.assertEqual(len(self.store.migrate_assets()["errors"]), 1)
        self.assertEqual(destination.read_bytes(), b"existing different file")
        self.assertEqual(self.store.asset(project["id"], asset["id"])[0].read_bytes(), png())

    def test_catalog_category_cannot_escape_assets_directory(self):
        project = self.create()
        asset = self.upload(project)[2]
        directory = self.store.directory(project["id"])
        catalog = self.store.catalog(directory)
        catalog[asset["id"]]["category"] = "../../outside"
        server.atomic_json(directory / "assets" / "catalog.json", catalog)
        status, _, _ = self.request("GET", f"/api/projects/{project['id']}/assets/{asset['id']}")
        self.assertEqual(status, 400)

    def test_missing_or_wrong_type_asset_reference_is_rejected(self):
        project = self.create()
        video = self.upload(project, mp4(), "video/mp4", "clip.mp4")[2]
        for asset_id in ("a" * 32, video["id"]):
            project["gallery"] = [{"id": "bad-slot", "assetId": asset_id}]
            status, _, _ = self.request("PUT", f"/api/projects/{project['id']}", project)
            self.assertEqual(status, 400)
            self.assertEqual(self.store.get(project["id"])["gallery"], [])

    def test_video_ranges_head_and_complete_fetch(self):
        project = self.create()
        content = mp4()
        status, _, asset = self.upload(project, content, "video/mp4", "clip.mp4")
        self.assertEqual(status, 201)
        path = f"/api/projects/{project['id']}/assets/{asset['id']}"
        status, headers, result = self.request("GET", path)
        self.assertEqual((status, result), (200, content))
        self.assertEqual(headers["Accept-Ranges"], "bytes")
        for header, expected in [("bytes=0-9", content[:10]), ("bytes=10-", content[10:]), ("bytes=-7", content[-7:]), ("bytes=10-99999", content[10:]), ("bytes=-99999", content)]:
            with self.subTest(header=header):
                status, headers, result = self.request("GET", path, headers={"Range": header})
                self.assertEqual((status, result), (206, expected))
                self.assertEqual(int(headers["Content-Length"]), len(expected))
        for header in ("bytes=99999-", "bytes=10-2", "bytes=-0", "bytes=0-1,3-4", "bytes=-"):
            status, headers, _ = self.request("GET", path, headers={"Range": header})
            self.assertEqual(status, 416)
            self.assertEqual(headers["Content-Range"], f"bytes */{len(content)}")
        status, headers, result = self.request("HEAD", path)
        self.assertEqual((status, result), (200, b""))
        self.assertEqual(int(headers["Content-Length"]), len(content))
        status, headers, result = self.request("HEAD", path, headers={"Range": "bytes=0-9"})
        self.assertEqual((status, result), (206, b""))
        self.assertEqual(headers["Content-Length"], "10")

    def test_host_origin_and_path_boundaries(self):
        self.create()
        for headers in ({"Host": f"evil.example:{self.port}"}, {"Origin": "https://evil.example"}, {"Origin": "null"}, {"Sec-Fetch-Site": "cross-site"}):
            status, _, _ = self.request("GET", "/api/projects", headers=headers)
            self.assertEqual(status, 403)
        status, _, _ = self.request("GET", "/api/projects", headers={"Origin": f"http://127.0.0.1:{self.port}"})
        self.assertEqual(status, 200)
        for path in ("/server.py", "/data/", "/../server.py", "/%2e%2e/server.py", "/api/projects/../../server.py", "/api/projects/%2e%2e"):
            status, _, _ = self.request("GET", path)
            self.assertEqual(status, 404)

    def test_json_content_validation_and_size_limit(self):
        status, _, _ = self.request("POST", "/api/projects", b"{not json}", {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        status, _, _ = self.request("POST", "/api/projects", b"[]", {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        status, _, _ = self.request("POST", "/api/projects", b"", {"Content-Type": "application/json", "Content-Length": str(server.JSON_LIMIT + 1)})
        self.assertEqual(status, 413)
        self.assertEqual(self.store.list(), [])

    def test_auto_port_uses_next_available_port(self):
        second = server.make_server(self.store, self.port, auto_port=True)
        try:
            self.assertNotEqual(second.server_address[1], self.port)
            self.assertEqual(second.server_address[0], "127.0.0.1")
        finally:
            second.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
