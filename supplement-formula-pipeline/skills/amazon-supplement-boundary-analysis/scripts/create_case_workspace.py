#!/usr/bin/env python
"""Create an isolated output workspace for one ASIN boundary-analysis case."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def slug(value: str, *, uppercase: bool = False) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    if uppercase:
        return cleaned.upper()
    return cleaned or "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asin", required=True, help="Anchored ASIN.")
    parser.add_argument("--core-ingredient", required=True, help="Short core ingredient name.")
    parser.add_argument("--timestamp", default=None, help="Timestamp in yyyyMMdd-HHmmss. Defaults to now.")
    parser.add_argument("--output-root", default=None, help="Defaults to <repo>/outputs/cases.")
    parser.add_argument("--sif-excel", default=None, help="Optional Sif Excel file to copy into inputs/.")
    parser.add_argument("--package-count", type=int, default=90, help="Default package count.")
    parser.add_argument("--dosage-form", default="softgels", help="capsules or softgels.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    asin = slug(args.asin, uppercase=True)
    ingredient = slug(args.core_ingredient)
    output_root = Path(args.output_root) if args.output_root else repo_root() / "outputs" / "cases"
    case_dir = output_root / f"{asin}-{ingredient}-{timestamp}"

    paths = {
        "case_dir": case_dir,
        "inputs": case_dir / "inputs",
        "sources": case_dir / "sources",
        "scratch": case_dir / "scratch",
        "deliverables": case_dir / "deliverables",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    copied_excel = None
    if args.sif_excel:
        source = Path(args.sif_excel).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"Sif Excel not found: {source}")
        copied_excel = paths["inputs"] / f"{asin.lower()}-sif-keyword-research{source.suffix}"
        shutil.copy2(source, copied_excel)

    config = {
        "asin": asin,
        "core_ingredient": args.core_ingredient,
        "timestamp": timestamp,
        "package_count": args.package_count,
        "dosage_form": args.dosage_form,
        "paths": {key: str(value) for key, value in paths.items()},
        "sif_excel": str(copied_excel) if copied_excel else None,
    }
    config_path = case_dir / "case_config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
