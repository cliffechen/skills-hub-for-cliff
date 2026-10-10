#!/usr/bin/env python3
"""Build per-page Canva notes (four-zone format) from the copy JSON.

Usage:
  python3 build_notes.py copy.json [--out notes_dir] [--pages 1-8] [--before notes_before.json]

Reads the same copy.json as build_xlsx.py plus the optional "canva" block and "page" fields
(see references/canva-notes-format.md). Writes:
  notes_dir/p{N}.txt     full note text for page N (what gets pasted into Canva)
  notes_dir/all_notes.md all pages, for preview or manual pasting
  notes_dir/manifest.json [{page, page_id, label, path, chars}]

Lint (exit code 1 on any FLAG):
  - zone ① value contains CJK characters or designer-instruction words -> FLAG
  - zone ① value contains **bold** / *italic* markup (put the style in the slot name instead) -> FLAG
  - note longer than 5000 characters (Canva limit) -> FLAG
  - zone ① has a claim asterisk but no FDA footer line -> WARN
  - page has no zone ① lines -> WARN
"""
import argparse
import json
import os
import re
import sys

LEGEND = "【备注规则】只有①区内容可以上图；②③④区一律不得出现在图上。"
Z1 = "【① 上图文案 ON-IMAGE】"
Z2 = "【② 设计指令 DESIGNER ONLY · 不上图】"
Z3 = "【③ 待确认 TO CONFIRM】"
Z4 = "【④ 审核记录 REVIEW LOG】"
Z5 = "【⑤ 原备注 ARCHIVE】"
MAX_CHARS = 5000

CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
# KEEP / DO NOT only count in capitals: real headlines say "the One You Keep" or "Keep Showing Up."
INSTRUCTION = re.compile(
    r"\bKEEP\b|\bDO NOT\b|(?i:\bdo not put\b|^\s*(Remove|Delete|Replace|Fix|Add|Swap|Move|TODO|Designer|Note)\b"
    r"|\bOptional\s*:|\[Page\s*\d|\bFDA if\b|\bif needed\b)|→",
    re.M,
)
# **bold** / *italic* markup: on a Canva note every asterisk reads as a claim asterisk to be put on the image
STYLE_MARKUP = re.compile(r"\*\*|^\*[^*\n]+\*$", re.M)
CLAIM_STAR = re.compile(r"\*\s*$|\*\s*[.)]?\s*$")


def parse_pages(spec):
    if not spec:
        return None
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return out


def bullets(items):
    items = [i for i in items if str(i).strip()]
    if not items:
        return ["- 无。"]
    lines = []
    for item in items:
        text = str(item).strip()
        first, *rest = text.split("\n")
        lines.append("- " + first)
        lines.extend("  " + r for r in rest)
    return lines


def build_page(n, page, rows, issues, review_date, before_text):
    label = page.get("label", "")
    head = f"[P{n} · {label}]" if label else f"[P{n}]"
    z1_title = Z1 + page.get("on_image_hint", "")
    z1 = []
    if page.get("on_image_preface"):
        z1.append(page["on_image_preface"])
    for r in rows:
        if str(r.get("id", "")).upper().startswith("ALT"):
            continue
        slot = str(r.get("slot", "")).strip()
        z1.append(f"{slot}：{r.get('copy', '')}" if slot else str(r.get("copy", "")))

    designer = list(page.get("designer", []))
    confirm = list(page.get("confirm", []))
    for it in issues:
        fix, problem = it.get("fix", "").strip(), it.get("problem", "").strip()
        text = f"{fix}（{problem}）" if fix and problem else (fix or problem)
        (confirm if it.get("priority") == "确认" else designer).append(text)

    log = [f"{review_date}：{x}" if review_date else x for x in page.get("log", [])]

    parts = [head, LEGEND, "", z1_title, *z1, "", Z2, *bullets(designer), "", Z3, *bullets(confirm),
             "", Z4, *bullets(log)]
    if before_text is not None:
        parts += ["", Z5, before_text.strip() or "（原备注为空）"]
    return "\n".join(parts) + "\n", z1


