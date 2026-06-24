#!/usr/bin/env python
"""Fail if Chinese formal deliverables still contain English template scaffolding."""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = [
    r"\bExecutive Summary\b",
    r"\bInput Snapshot\b",
    r"\bProduct & Traffic Baseline\b",
    r"\bKeyword Boundary Map\b",
    r"\bObserved Ingredient Table\b",
    r"\bIngredient Classification\b",
    r"\bRisk Matrix\b",
    r"\bMissing Evidence Points\b",
    r"\bRebuild Posture Summary\b",
    r"\|\s*ingredient_name\s*\|",
    r"\|\s*ingredient_name_or_claim\s*\|",
    r"\|\s*alias\s*\|\s*source_or_form\s*\|",
    r"\|\s*dosage_if_visible\s*\|",
    r"\|\s*claim_link\s*\|",
    r"\|\s*category\s*\|\s*why\s*\|",
    r"\|\s*TM_risk\s*\|",
    r"\|\s*patent_risk\s*\|",
    r"\|\s*compliance_risk\s*\|",
    r"\|\s*marketplace_risk\s*\|",
    r"\|\s*question\s*\|\s*why_it_matters\s*\|",
    r"\|\s*best_next_document_or_source\s*\|",
    r"\|\s*item\s*\|\s*posture\s*\|\s*rationale\s*\|",
    r"\|\s*generic\s*\|",
    r"\|\s*branded\s*\|",
    r"\|\s*likely proprietary\s*\|",
    r"\|\s*unclear\s*\|",
    r"\|\s*keep concept\s*\|",
    r"\|\s*legal review\s*\|",
    r"\|\s*avoid\s*\|",
    r"\|\s*replace\s*\|",
    r"\bHero ingredient\b",
    r"\bCore function and traffic anchor\b",
    r"\bSupport or experience upgrade\b",
    r"\bfinal direction name\b",
    r"\binherited core audience\b",
    r"\bmain star ingredient\b",
    r"\bsatellite selling points\b",
    r"\bProduct concept name\b",
    r"\bTarget market and channel\b",
    r"\bDoes the formula still center the hero ingredient\b",
    r"\bDo satellites explain or support the hero\b",
    r"\bAre label amounts plausible\b",
    r"\bAre forms suitable for the intended role\b",
    r"\bAre any ingredients ornamental\b",
    r"\bAny sensitivity, interaction, UL, or population flags\b",
]


def expand_paths(values: list[str]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        matches = glob.glob(value)
        if matches:
            paths.extend(Path(match) for match in matches)
        else:
            paths.append(Path(value))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Markdown deliverables or glob patterns to validate.")
    args = parser.parse_args()

    patterns = [re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_PATTERNS]
    failures: list[str] = []
    for path in expand_paths(args.paths):
        if not path.exists():
            failures.append(f"{path}: file not found")
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                if pattern.search(line):
                    failures.append(f"{path}:{line_number}: {line.strip()}")
                    break

    if failures:
        print("Chinese deliverable validation failed. Translate these template remnants:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Chinese deliverable validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
