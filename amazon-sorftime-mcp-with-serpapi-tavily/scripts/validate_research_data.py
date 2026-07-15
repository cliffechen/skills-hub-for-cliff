#!/usr/bin/env python3
"""Validate the minimum structure and evidence discipline of a research data file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL = {
    "run",
    "sources",
    "source_usage",
    "market_capacity",
    "competition",
    "differentiation",
    "decision",
    "missing_fields",
    "conflicts",
}
REQUIRED_GATES = {
    "market_capacity": {
        "primary_keyword_selection",
        "amazon_keyword_detail",
        "amazon_keyword_trend_12m",
        "keyword_drift_analysis",
        "google_trends_web_5y",
        "top10_monthly_units",
        "trend_classification",
        "seasonality_classification",
        "gate",
    },
    "competition": {
        "top20_products",
        "new_listing_share_6m_top20",
        "sorftime_new_product_sales_share_3m_top100",
        "review_concentration_top3_top10",
        "brand_listing_concentration_top3_top20",
        "unit_concentration_top3_top10",
        "price_bands",
        "entry_position",
        "gate",
    },
    "differentiation": {
        "selected_competitors",
        "negative_review_sample_size",
        "complaint_clusters",
        "candidate_price_position",
        "product_improvements",
        "open_validation_questions",
        "gate",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.data_file.read_text(encoding="utf-8"))
    errors: list[str] = []

    missing_top = REQUIRED_TOP_LEVEL - set(data)
    if missing_top:
        errors.append(f"missing top-level fields: {sorted(missing_top)}")

    for section, required in REQUIRED_GATES.items():
        value = data.get(section)
        if not isinstance(value, dict):
            errors.append(f"{section} must be an object")
            continue
        missing = required - set(value)
        if missing:
            errors.append(f"{section} missing fields: {sorted(missing)}")

    run = data.get("run", {})
    if run.get("marketplace") != "US":
        errors.append("run.marketplace must be US")
    if not isinstance(run.get("keyword"), str) or not run.get("keyword", "").strip():
        errors.append("run.keyword must contain the user input keyword")
    primary_keyword = run.get("primary_research_keyword")
    if primary_keyword is not None and (
        not isinstance(primary_keyword, str) or not primary_keyword.strip()
    ):
        errors.append("run.primary_research_keyword must be a non-empty string or null")
    if not isinstance(run.get("keyword_handoff"), bool):
        errors.append("run.keyword_handoff must be a boolean")
    if run.get("keyword_handoff") and not primary_keyword:
        errors.append("run.keyword_handoff=true requires run.primary_research_keyword")

    market = data.get("market_capacity", {})
    selection_evidence = market.get("primary_keyword_selection", {})
    if isinstance(selection_evidence, dict):
        selection_value = selection_evidence.get("value")
        if selection_evidence.get("status") in {"observed", "derived"}:
            if not isinstance(selection_value, dict):
                errors.append("observed primary_keyword_selection.value must be an object")
            else:
                selected = selection_value.get("primary_research_keyword")
                if selected != primary_keyword:
                    errors.append(
                        "run.primary_research_keyword must match primary_keyword_selection.value"
                    )
                if selection_value.get("keyword_handoff") != run.get("keyword_handoff"):
                    errors.append(
                        "run.keyword_handoff must match primary_keyword_selection.value"
                    )

    decision = data.get("decision", {})
    if decision.get("result") not in {"GO", "VERIFY", "NO-GO"}:
        errors.append("decision.result must be GO, VERIFY, or NO-GO")
    if decision.get("confidence") not in {"high", "medium", "low"}:
        errors.append("decision.confidence must be high, medium, or low")

    usage = data.get("source_usage")
    if not isinstance(usage, dict):
        errors.append("source_usage must be an object")
    else:
        tool_calls = usage.get("tool_calls")
        if not isinstance(tool_calls, list):
            errors.append("source_usage.tool_calls must be an array")
            tool_calls = []
        calculated_total = 0
        distinct_sources: set[str] = set()
        for index, item in enumerate(tool_calls):
            if not isinstance(item, dict):
                errors.append(f"source_usage.tool_calls[{index}] must be an object")
                continue
            source = item.get("source")
            tool = item.get("tool")
            calls = item.get("call_count")
            if not isinstance(source, str) or not source.strip():
                errors.append(f"source_usage.tool_calls[{index}].source must be a non-empty string")
            else:
                distinct_sources.add(source)
            if not isinstance(tool, str) or not tool.strip():
                errors.append(f"source_usage.tool_calls[{index}].tool must be a non-empty string")
            if not isinstance(calls, int) or calls < 0:
                errors.append(f"source_usage.tool_calls[{index}].call_count must be a non-negative integer")
            else:
                calculated_total += calls

        if usage.get("total_calls") != calculated_total:
            errors.append(
                f"source_usage.total_calls must equal detailed call total {calculated_total}"
            )
        if usage.get("source_count") != len(distinct_sources):
            errors.append(
                f"source_usage.source_count must equal distinct source count {len(distinct_sources)}"
            )
        if not isinstance(usage.get("outputs"), list):
            errors.append("source_usage.outputs must be an array")

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("VALID")


if __name__ == "__main__":
    main()
