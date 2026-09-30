"""Capture the authorized Ginv-Ads source with a fresh HTTP session.

The access code is read from GINV_ACCESS_CODE or a hidden one-time prompt.
Credentials and session cookies are never written to the archive or logs.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
START_URL = "https://sellerhelp.top/projects/Ginv-Ads%E5%B9%BF%E5%91%8A%E6%99%BA%E5%BA%93/"


def clean_html(html: str, access_code: str) -> str:
    if access_code:
        html = html.replace(access_code, "[REDACTED]")
    soup = BeautifulSoup(html, "html.parser")
    for field in soup.select('input[type="password"]'):
        field.attrs.pop("value", None)
    for node in soup.select("[data-cf-beacon]"):
        node.attrs.pop("data-cf-beacon", None)
    return str(soup)


def authenticated_session(access_code: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Ginv-Ads authorized local archive/1.0"})
    challenge = session.get(START_URL, timeout=40)
    challenge.raise_for_status()
    if "/api/verify" not in challenge.text:
        raise RuntimeError("The expected access-code form was not present.")
    # These fields are taken from the live verification form's own JavaScript.
    result = session.post(
        urljoin(START_URL, "/api/verify"),
        json={
            "type": "project",
            "identifier": "Ginv-Ads广告智库",
            "password": access_code,
            "remember": False,
        },
        timeout=40,
    )
    result.raise_for_status()
    if result.json().get("success") is not True:
        raise RuntimeError("The site did not accept the access code.")
    return session


def node_html(node) -> str:
    return node.decode_contents() if node else ""


def node_text(node) -> str:
    return node.get_text("\n", strip=True) if node else ""


def extract_function(script: str, name: str) -> str:
    match = re.search(r"function\s+" + re.escape(name) + r"\s*\([^)]*\)\s*\{", script)
    if not match:
        return ""
    depth, quote, escaped = 1, "", False
    pos = match.end()
    while pos < len(script):
        char = script[pos]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
        elif char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return script[match.start():pos + 1]
        pos += 1
    raise ValueError("Unclosed source function: " + name)


def extract_content(html: str, captured_at: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    script = "\n\n".join(node.get_text() for node in soup.select("script:not([src])"))
    topics, articles, concepts, tools = [], [], [], []
    for topic_order, topic in enumerate(soup.select("#zoneContent .topic"), 1):
        topic_id = topic["id"]
        topic_articles = []
        for article_order, article in enumerate(topic.select("article.method-card"), 1):
            article_id = f"{topic_id}-{article_order:02}"
            body = article.select_one(".method-body")
            item = {
                "id": article_id,
                "topicId": topic_id,
                "order": article_order,
                "title": node_text(article.select_one(".method-q")),
                "bodyHtml": node_html(body),
                "bodyText": node_text(body),
                "sourceUrl": START_URL + "#" + topic_id,
                "summary": node_text(article.select_one(".det")),
                "tags": [node_text(n) for n in article.select(".tag")],
                "sections": [
                    {"title": node_text(n.select_one(".blk-t")), "html": str(n), "text": node_text(n)}
                    for n in article.select(".blk")
                ],
            }
            articles.append(item)
            topic_articles.append(article_id)
        sop, decision, tips = (topic.select_one(s) for s in (".sop-card", ".dec-card", ".tips"))
        topics.append({
            "id": topic_id,
            "title": topic.get("data-title", node_text(topic.select_one("h2"))),
            "order": topic_order,
            "sourceUrl": START_URL + "#" + topic_id,
            "sopHtml": node_html(sop), "sopText": node_text(sop),
            "decisionHtml": node_html(decision), "decisionText": node_text(decision),
            "tipsHtml": node_html(tips), "tipsText": node_text(tips),
            "bodyHtml": node_html(topic), "bodyText": node_text(topic),
            "articleIds": topic_articles,
        })
    concept_ids = set()
    for order, concept in enumerate(soup.select(".concept-card"), 1):
        name = concept.select_one(".c-name")
        subtitle = name.select_one(".en") if name else None
        title = "".join(str(n) for n in name.contents if getattr(n, "name", None) is None).strip()
        concept_id = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or f"concept-{order:02}"
        if concept_id in concept_ids:
            concept_id = f"{concept_id}-{order:02}"
        concept_ids.add(concept_id)
        concepts.append({
            "id": concept_id, "order": order, "title": title,
            "subtitle": node_text(subtitle), "fullName": node_text(concept.select_one(".c-full")),
            "formula": node_text(concept.select_one(".c-formula")),
            "meaning": node_text(concept.select_one(".c-meaning")),
            "use": node_text(concept.select_one(".c-use")),
            "tips": node_text(concept.select_one(".c-tips")),
            "bodyHtml": node_html(concept), "bodyText": node_text(concept),
            "sourceUrl": START_URL + "#concepts",
        })
    for order, tool in enumerate(soup.select(".tool-grid .tool"), 1):
        button = tool.select_one("button[onclick]")
        function_name = button["onclick"].split("(")[0]
        output = tool.select_one(".tool-out[id]")
        tools.append({
            "id": output["id"][:-1], "order": order,
            "title": node_text(tool.select_one("h3")),
            "description": node_text(tool.select_one("p")),
            "inputs": [{
                "id": field["id"], "label": node_text(field.find_parent("label")),
                "type": field.get("type", "text"), "defaultValue": field.get("value", ""),
            } for field in tool.select("input[id]")],
            "functionName": function_name, "sourceCode": extract_function(script, function_name),
            "bodyHtml": node_html(tool), "bodyText": node_text(tool),
            "sourceUrl": START_URL + "#tools",
        })
    counts = {"topics": len(topics), "articles": len(articles), "concepts": len(concepts), "tools": len(tools)}
    return {
        "schemaVersion": 1, "capturedAt": captured_at,
        "source": {"url": START_URL, "title": node_text(soup.title), "archivePath": "archive/source/app.html"},
        "counts": counts, "topics": topics, "articles": articles, "concepts": concepts, "tools": tools,
        "coverage": {"status": "content-extracted; asset-and-link-audit-pending", "contentLoading": "All article and concept bodies are embedded in the authorized HTML."},
    }


def write_content(html: str, captured_at: str) -> dict:
    content = extract_content(html, captured_at)
    target = ROOT / "public" / "data" / "source-content.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    inline = "\n\n".join(n.get_text() for n in BeautifulSoup(html, "html.parser").select("script:not([src])"))
    (ROOT / "archive" / "source" / "inline.js").write_text(inline, encoding="utf-8")
    styles = "\n\n".join(n.get_text() for n in BeautifulSoup(html, "html.parser").select("style"))
    (ROOT / "archive" / "source" / "styles.css").write_text(styles, encoding="utf-8")
    return content


def asset_refs(text: str, base_url: str, content_type: str) -> set[str]:
    refs = set()
    if "html" in content_type:
        soup = BeautifulSoup(text, "html.parser")
        for node in soup.select("script[src], img[src], source[src], video[src], audio[src], iframe[src], link[href]"):
            if node.name == "link" and "stylesheet" not in node.get("rel", []) and "icon" not in node.get("rel", []):
                continue
            refs.add(urljoin(base_url, node.get("src", node.get("href", ""))))
        for node in soup.select("[srcset]"):
            for entry in node["srcset"].split(","):
                refs.add(urljoin(base_url, entry.strip().split(" ")[0]))
    for match in re.finditer(r"url\(\s*['\"]?([^\s'\"\)]+)", text):
        refs.add(urljoin(base_url, match.group(1)))
    if "javascript" in content_type or "html" in content_type:
        for match in re.finditer(r"(?:src|href|image|avatar)\s*[:=]\s*['\"]([^'\"]+)['\"]", text):
            ref = match.group(1)
            if re.search(r"\.(?:css|js|png|jpe?g|webp|gif|svg|woff2?|ttf|eot)(?:[?#]|$)", ref):
                refs.add(urljoin(base_url, ref))
    return {urldefrag(url)[0] for url in refs if urlparse(url).scheme in ("http", "https")}


def archive_path(url: str) -> Path:
    parsed = urlparse(url)
    host = "site" if parsed.hostname == "sellerhelp.top" else parsed.hostname
    path = unquote(parsed.path).lstrip("/")
    target = ROOT / "archive" / "assets" / host / (path or "index.html")
    if parsed.query:
        target = target.with_name(target.stem + "-" + hashlib.sha256(parsed.query.encode()).hexdigest()[:8] + target.suffix)
    return target


def capture_assets(session: requests.Session, html: str, page_url: str, access_code: str) -> list[dict]:
    refs = asset_refs(html, page_url, "text/html")
    wrapper = ROOT / "archive" / "source" / "index.html"
    if wrapper.exists():
        refs.update(asset_refs(wrapper.read_text(encoding="utf-8"), START_URL, "text/html"))
    queue = sorted(refs)
    seen, manifest = set(), []
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        # Pages use a separate scoped content crawl, not the dependency crawler.
        if "render=direct" in url:
            continue
        result = {"url": url}
        try:
            response = session.get(url, timeout=(15, 45))
            result.update({"status": response.status_code, "contentType": response.headers.get("Content-Type", "")})
            response.raise_for_status()
            content_type = result["contentType"]
            data = response.content
            is_text = any(part in content_type for part in ("text/", "javascript", "json", "svg"))
            if is_text:
                # Shared JS omits charset. requests' guessed Windows-1254 corrupts
                # Chinese here; the site's actual response bytes are UTF-8.
                try:
                    text = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    text = response.text
                if access_code:
                    text = text.replace(access_code, "[REDACTED]")
                if "html" in content_type:
                    text = clean_html(text, access_code)
                data = text.encode("utf-8")
                for ref in sorted(asset_refs(text, response.url, content_type)):
                    if ref not in seen:
                        queue.append(ref)
            destination = archive_path(url)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            result.update({"path": destination.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        except requests.RequestException as error:
            # Do not print request headers or exception representations containing cookies.
            result["error"] = type(error).__name__
        manifest.append(result)
        print("Asset", result.get("status", "failed"), url, flush=True)
    return manifest


def inspect_injected_links(session: requests.Session, assets: list[dict], access_code: str) -> list[dict]:
    links, seen = [], set()
    for asset in assets:
        if not asset.get("path", "").endswith(".js"):
            continue
        text = (ROOT / asset["path"]).read_text(encoding="utf-8")
        for match in re.finditer(r"href\s*:\s*['\"]([^'\"]+)['\"]", text):
            href = match.group(1)
            if "${" in href:
                continue
            url = urljoin(asset["url"], href)
            if url in seen:
                continue
            seen.add(url)
            result = {"url": url, "discoveredIn": asset["path"], "classification": "shared-site navigation or promotional referral; outside Ginv-Ads project"}
            if urlparse(url).hostname == "sellerhelp.top":
                try:
                    response = session.get(url, timeout=(15, 40))
                    soup = BeautifulSoup(clean_html(response.text, access_code), "html.parser")
                    result.update({"checked": True, "status": response.status_code, "title": node_text(soup.title), "accessVerificationRequired": "访问验证 -" in node_text(soup.title), "recursiveCapture": False})
                except requests.RequestException as error:
                    result.update({"checked": True, "error": type(error).__name__})
            else:
                result.update({"checked": False, "recursiveCapture": False, "reason": "External promotional referral is outside the requested project."})
            links.append(result)
    return links


def audit_content(html: str, content: dict, assets: list[dict]) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    anchors, links, data_endpoints = [], [], []
    for node in soup.select("a[href]"):
        href = node["href"]
        if href.startswith("#"):
            anchors.append({"href": href, "targetExists": soup.find(id=href[1:]) is not None, "text": node_text(node)})
        else:
            links.append({"url": urljoin(START_URL, href), "text": node_text(node)})
    for match in re.finditer(r"fetch\(\s*['\"]([^'\"]+)", html):
        endpoint = match.group(1)
        data_endpoints.append({"url": urljoin(START_URL, endpoint), "purpose": "visitor statistics" if endpoint == "/api/track" else "requires review", "containsContent": endpoint != "/api/track", "requested": False})
    counts = content["counts"]
    expected = {"topics": 13, "articles": 54, "concepts": 20, "tools": 5}
    source_articles = soup.select("#zoneContent article.method-card")
    article_parity = len(source_articles) == len(content["articles"]) and all(
        node_text(source.select_one(".method-q")) == article["title"]
        and node_html(source.select_one(".method-body")) == article["bodyHtml"]
        for source, article in zip(source_articles, content["articles"])
    )
    sources = []
    for name in ("index.html", "app.html"):
        path = ROOT / "archive" / "source" / name
        if path.exists():
            data = path.read_bytes()
            sources.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    per_topic = []
    for topic in content["topics"]:
        nav = soup.select_one(f'a[data-topic="{topic["id"]}"] .nav-cnt')
        declared = int(node_text(nav))
        actual = len(topic["articleIds"])
        per_topic.append({"id": topic["id"], "declared": declared, "captured": actual, "match": declared == actual})
    return {
        "status": "complete" if counts == expected and article_parity
        and len({n["id"] for n in content["articles"]}) == counts["articles"]
        and len({n["id"] for n in content["concepts"]}) == counts["concepts"]
        and all(n["bodyText"] for n in content["articles"])
        and all(n["match"] for n in per_topic)
        and all(n["targetExists"] for n in anchors)
        and assets and all(n.get("status") == 200 for n in assets)
        and not any(n["containsContent"] for n in data_endpoints) else "requires-review",
        "scope": "Authorized Ginv-Ads project and its explicitly referenced dependencies; promotional sites are not recursively crawled.",
        "contentLoading": "All 54 method bodies and 20 concept cards are embedded in the authorized HTML. No deferred content fetch exists in its inline JavaScript.",
        "expectedCounts": expected, "capturedCounts": counts, "perTopic": per_topic,
        "sourceDocuments": sources, "articleHtmlAndTitleParity": article_parity,
        "internalAnchors": anchors, "contentLinks": links, "dataEndpoints": data_endpoints,
        "assets": assets, "imageElements": len(soup.select("img")),
        "articleIdsUnique": len({n["id"] for n in content["articles"]}) == counts["articles"],
        "conceptIdsUnique": len({n["id"] for n in content["concepts"]}) == counts["concepts"],
        "emptyArticleBodies": sum(not n["bodyText"] for n in content["articles"]),
        "notes": ["The original wording, numeric recommendations, and typographical errors are preserved. Formula review is recorded separately.", "No access code, authentication response, session cookie, or browser storage is archived."],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial-only", action="store_true")
    parser.add_argument("--extract-existing", action="store_true")
    parser.add_argument("--audit-existing", action="store_true", help="Audit the already verified snapshot and public dependencies without another login.")
    args = parser.parse_args()
    if args.extract_existing:
        content = write_content((ROOT / "archive" / "source" / "app.html").read_text(encoding="utf-8"), datetime.now(timezone.utc).isoformat())
        print(json.dumps(content["counts"]))
        return
    if args.audit_existing:
        html = (ROOT / "archive" / "source" / "app.html").read_text(encoding="utf-8")
        target = ROOT / "public" / "data" / "source-content.json"
        content = json.loads(target.read_text(encoding="utf-8"))
        session = requests.Session()
        session.headers.update({"User-Agent": "Ginv-Ads authorized local archive/1.0"})
        assets = capture_assets(session, html, START_URL, "")
        coverage = audit_content(html, content, assets)
        coverage["injectedNavigationLinks"] = inspect_injected_links(session, assets, "")
        content["coverage"] = coverage
        target.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        (ROOT / "archive" / "coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        styles = "\n\n".join(n.get_text() for n in BeautifulSoup(html, "html.parser").select("style"))
        (ROOT / "archive" / "source" / "styles.css").write_text(styles, encoding="utf-8")
        print(json.dumps({"coverageStatus": coverage["status"], "assets": len(assets), "counts": content["counts"]}))
        return
    access_code = os.environ.pop("GINV_ACCESS_CODE", "") or getpass.getpass("Access code (hidden): ")
    session = authenticated_session(access_code)
    response = session.get(START_URL, timeout=40)
    response.raise_for_status()
    html = clean_html(response.text, access_code)
    if "访问验证 -" in html:
        raise RuntimeError("Authorization did not persist in the fresh HTTP session.")
    destination = ROOT / "archive" / "source" / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    frame = soup.select_one("iframe[src]")
    if frame:
        frame_url = urljoin(response.url, frame["src"])
        response = session.get(frame_url, timeout=40)
        response.raise_for_status()
        html = clean_html(response.text, access_code)
        (destination.parent / "app.html").write_text(html, encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
    summary = {
        "capturedAt": datetime.now(timezone.utc).isoformat(),
        "sourceUrl": response.url,
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "bytes": len(html.encode("utf-8")),
        "links": [n.get("href") for n in soup.select("a[href]")],
        "scripts": [n.get("src") for n in soup.select("script[src]")],
    }
    content = write_content(html, summary["capturedAt"])
    summary["counts"] = content["counts"]
    if not args.initial_only:
        assets = capture_assets(session, html, response.url, access_code)
        coverage = audit_content(html, content, assets)
        coverage["injectedNavigationLinks"] = inspect_injected_links(session, assets, access_code)
        content["coverage"] = coverage
        (ROOT / "public" / "data" / "source-content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        (ROOT / "archive" / "coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["coverageStatus"] = coverage["status"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