def lint(n, text, z1_lines, rows):
    flags, warns = [], []
    for r in rows:
        if str(r.get("id", "")).upper().startswith("ALT"):
            continue
        val = str(r.get("copy", ""))
        if CJK.search(val):
            flags.append(f"P{n} ①[{r.get('slot')}] 含中文（①区只放上图的英文）：{val[:60]}")
        if INSTRUCTION.search(val):
            flags.append(f"P{n} ①[{r.get('slot')}] 疑似设计指令写进了上图文案：{val[:60]}")
        if STYLE_MARKUP.search(val):
            flags.append(f"P{n} ①[{r.get('slot')}] 含 ** 或 *…* 样式标记，会被当成要上图的星号；样式写进文字位名称：{val[:60]}")
    if len(text) > MAX_CHARS:
        flags.append(f"P{n} 备注 {len(text)} 字符，超过 Canva 上限 {MAX_CHARS}")
    has_star = any(CLAIM_STAR.search(str(r.get("copy", ""))) for r in rows)
    has_fda = any("Food and Drug Administration" in str(r.get("copy", "")) for r in rows)
    if has_star and not has_fda:
        warns.append(f"P{n} ①区有带 * 的句子，但没有 FDA 页脚行")
    if not rows:
        warns.append(f"P{n} ①区为空（主图或纯视觉页可忽略）")
    return flags, warns


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to a legacy code page
        stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("copy_json")
    ap.add_argument("--out", default="notes")
    ap.add_argument("--pages", help="e.g. 1-8 or 1,3,5")
    ap.add_argument("--before", help="notes_before.json (read-design presenter_notes output) for write_mode=archive")
    a = ap.parse_args()

    data = json.load(open(a.copy_json, encoding="utf-8"))
    canva = data.get("canva") or {}
    pages_meta = {int(p["page"]): p for p in canva.get("pages", [])}
    rows_by_page, issues_by_page = {}, {}
    for r in data.get("rows", []):
        if "page" in r:
            rows_by_page.setdefault(int(r["page"]), []).append(r)
    for it in data.get("issues", []):
        if "page" in it:
            issues_by_page.setdefault(int(it["page"]), []).append(it)

    wanted = parse_pages(a.pages)
    all_pages = sorted(set(pages_meta) | set(rows_by_page) | set(issues_by_page))
    if wanted:
        all_pages = [p for p in all_pages if p in wanted]
    if not all_pages:
        sys.exit("no pages found: add \"page\" to rows/issues or a canva.pages block")

    before = {}
    archive = canva.get("write_mode") == "archive"
    if archive:
        if not a.before:
            sys.exit("write_mode=archive needs --before notes_before.json")
        items = json.load(open(a.before, encoding="utf-8"))
        if isinstance(items, dict):  # read-design output saved verbatim
            items = items.get("presenter_notes", [])
        for item in items:
            before[int(item["page_number"])] = item.get("notes", "")

    os.makedirs(a.out, exist_ok=True)
    review_date = canva.get("review_date", "")
    manifest, bundle, flags, warns = [], [], [], []
    for n in all_pages:
        page = pages_meta.get(n, {"page": n})
        rows = rows_by_page.get(n, [])
        text, z1 = build_page(n, page, rows, issues_by_page.get(n, []), review_date,
                              before.get(n, "") if archive else None)
        f, w = lint(n, text, z1, rows)
        flags += f
        warns += w
        path = os.path.join(a.out, f"p{n}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        manifest.append({"page": n, "page_id": page.get("page_id", ""), "label": page.get("label", ""),
                         "path": os.path.abspath(path), "chars": len(text)})
        bundle.append(f"## P{n}\n\n```\n{text}```\n")

    title = canva.get("design_title", "")
    with open(os.path.join(a.out, "all_notes.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# {title} 备注（{len(all_pages)} 页）\n\n" + "\n".join(bundle))
    with open(os.path.join(a.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"design_id": canva.get("design_id", ""), "edit_url": canva.get("edit_url", ""),
                   "write_mode": canva.get("write_mode", "replace"), "pages": manifest},
                  fh, ensure_ascii=False, indent=2)

    for m in manifest:
        print(f"P{m['page']:<3} {m['chars']:>5} chars  {m['path']}")
    for w in warns:
        print("WARN ", w)
    for f in flags:
        print("FLAG ", f)
    print(f"saved {os.path.abspath(a.out)}  ({len(flags)} FLAG, {len(warns)} WARN)")
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
