#!/usr/bin/env python3
"""Analyze a Google Web Trends timeline CSV export."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev


def parse_value(value: str) -> int | None:
    cleaned = value.strip().replace("<", "")
    if not cleaned or not cleaned.isdigit():
        return None
    return int(cleaned)


def load_timeline(path: Path) -> tuple[str, list[tuple[datetime, int]]]:
    rows = list(csv.reader(path.open("r", encoding="utf-8-sig", newline="")))
    timeline_headers = {"week", "month", "day", "周", "月", "日"}
    header_index = next(
        (i for i, row in enumerate(rows) if row and row[0].strip().lower() in timeline_headers),
        None,
    )
    if header_index is None or len(rows[header_index]) < 2:
        raise ValueError(f"No Google Trends timeline header found in {path}")

    label = rows[header_index][1].strip()
    points: list[tuple[datetime, int]] = []
    for row in rows[header_index + 1 :]:
        if len(row) < 2:
            continue
        try:
            date = datetime.strptime(row[0].strip(), "%Y-%m-%d")
        except ValueError:
            continue
        value = parse_value(row[1])
        if value is not None:
            points.append((date, value))
    if len(points) < 26:
        raise ValueError(f"Too few timeline points in {path}: {len(points)}")
    return label, points


def slope(values: list[int]) -> float:
    if len(values) < 2:
        return 0.0
    x_mean = (len(values) - 1) / 2
    y_mean = mean(values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in enumerate(values))
    denominator = sum((x - x_mean) ** 2 for x in range(len(values)))
    return numerator / denominator if denominator else 0.0


def safe_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def classify_trend(recent_mean: float, previous_mean: float, recent_slope: float) -> str:
    change = safe_change(recent_mean, previous_mean)
    if change is None:
        return "insufficient_baseline"
    if change >= 15 and recent_slope >= -0.05:
        return "rising"
    if change <= -15 and recent_slope <= 0.05:
        return "falling"
    return "stable_or_mixed"


def analyze(path: Path, view: str) -> dict:
    label, points = load_timeline(path)
    values = [value for _, value in points]
    recent = values[-52:]
    previous = values[-104:-52]
    recent_13 = values[-13:]
    prior_year_13 = values[-65:-52]
    recent_mean = mean(recent)
    previous_mean = mean(previous) if previous else 0.0
    recent_slope = slope(recent)
    peak_date, peak_value = max(points, key=lambda point: point[1])
    zero_share = sum(value == 0 for value in recent) / len(recent)
    coefficient_of_variation = pstdev(recent) / recent_mean if recent_mean else math.inf

    return {
        "view": view,
        "series_label": label,
        "source_file": str(path),
        "definition": "Google Trends relative interest, normalized from 0 to 100 within this query",
        "point_count": len(points),
        "date_start": points[0][0].date().isoformat(),
        "date_end": points[-1][0].date().isoformat(),
        "recent_52w_mean": round(recent_mean, 2),
        "previous_52w_mean": round(previous_mean, 2),
        "year_over_year_change_pct": (
            round(safe_change(recent_mean, previous_mean), 2)
            if safe_change(recent_mean, previous_mean) is not None
            else None
        ),
        "recent_13w_mean": round(mean(recent_13), 2),
        "prior_year_same_13w_mean": round(mean(prior_year_13), 2) if prior_year_13 else None,
        "recent_13w_yoy_change_pct": (
            round(safe_change(mean(recent_13), mean(prior_year_13)), 2)
            if prior_year_13 and safe_change(mean(recent_13), mean(prior_year_13)) is not None
            else None
        ),
        "recent_52w_slope_per_week": round(recent_slope, 4),
        "recent_52w_zero_share": round(zero_share, 4),
        "recent_52w_coefficient_of_variation": (
            round(coefficient_of_variation, 4) if math.isfinite(coefficient_of_variation) else None
        ),
        "peak_week": peak_date.date().isoformat(),
        "peak_value": peak_value,
        "trend_classification": classify_trend(recent_mean, previous_mean, recent_slope),
        "caution": "Values are relative interest, not Amazon search volume; zero can mean insufficient relative interest.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "web_search": analyze(args.web, "web_search"),
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)


if __name__ == "__main__":
    main()
