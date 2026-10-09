#!/usr/bin/env python3
"""Verify Canva notes after writing, and audit on-image text against zone ①.

Usage:
  python3 verify_notes.py --expected notes_dir --readback notes_after.json [--on-image-dir onimage_dir]
  python3 verify_notes.py --compare notes_before.json notes_now.json      # detect concurrent edits

--readback / --compare files are the get-presenter-notes output saved as JSON:
  [{"page_id": "...", "page_number": 3, "notes": "..."}]
--expected is the build_notes.py output dir (p{N}.txt + manifest.json).
--on-image-dir holds p{N}.txt with get-design-content output for that single page.

Checks:
  - per page: notes in Canva == expected text (trailing whitespace ignored) -> MATCH / DIFF (FLAG)
  - on-image audit (optional):
      zone ① line found on the canvas (whitespace/case ignored) -> 已上图, else 未上图 (INFO)
      canvas line that looks like an internal instruction, or equals a zone ②/③ line -> FLAG
Exit code 1 if any FLAG.
"""
import argparse
import json
import os
import re
import sys

INSTRUCTION = re.compile(
    r"\bKEEP\b|\bDO NOT\b|^\s*(Remove|Delete|Replace|Fix|TODO|Designer)\b|\bOptional\s*:|\[Page\s*\d|→|^\s*【",
    re.I,
)
ZONE = re.compile(r"^【([①②③④⑤])")


def norm(text):
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


def squash(text):
    return re.sub(r"\s+", "", text).lower()


def load_readback(path):
    return {int(i["page_number"]): i.get("notes", "") for i in json.load(open(path, encoding="utf-8"))}


def zones(text):
    out, cur = {}, None
    for line in text.split("\n"):
        m = ZONE.match(line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if cur and line.strip():
            out[cur].append(line)
    return out


def first_diff(a, b):
    al, bl = a.split("\n"), b.split("\n")
    for i in range(max(len(al), len(bl))):
        x = al[i] if i < len(al) else "<缺>"
        y = bl[i] if i < len(bl) else "<缺>"
        if x != y:
            return f"第 {i + 1} 行  期望: {x[:70]!r}  实际: {y[:70]!r}"
    return ""


def compare(before_path, now_path):
    b, n = load_readback(before_path), load_readback(now_path)
    changed = [p for p in sorted(set(b) | set(n)) if norm(b.get(p, "")) != norm(n.get(p, ""))]
    for p in changed:
        print(f"CHANGED P{p}: {first_diff(norm(b.get(p, '')), norm(n.get(p, '')))}")
    print(f"{len(changed)} page(s) changed since first read")
    return 1 if changed else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected")
    ap.add_argument("--readback")
    ap.add_argument("--on-image-dir")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "NOW"))
    a = ap.parse_args()

    if a.compare:
        sys.exit(compare(*a.compare))
    if not (a.expected and a.readback):
        ap.error("--expected and --readback are required (or use --compare)")

    manifest = json.load(open(os.path.join(a.expected, "manifest.json"), encoding="utf-8"))
    readback = load_readback(a.readback)
    flags = 0
    for m in manifest["pages"]:
        n = m["page"]
        expected = norm(open(m["path"], encoding="utf-8").read())
        actual = norm(readback.get(n, ""))
        if expected == actual:
            print(f"MATCH P{n}")
        else:
            flags += 1
            print(f"FLAG  P{n} DIFF  {first_diff(expected, actual) if n in readback else '回读里没有这一页'}")

        if not a.on_image_dir:
            continue
        img_path = os.path.join(a.on_image_dir, f"p{n}.txt")
        if not os.path.exists(img_path):
            print(f"      P{n} 无图上文字文件，跳过上图审计")
            continue
        canvas = open(img_path, encoding="utf-8").read()
        canvas_sq = squash(canvas)
        z = zones(expected)
        for line in z.get("①", []):
            if line.startswith("（"):
                continue
            slot, copy = line.split("：", 1) if "：" in line else ("", line)
            copy_sq = squash(copy.replace("**", ""))
            status = "已上图" if copy_sq and copy_sq in canvas_sq else "未上图"
            print(f"      P{n} ①[{slot}] {status}: {copy[:60]}")
        internal = {squash(l.lstrip("- ")) for k in ("②", "③") for l in z.get(k, [])}
        for cl in canvas.split("\n"):
            if not cl.strip():
                continue
            if INSTRUCTION.search(cl) or squash(cl) in internal:
                flags += 1
                print(f"FLAG  P{n} 图上疑似内部指令: {cl.strip()[:70]}")
    print(f"done ({flags} FLAG)")
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
