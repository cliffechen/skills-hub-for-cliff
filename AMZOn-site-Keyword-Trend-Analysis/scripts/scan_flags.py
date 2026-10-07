#!/usr/bin/env python3
"""Flag-only scan: write red flags (claim directions, brand words) into candidates[].flags.

Flags never change a candidate's verdict; they only warn that the direction is risky for copy/compliance.

Usage:
  python scan_flags.py <payload.json> [--brands a,b,c]

Claim directions come from the bundled references/blocked-claims-default.json; if it is missing,
falls back to amazon-preupload-check's copy (read-only). Matching is run on keyword + zh + demand/gap
text of each candidate.
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BLOCKED_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "blocked-claims-default.json"),
    os.path.expanduser("~/.claude/skills/amazon-preupload-check/references/blocked-claims-default.json"),
]

# Well-known supplement brands; extend with --brands. Lowercase.
BRANDS = [
    "nature made", "nature's bounty", "natures bounty", "centrum", "garden of life", "olly", "nordic naturals",
    "thorne", "pure encapsulations", "now foods", "solgar", "life extension", "optimum nutrition", "athletic greens",
    "ag1", "vitafusion", "goli", "sundown", "doctor's best", "doctors best", "jarrow", "swanson", "bluebonnet",
    "viactiv", "emergen-c", "airborne", "zarbee", "new chapter", "ritual", "seed", "momentous", "legion",
]


def load_directions():
    for p in BLOCKED_PATHS:
        try:
            return json.load(open(p, encoding="utf-8")).get("directions", {})
        except (OSError, ValueError):
            continue
    return {}


def main(path, extra_brands):
    data = json.load(open(path, encoding="utf-8"))
    directions = load_directions()
    if not directions:
        print("WARN: blocked-claims-default.json not readable; claim-direction flags skipped")
    brands = BRANDS + [b.strip().lower() for b in extra_brands if b.strip()]
    total = 0
    for c in data.get("candidates", []):
        text = " ".join(str(c.get(k, "")) for k in ("keyword", "zh", "demand", "gap")).lower()
        flags = [f for f in c.get("flags", []) if f.get("type", "").startswith("人工")]  # keep manual flags
        for key, d in directions.items():
            hits = []
            for p in d.get("patterns", []):
                p = p.replace("\x08", r"\b")  # source JSON stores one \b as a literal backspace char
                try:
                    m = re.search(p, text, re.I)
                except re.error:
                    continue
                if m:
                    hits.append(m.group(0))
            if hits:
                flags.append({"type": "功效方向-" + d.get("zh", key).split("（")[0],
                              "text": "命中：" + ", ".join(sorted(set(hits))[:6]) + "。此方向文案/合规风险高，仅提示，不影响趋势结论。"})
        for b in brands:
            if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", text):
                flags.append({"type": "品牌词", "text": f"含疑似品牌词「{b}」，作为关键词需求可参考，但不可作为自家 Listing 用词。"})
        c["flags"] = flags
        total += len(flags)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"flags written: {total} across {len(data.get('candidates', []))} candidates")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    brands = []
    if "--brands" in args:
        i = args.index("--brands")
        brands = args[i + 1].split(",")
        del args[i:i + 2]
    main(args[0], brands)
