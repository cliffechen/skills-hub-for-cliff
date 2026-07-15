#!/usr/bin/env python3
"""Fetch a Google Web Trends timeline through SerpApi.

The API key is read from an environment variable and is never written to disk.
Raw JSON and Google-Trends-compatible CSV files are saved for audit and analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ENDPOINT = "https://serpapi.com/search"
SENSITIVE_KEYS = {"api_key", "serpapi_key", "authorization"}


def redact_secrets(value):
    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact_secrets(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"([?&]api_key=)[^&]+", r"\1[REDACTED]", value, flags=re.IGNORECASE)
    return value


def fetch_timeline(api_key: str, keyword: str, geo: str, date: str) -> dict:
    params = {
        "engine": "google_trends",
        "q": keyword,
        "geo": geo,
        "date": date,
        "data_type": "TIMESERIES",
        "hl": "en",
        "api_key": api_key,
    }
    url = f"{ENDPOINT}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"SerpApi returned HTTP {exc.code}: {body[:500]}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"SerpApi request failed: {exc.reason}") from None

    if payload.get("error"):
        raise RuntimeError(f"SerpApi error: {payload['error']}")
    timeline = payload.get("interest_over_time", {}).get("timeline_data")
    if not isinstance(timeline, list) or not timeline:
        raise RuntimeError("SerpApi response does not contain an interest-over-time timeline")
    return payload


def write_csv(payload: dict, keyword: str, destination: Path) -> int:
    timeline = payload["interest_over_time"]["timeline_data"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Week", f"{keyword}: (United States)"])
        for point in timeline:
            values = point.get("values") or []
            if not values:
                continue
            value = values[0].get("extracted_value")
            if value is None:
                continue
            date = datetime.fromtimestamp(int(point["timestamp"]), tz=timezone.utc).date()
            writer.writerow([date.isoformat(), value])
    return len(timeline)


def save_payload(payload: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = redact_secrets(payload)
    destination.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="algae calcium")
    parser.add_argument("--geo", default="US")
    parser.add_argument("--date", default="today 5-y")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--api-key-env", default="SERPAPI_KEY")
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing environment variable: {args.api_key_env}")

    payload = fetch_timeline(api_key, args.keyword, args.geo, args.date)
    json_path = args.output_dir / "web_search_us_5y.serpapi.json"
    csv_path = args.output_dir / "web_search_us_5y.csv"
    save_payload(payload, json_path)
    point_count = write_csv(payload, args.keyword, csv_path)
    print(json.dumps({"view": "web_search", "points": point_count, "json": str(json_path), "csv": str(csv_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
