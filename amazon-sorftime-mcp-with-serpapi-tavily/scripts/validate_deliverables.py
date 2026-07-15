#!/usr/bin/env python3
"""Validate the stable, portable output set for one research run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


JSON_ARTIFACTS = (
    "raw/sorftime/keyword-selection-input.json",
    "raw/sorftime/keyword-drift-analysis.json",
    "raw/google-trends/analysis.json",
    "raw/tavily/retained-sources.json",
    "raw/source-usage.json",
    "data.json",
)
TEXT_ARTIFACTS = (
    "report.md",
    "html/report.html",
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the fixed output files produced by one research run."
    )
    parser.add_argument("run_dir", type=Path, help="research/<keyword>-<date> directory")
    args = parser.parse_args()

    errors: list[str] = []
    for relative_path in JSON_ARTIFACTS:
        path = args.run_dir / relative_path
        if not path.is_file():
            errors.append(f"missing required artifact: {relative_path}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON artifact {relative_path}: {exc}")

    for relative_path in TEXT_ARTIFACTS:
        path = args.run_dir / relative_path
        if not path.is_file():
            errors.append(f"missing required artifact: {relative_path}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty required artifact: {relative_path}")

    if errors:
        print("DELIVERABLES_INVALID")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("DELIVERABLES_VALID")


if __name__ == "__main__":
    main()
