# Research data contract

Use one `data.json` per research run. Unknown values must be `null`, never guessed values or empty strings.

## Fixed artifact set

Every run writes the same portable output shape, even when the final decision is `VERIFY`, `NO-GO`, or the run is `partial`:

```text
raw/sorftime/keyword-selection-input.json
raw/sorftime/keyword-drift-analysis.json
raw/google-trends/analysis.json
raw/tavily/retained-sources.json
raw/source-usage.json
data.json
report.md
html/report.html
```

For an unavailable provider, its fixed JSON file contains a non-sensitive status and missing reason. `data.json` remains the source of truth; the Markdown and HTML reports must repeat the same decision, confidence, primary keyword, handoff status, and source-usage totals.

## Top-level shape

```json
{
  "run": {
    "keyword": "user input / seed keyword",
    "primary_research_keyword": "selected Amazon keyword or null",
    "keyword_handoff": "boolean",
    "marketplace": "US",
    "started_at": "ISO-8601",
    "completed_at": "ISO-8601 or null",
    "methodology": "relative path",
    "status": "collecting | complete | partial"
  },
  "sources": [],
  "source_usage": {},
  "market_capacity": {},
  "competition": {},
  "differentiation": {},
  "decision": {},
  "missing_fields": [],
  "conflicts": []
}
```

## Source-usage object

Every completed run includes a non-sensitive tool-call overview:

```json
{
  "source_usage": {
    "generated_at": "ISO-8601",
    "scope": "data-source calls used during this research task",
    "raw_file": "raw/source-usage.json",
    "total_calls": 2,
    "source_count": 2,
    "headline_metrics": [
      {"label": "Google Web Trends 周度点", "value": 262, "unit": "个"}
    ],
    "tool_calls": [
      {"source": "SerpApi", "tool": "google_trends Web Search", "call_count": 1, "status": "observed", "notes": null},
      {"source": "Sorftime MCP", "tool": "keyword_extends", "call_count": 1, "status": "observed", "notes": "keyword-drift candidates"}
    ],
    "outputs": [
      {"source": "SerpApi", "metric": "Web weekly timeline points", "count": 262, "unit": "points", "notes": null}
    ]
  }
}
```

`total_calls` must equal the sum of `tool_calls[].call_count`. `source_count` must equal the number of distinct `tool_calls[].source` values. Do not sum heterogeneous output units. Unknown historical counts use `null` plus an explanatory note; they are never guessed.

## Evidence object

Every metric that affects a gate uses this structure:

```json
{
  "value": null,
  "unit": "string or null",
  "definition": "what was measured and over which product/time scope",
  "source": "sorftime | google_trends | tavily",
  "retrieved_at": "ISO-8601",
  "status": "observed | derived | missing | conflicting",
  "raw_file": "relative path or null",
  "notes": "string or null"
}
```

## Required market-capacity fields

- `primary_keyword_selection`
- `amazon_keyword_detail`
- `amazon_keyword_trend_12m`
- `keyword_drift_analysis`
- `google_trends_web_5y`
- `top10_monthly_units`
- `trend_classification`
- `seasonality_classification`
- `gate`

`primary_keyword_selection.value` must contain the deterministic output needed to audit the handoff:

```json
{
  "seed_keyword": "algae calcium",
  "primary_research_keyword": "algaecal",
  "keyword_handoff": true,
  "selection_status": "selected | insufficient_evidence",
  "selection_formula": "V × R × I × C × (0.85 + 0.15 × S)",
  "ranked_candidates": [],
  "terms": []
}
```

Each scored term records search volume, classification, hard-gate failures, listing and sales relevance, fixed purchase-intent weight, market coverage, sales-support multiplier, and final score. Keep excluded candidates in the array for audit. When no candidate passes the hard gates, store `primary_research_keyword=null`, mark the evidence `missing`, retain the seed only for exploration, and keep the market gate at `VERIFY`.

After a successful handoff, `amazon_keyword_detail`, `amazon_keyword_trend_12m`, `top10_monthly_units`, competition, and review evidence use the selected primary keyword as their main collection path. Preserve the original seed in `run.keyword` and the selection evidence.

## Required competition fields

- `top20_products`
- `new_listing_share_6m_top20`
- `sorftime_new_product_sales_share_3m_top100`
- `review_concentration_top3_top10`
- `brand_listing_concentration_top3_top20`
- `unit_concentration_top3_top10`
- `price_bands`
- `entry_position`
- `gate`

The Sorftime proxy fields do not replace the methodology fields. If product-level dates or units are absent, the methodology metric remains `missing`.

## Required differentiation fields

- `selected_competitors`
- `negative_review_sample_size`
- `complaint_clusters`
- `candidate_price_position`
- `product_improvements`
- `open_validation_questions`
- `gate`

## Decision object

```json
{
  "result": "GO | VERIFY | NO-GO",
  "confidence": "high | medium | low",
  "reason_codes": [],
  "summary": "string"
}
```

The overall result follows the weakest sufficiently evidenced gate. Any material missing field that could reverse the result changes the result to `VERIFY`.
