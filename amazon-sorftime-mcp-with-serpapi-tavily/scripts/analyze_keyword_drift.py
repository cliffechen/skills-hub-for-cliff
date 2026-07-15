#!/usr/bin/env python3
"""Score Amazon keyword candidates and detect keyword drift from Sorftime evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from statistics import mean


PURCHASE_INTENT_WEIGHTS = {
    "brand_product": 1.00,
    "brand_root": 0.95,
    "brand_variant": 0.90,
    "exact_product_category": 0.90,
    "generic_core": 0.80,
    "generic_synonym_source": 0.80,
    "benefit_formulation": 0.70,
    "broad_product": 0.55,
    "informational": 0.35,
    "noise": 0.00,
}

SCOPE_CAPS = {
    "generic_core": 1.00,
    "generic_synonym_source": 1.00,
    "exact_product_category": 1.00,
    "brand_root": 0.90,
    "brand_variant": 0.85,
    "benefit_formulation": 0.75,
    "brand_product": 0.60,
    "broad_product": 0.55,
    "informational": 0.30,
    "noise": 0.00,
}

MIN_LISTING_RELEVANCE = 0.70
MIN_STRICT_RELEVANT_COUNT = 10
MIN_PURCHASE_INTENT = 0.70
MIN_SEED_OVERLAP = 0.40
MIN_CONCEPT_RELEVANCE = 0.80


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def ratio(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return clamp(float(numerator) / float(denominator))


def pct_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round((current / previous - 1) * 100, 2)


def trend_metrics(previous: list[int], current: list[int]) -> dict:
    previous_mean = mean(previous) if previous else 0.0
    current_mean = mean(current) if current else 0.0
    first_half = mean(current[:6]) if len(current) >= 6 else 0.0
    second_half = mean(current[-6:]) if len(current) >= 6 else 0.0
    return {
        "previous_12m_mean": round(previous_mean, 2) if previous else None,
        "latest_12m_mean": round(current_mean, 2) if current else None,
        "year_over_year_change_pct": (
            pct_change(current_mean, previous_mean) if previous and current else None
        ),
        "latest_6m_vs_prior_6m_pct": (
            pct_change(second_half, first_half) if len(current) >= 12 else None
        ),
    }


def string_set(value) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def overlap_metrics(seed_asins: list[str], candidate_asins: list[str]) -> dict | None:
    if not seed_asins or not candidate_asins:
        return None
    left, right = set(seed_asins), set(candidate_asins)
    shared = left & right
    union = left | right
    return {
        "shared_asins": sorted(shared),
        "shared_count": len(shared),
        "overlap_coefficient_pct": round(len(shared) / min(len(left), len(right)) * 100, 2),
        "jaccard_pct": round(len(shared) / len(union) * 100, 2),
    }


def strict_result_summary(item: dict) -> dict:
    results = item.get("top_results") if isinstance(item.get("top_results"), list) else []
    top_asins = item.get("top_asins") or [row.get("asin") for row in results if row.get("asin")]
    strict_rows = [row for row in results if row.get("strict_relevant") is True]
    strict_asins = string_set(item.get("strict_relevant_asins")) or {
        str(row.get("asin")) for row in strict_rows if row.get("asin")
    }
    strict_brands = string_set(item.get("strict_relevant_brands")) or {
        str(row.get("brand")) for row in strict_rows if row.get("brand")
    }
    strict_forms = string_set(item.get("strict_relevant_forms")) or {
        str(row.get("form")) for row in strict_rows if row.get("form")
    }

    total_count = item.get("top20_total_count")
    if total_count is None:
        total_count = len(results) or len(top_asins)
    strict_count = item.get("strict_relevant_count")
    if strict_count is None:
        strict_count = len(strict_rows) or len(strict_asins)

    total_units = item.get("top20_total_monthly_units")
    if total_units is None and results:
        units = [row.get("monthly_units") for row in results]
        if all(isinstance(value, (int, float)) for value in units):
            total_units = sum(units)
    strict_units = item.get("strict_relevant_monthly_units")
    if strict_units is None and strict_rows:
        units = [row.get("monthly_units") for row in strict_rows]
        if all(isinstance(value, (int, float)) for value in units):
            strict_units = sum(units)

    return {
        "top_asins": [str(value) for value in top_asins if value],
        "strict_asins": strict_asins,
        "strict_brands": strict_brands,
        "strict_forms": strict_forms,
        "total_count": int(total_count or 0),
        "strict_count": int(strict_count or 0),
        "total_units": total_units,
        "strict_units": strict_units,
    }


def universe_counts(payload: dict, summaries: list[dict]) -> dict:
    configured = payload.get("reference_universe") or {}
    asins = string_set(configured.get("asins"))
    brands = string_set(configured.get("brands"))
    forms = string_set(configured.get("forms"))
    if not asins:
        asins = set().union(*(item["strict_asins"] for item in summaries))
    if not brands:
        brands = set().union(*(item["strict_brands"] for item in summaries))
    if not forms:
        forms = set().union(*(item["strict_forms"] for item in summaries))
    return {
        "asin_count": int(configured.get("asin_count") or len(asins)),
        "brand_count": int(configured.get("brand_count") or len(brands)),
        "form_count": int(configured.get("form_count") or len(forms)),
    }


def market_coverage(item: dict, summary: dict, universe: dict) -> dict | None:
    explicit = item.get("market_coverage_raw")
    if explicit is not None:
        raw = clamp(float(explicit))
        components = {"asin": None, "brand": None, "form": None}
    else:
        strict_count = summary["strict_count"]
        asin_denominator = min(20, universe["asin_count"]) if universe["asin_count"] else 0
        brand_count = item.get("strict_relevant_brand_count")
        if brand_count is None:
            brand_count = len(summary["strict_brands"])
        form_count = item.get("strict_relevant_form_count")
        if form_count is None:
            form_count = len(summary["strict_forms"])
        brand_denominator = min(10, universe["brand_count"]) if universe["brand_count"] else 0
        form_denominator = universe["form_count"]
        asin_component = ratio(strict_count, asin_denominator)
        brand_component = ratio(brand_count, brand_denominator)
        form_component = ratio(form_count, form_denominator)
        if None in (asin_component, brand_component, form_component):
            return None
        raw = 0.60 * asin_component + 0.30 * brand_component + 0.10 * form_component
        components = {
            "asin": round(asin_component, 4),
            "brand": round(brand_component, 4),
            "form": round(form_component, 4),
        }
    cap = SCOPE_CAPS.get(item.get("classification"), 0.0)
    return {
        "components": components,
        "raw": round(raw, 4),
        "scope_cap": cap,
        "final": round(raw * cap, 4),
    }


def percentile_ranks(values: list[float]) -> dict[float, float]:
    unique = sorted(set(values))
    if not unique:
        return {}
    if len(unique) == 1:
        return {unique[0]: 1.0}
    return {value: index / (len(unique) - 1) for index, value in enumerate(unique)}


def analyze(payload: dict) -> dict:
    seed = payload["seed_keyword"]
    terms = payload["terms"]
    seed_term = next(item for item in terms if item["keyword"] == seed)
    summaries = [strict_result_summary(item) for item in terms]
    seed_asins = summaries[terms.index(seed_term)]["top_asins"]
    universe = universe_counts(payload, summaries)

    analyzed = []
    for item, summary in zip(terms, summaries):
        classification = item["classification"]
        volume = item.get("current_monthly_search_volume")
        listing_relevance = ratio(summary["strict_count"], summary["total_count"])
        sales_relevance = ratio(summary["strict_units"], summary["total_units"])
        if listing_relevance is None:
            strict_relevance = None
            relevance_formula = "missing"
        elif sales_relevance is None:
            strict_relevance = listing_relevance
            relevance_formula = "listing_only"
        else:
            strict_relevance = 0.70 * listing_relevance + 0.30 * sales_relevance
            relevance_formula = "listing_70_sales_30"

        overlap = None
        if item["keyword"] != seed:
            overlap = overlap_metrics(seed_asins, summary["top_asins"])
        overlap_rate = (
            overlap["overlap_coefficient_pct"] / 100 if overlap else (1.0 if item["keyword"] == seed else None)
        )
        intent = PURCHASE_INTENT_WEIGHTS.get(classification, 0.0)
        coverage = market_coverage(item, summary, universe)

        failures = []
        if not isinstance(volume, (int, float)) or volume <= 0:
            failures.append("missing_search_volume")
        if listing_relevance is None or listing_relevance < MIN_LISTING_RELEVANCE:
            failures.append("listing_relevance_below_70pct")
        if summary["strict_count"] < MIN_STRICT_RELEVANT_COUNT:
            failures.append("fewer_than_10_strict_results")
        if intent < MIN_PURCHASE_INTENT:
            failures.append("purchase_intent_below_0_70")
        concept_relevance = listing_relevance or 0.0
        if (overlap_rate or 0.0) < MIN_SEED_OVERLAP and concept_relevance < MIN_CONCEPT_RELEVANCE:
            failures.append("insufficient_seed_overlap_or_concept_relevance")
        if strict_relevance is None:
            failures.append("missing_strict_relevance")
        if coverage is None:
            failures.append("missing_market_coverage")

        row = {
            "keyword": item["keyword"],
            "classification": classification,
            "current_monthly_search_volume": volume,
            **trend_metrics(item.get("previous_12m") or [], item.get("latest_12m") or []),
            "seed_result_overlap": overlap,
            "scoring": {
                "listing_relevance_rate": round(listing_relevance, 4) if listing_relevance is not None else None,
                "sales_relevance_rate": round(sales_relevance, 4) if sales_relevance is not None else None,
                "strict_relevance_rate": round(strict_relevance, 4) if strict_relevance is not None else None,
                "strict_relevance_formula": relevance_formula,
                "strict_relevant_count": summary["strict_count"],
                "purchase_intent_weight": intent,
                "market_coverage": coverage,
                "strict_relevant_monthly_units": summary["strict_units"],
                "eligibility_failures": failures,
                "eligible": not failures,
            },
        }
        analyzed.append(row)

    eligible_with_sales = [
        item["scoring"]["strict_relevant_monthly_units"]
        for item in analyzed
        if item["scoring"]["eligible"]
        and isinstance(item["scoring"]["strict_relevant_monthly_units"], (int, float))
    ]
    sales_ranks = percentile_ranks(eligible_with_sales)

    for item in analyzed:
        scoring = item["scoring"]
        if not scoring["eligible"]:
            scoring.update({"sales_support_percentile": None, "sales_multiplier": None, "primary_keyword_score": None})
            continue
        strict_units = scoring["strict_relevant_monthly_units"]
        if isinstance(strict_units, (int, float)) and strict_units in sales_ranks:
            support = sales_ranks[strict_units]
            sales_multiplier = 0.85 + 0.15 * support
        else:
            support = None
            sales_multiplier = 1.0
        score = (
            float(item["current_monthly_search_volume"])
            * scoring["strict_relevance_rate"]
            * scoring["purchase_intent_weight"]
            * scoring["market_coverage"]["final"]
            * sales_multiplier
        )
        scoring.update(
            {
                "sales_support_percentile": round(support, 4) if support is not None else None,
                "sales_multiplier": round(sales_multiplier, 4),
                "primary_keyword_score": round(score, 2),
            }
        )

    ranked = sorted(
        (item for item in analyzed if item["scoring"]["primary_keyword_score"] is not None),
        key=lambda item: item["scoring"]["primary_keyword_score"],
        reverse=True,
    )
    primary = ranked[0]["keyword"] if ranked else None

    brand_root = next((item for item in analyzed if item["classification"] == "brand_root"), None)
    seed_volume = seed_term.get("current_monthly_search_volume") or 0
    brand_ratio = None
    if brand_root and seed_volume and brand_root.get("current_monthly_search_volume"):
        brand_ratio = round(brand_root["current_monthly_search_volume"] / seed_volume, 2)

    rising_brand_terms = [
        item["keyword"]
        for item in analyzed
        if item["classification"].startswith("brand_")
        and (item.get("year_over_year_change_pct") or 0) >= 15
    ]
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "seed_keyword": seed,
        "primary_research_keyword": primary,
        "keyword_handoff": bool(primary and primary != seed),
        "selection_status": "selected" if primary else "insufficient_evidence",
        "selection_formula": "V × R × I × C × (0.85 + 0.15 × S)",
        "selection_config": {
            "hard_gates": {
                "minimum_listing_relevance": MIN_LISTING_RELEVANCE,
                "minimum_strict_relevant_count": MIN_STRICT_RELEVANT_COUNT,
                "minimum_purchase_intent": MIN_PURCHASE_INTENT,
                "minimum_seed_overlap_or_concept_relevance": [MIN_SEED_OVERLAP, MIN_CONCEPT_RELEVANCE],
            },
            "strict_relevance_weights": {"listing": 0.70, "sales": 0.30},
            "coverage_weights": {"asin": 0.60, "brand": 0.30, "form": 0.10},
            "purchase_intent_weights": PURCHASE_INTENT_WEIGHTS,
            "scope_caps": SCOPE_CAPS,
            "sales_support_max_effect": 0.15,
        },
        "reference_universe_counts": universe,
        "ranked_candidates": [
            {
                "rank": index,
                "keyword": item["keyword"],
                "classification": item["classification"],
                "primary_keyword_score": item["scoring"]["primary_keyword_score"],
            }
            for index, item in enumerate(ranked, start=1)
        ],
        "definition": "The input term is a seed. The primary Amazon research keyword is selected by fixed relevance, intent, coverage, and sales-support rules after Sorftime validation.",
        "terms": analyzed,
        "brand_root_to_seed_volume_ratio": brand_ratio,
        "rising_brand_family_terms": rising_brand_terms,
        "classification": (
            "brand_family_keyword_drift_confirmed"
            if len(rising_brand_terms) >= 2
            else "keyword_drift_not_confirmed"
        ),
        "decision_rule": "Use the selected primary keyword for the main Amazon research workflow. Keep branded and non-branded demand separate; branded volumes are not generic addressable demand.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input_file.read_text(encoding="utf-8"))
    result = analyze(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {args.output.resolve()}")


if __name__ == "__main__":
    main()
