#!/usr/bin/env python3
"""Download page thumbnails listed in a saved get-design-pages response.

Only needed with the older Canva tool set: read-design returns thumbnails as images directly.

Usage: python3 fetch_thumbs.py pages.json out_dir

pages.json is the get-design-pages result saved verbatim ({"items": [...]} or a bare list).
Saves out_dir/p{page_number}.png and prints page, size and page_id. Thumbnail URLs are signed
and expire after about two hours; call get-design-pages again if downloads return 403.
"""
import json
import os
import sys
import urllib.request


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    items = data.get("items", []) if isinstance(data, dict) else data
    os.makedirs(sys.argv[2], exist_ok=True)
    failed = 0
    for it in items:
        n = it.get("page_number") or it.get("index")
        url = (it.get("thumbnail") or {}).get("url")
        dims = it.get("dimensions") or {}
        if not url:
            print(f"P{n}: no thumbnail url")
            failed += 1
            continue
        path = os.path.join(sys.argv[2], f"p{n}.png")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as fh:
                fh.write(r.read())
            print(f"P{n}: {dims.get('width')}x{dims.get('height')}  {it.get('id', '')}  -> {path}")
        except Exception as e:  # noqa: BLE001
            print(f"P{n}: download failed ({e})")
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
