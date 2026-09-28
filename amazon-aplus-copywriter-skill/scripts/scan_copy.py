#!/usr/bin/env python3
"""Scan copy JSON (same format as build_xlsx.py) for compliance and conflict problems.

Usage:
  python3 scan_copy.py copy.json [--forbid "1000mg,softgel,OldBrand"] [--supplement] [--listing] [--max-over 10]

Checks the "copy" and "alt" fields of every row:
  - --forbid terms (this run's conflict list: wrong dose, wrong dosage form, placeholder brand, benchmark brand)
  - --supplement: high-risk supplement claim words; claim asterisks need an FDA disclaimer row
  - --listing: gallery images (主图/副图). Headline-like slots (slot contains 标题) over 45 chars or 2 lines
    get a WARN; any Chinese character left in copy is a FLAG (placeholder not replaced)
  - ALT rows (id starts with "ALT") longer than 100 characters
  - copy much longer than the placeholder (> --max-over characters)
Exit code 1 if any FLAG was found, else 0. WARN items are informational.
"""
import argparse
import json
import re
import sys

SUPPLEMENT_RISK = [
    r"\bcure[sd]?\b", r"\btreat(s|ment)?\b", r"\bprevent(s|ion)?\b", r"\bheal(s|ing)?\b", r"\bdiagnos",
    r"anti-?aging", r"revers(e|es|ing) aging", r"guarantee", r"\binstant(ly)?\b", r"works for everyone",
    r"#1\b", r"\bbest\b", r"most effective", r"strongest", r"100%", r"\d+x (better|more)",
    r"fda[- ]approved", r"clinically proven", r"doctor recommended", r"made in (the )?usa",
]
FDA_MARK = "not intended to diagnose"
DISCLAIMER_EXEMPT = re.compile(r"not been evaluated by the food and drug administration", re.I)


def claim_star(text):
    """True if text carries a structure/function asterisk (not just **bold** markup)."""
    stripped = re.sub(r"\*\*[^*]+\*\*", "", text)       # remove **bold**
    stripped = re.sub(r"\*[^*\n]+\*", "", stripped)     # remove *accent*
    return "*" in stripped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--forbid", default="")
    ap.add_argument("--supplement", action="store_true")
    ap.add_argument("--listing", action="store_true")
    ap.add_argument("--max-over", type=int, default=10)
    a = ap.parse_args()

    rows = json.load(open(a.json, encoding="utf-8"))["rows"]
    forbid = [t.strip() for t in a.forbid.split(",") if t.strip()]
    flags, warns = [], []
    has_fda = any(FDA_MARK in (r.get("copy") or "").lower() for r in rows)
    star_rows = []
    cjk = re.compile(r"[一-鿿]")

    for r in rows:
        rid = r.get("id", "?")
        for field in ("copy", "alt"):
            t = r.get(field) or ""
            if not t or t == "—":
                continue
            if DISCLAIMER_EXEMPT.search(t):
                continue
            low = t.lower()
            for term in forbid:
                if term.lower() in low:
                    flags.append(f"{rid} [{field}] contains forbidden term '{term}': {t!r}")
            if a.supplement:
                for pat in SUPPLEMENT_RISK:
                    if re.search(pat, low):
                        warns.append(f"{rid} [{field}] high-risk wording /{pat}/: {t!r}")
            if a.listing and field == "copy" and cjk.search(t):
                flags.append(f"{rid} [copy] still contains Chinese characters (placeholder not replaced?): {t!r}")
            if a.listing and field == "copy" and "标题" in (r.get("slot") or ""):
                plain = re.sub(r"\*", "", t)
                if len(plain) > 45 or plain.count("\n") > 1:
                    warns.append(f"{rid} headline is {len(plain)} chars / {plain.count(chr(10))+1} lines - long for a 1600px gallery thumbnail")
            if field == "copy" and claim_star(t):
                star_rows.append(rid)
        copy = r.get("copy") or ""
        if rid.upper().startswith("ALT") and len(copy) > 100:
            flags.append(f"{rid} alt text is {len(copy)} chars (>100)")
        ph = r.get("placeholder") or ""
        if ph and ph != "—" and not ph.startswith("（") and not rid.upper().startswith("ALT"):
            over = len(copy) - len(ph)
            if over > a.max_over:
                warns.append(f"{rid} copy is {over} chars longer than placeholder ({len(copy)} vs {len(ph)}) - check fit or offer shorter alt")

    if a.supplement and star_rows and not has_fda:
        flags.append(f"claim asterisks in {star_rows} but no FDA disclaimer row found")

    print(f"rows scanned: {len(rows)} | claim-asterisk rows: {star_rows} | FDA disclaimer present: {has_fda}")
    for f in flags:
        print("FLAG ", f)
    for w in warns:
        print("WARN ", w)
    if not flags:
        print("OK: no FLAG items")
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
