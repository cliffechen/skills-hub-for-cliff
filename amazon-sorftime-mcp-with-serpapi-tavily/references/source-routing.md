# Source routing and fallback rules

## Routing table

| Evidence need | Primary | Fallback / cross-check | Required handling |
| --- | --- | --- | --- |
| Primary Amazon keyword, demand and drift | LLM candidates + Sorftime MCP + fixed local scorer | Mark missing after one corrected retry | Generate candidates, validate Top20, score deterministically, preserve brand/non-brand separation |
| Category and Top100 structure | Sorftime MCP | Mark unavailable | Preserve result scope and collection time |
| Product details and listing dates | Sorftime MCP | Mark unavailable | Keep ASIN and marketplace explicit |
| Negative reviews / Customers Say | Sorftime MCP | Expand the Sorftime competitor set | Target 100 informative negative reviews across five or more competitors |
| Google Web Trends | SerpApi `google_trends` endpoint | User-supplied Web Search CSV | Collect US Web Search only; never persist the API key |
| Off-Amazon science, regulation and demand context | Tavily MCP | Mark unavailable | Prefer primary/authoritative pages and independent domains |
| HTML report | Included renderer | Data Analytics report builder, if installed | The included renderer is the portable default |
| Feishu delivery | Included optional Feishu MCP | None | Inspect schema before appending one record |

## Failure sequence

1. Generate and classify semantic candidates without inventing metrics.
2. Check marketplace, spelling, required IDs, pagination, date range, and the live MCP tool schema.
3. Retry a failed Sorftime call once with corrected parameters.
4. Run the fixed primary-keyword scorer before full market collection.
5. For Google Web Trends, try SerpApi before accepting a user-supplied CSV.
6. Save source, timestamp, scope, raw file, failure reason, and fallback source.
7. If required selection evidence fails, store `null`, mark `missing`, and keep `VERIFY`.

## Google Trends contract

Use Web Search for the same exact seed keyword, US geography, and five-year range across runs.

Use the latest 52 weeks as the decision window and earlier years for direction and seasonality. Zero means insufficient relative interest in that slice, not proven zero demand.

When `SERPAPI_KEY` is available, run `scripts/fetch_serpapi_google_trends.py`. The script must issue exactly one Web Search request, save raw JSON without credentials, and produce the CSV expected by `scripts/analyze_google_trends.py`.

## Source-usage accounting

- Count each MCP tool call, external API request, and Web search interface invocation once.
- Keep wrapper/runtime calls such as shell execution, file edits, rendering, and validation out of data-source totals.
- Record tool/API names and counts even when calls are exploratory or fail.
- Report returned volume using meaningful units; do not add unlike units into one synthetic record total.
- If historical calls cannot be recovered from an audit log, use `null` and say `not recorded`; never infer a count from the final file alone.

## Tavily evidence grades

- High: regulator, official standard, peer-reviewed paper, official product/ingredient documentation.
- Medium: established trade source or transparent first-party survey.
- Low: commercial market-size landing page with unclear method, affiliate content, generic SEO page.

Low-authority pages may create validation questions but cannot independently upgrade a gate to `GO`.
