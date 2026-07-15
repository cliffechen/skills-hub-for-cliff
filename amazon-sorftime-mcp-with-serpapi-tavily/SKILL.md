---
name: amazon-sorftime-mcp-with-serpapi-tavily
description: Research Amazon US product-selection opportunities from a seed keyword, product idea, category, or ASIN using Sorftime MCP as the primary Amazon data source, SerpApi for Google Web Trends, and Tavily for independent off-Amazon validation. Use when Codex must generate semantic keyword candidates, validate Amazon demand and result relevance, automatically hand research off to the highest-scoring consumer-path keyword, detect generic/synonym/brand/misspelling drift, produce auditable data.json plus Markdown and visual HTML reports with source-call statistics, analyze market capacity/competition/reviews/differentiation, optionally deliver to Feishu Bitable, or verify the stack. Exclude profit, margin, ROI, sourcing-cost, advertising-cost, and other financial viability calculations.
---

# Amazon Sorftime + SerpApi + Tavily Research

## Non-negotiable scope

- Default to Amazon US unless the user explicitly selects another marketplace.
- Evaluate market capacity, competition, and differentiation in that order.
- Never add profit, margin, ROI, sourcing-cost, advertising-cost, break-even, or financial-score sections.
- Return `GO`, `VERIFY`, or `NO-GO`; do not hide missing evidence inside a weighted score.
- Keep evidence definitions separate when Sorftime and the methodology measure different scopes.
- Include a data-source usage overview in every completed Markdown and HTML report.

## Load references progressively

1. Read [methodology.md](references/methodology.md) for every research run.
2. Read [source-routing.md](references/source-routing.md) before collecting evidence.
3. Read [data-contract.md](references/data-contract.md) before writing `data.json`.
4. Read [sorftime-tool-map.md](references/sorftime-tool-map.md) before the first Sorftime call, or whenever tool parameters fail.
5. Read [keyword-drift.md](references/keyword-drift.md) whenever the seed term may not represent the whole query family, especially in supplements.
6. Read [report-visual-spec.md](references/report-visual-spec.md) before generating HTML.
7. Read [feishu-output.md](references/feishu-output.md) only when the user requests Feishu delivery.

## Preflight

Run this from the installed skill folder or pass the folder explicitly:

```powershell
python scripts/preflight.py
```

Treat missing Sorftime as a core blocker. Tavily or SerpApi failures reduce confidence and can force `VERIFY`. Feishu is optional unless delivery was requested.

## Research workspace

Create all runtime files outside the installed skill:

```text
research/<keyword-slug>-<YYYYMMDD>/
├── raw/
│   ├── sorftime/
│   ├── google-trends/
│   ├── tavily/
│   └── source-usage.json
├── data.json
├── report.md
└── html/
    └── report.html
```

Never store API keys, cookies, browser profiles, access tokens, or live `.env` files in the research folder or skill folder.

Maintain `raw/source-usage.json` throughout the run. Record only provider names, tool/API names, call counts, outcomes, and non-sensitive return-size metrics. Never record keys, cookies, authorization headers, full request URLs containing credentials, or private payloads.

## Fixed deliverables

Every run, including a `partial` or `VERIFY` run, MUST produce the following stable file set. If a source is unavailable, write its status, missing reason, and any attempted-call metadata instead of omitting the artifact or inventing data.

```text
research/<keyword-slug>-<YYYYMMDD>/
├── raw/
│   ├── sorftime/
│   │   ├── keyword-selection-input.json
│   │   └── keyword-drift-analysis.json
│   ├── google-trends/
│   │   └── analysis.json
│   ├── tavily/
│   │   └── retained-sources.json
│   └── source-usage.json
├── data.json
├── report.md
└── html/
    └── report.html
```

`data.json` is the machine-readable source of truth. `report.md` and `html/report.html` are two synchronized views of that same validated data, with the same decision, confidence, primary keyword, keyword-handoff status, and **数据源统计** totals.

## Required workflow

### 1. Define the research target

- Confirm the seed keyword or ASIN, marketplace, and intended product concept.
- Resolve ambiguous category scope before treating broad-category data as niche evidence.
- Record start time, user input keyword, product-concept boundary, marketplace, and methodology path in `data.json`.

### 2. Select the primary Amazon research keyword first

- Use the LLM to generate 15-25 semantic candidates across generic, source, product-category, benefit/formulation, brand, brand-product, variant, and broad terms.
- Add Sorftime `keyword_extends` candidates, lowercase and deduplicate, and keep at most 30.
- Call `keyword_detail` for the candidate pool, then retain the seed plus the 5-8 highest-volume semantically plausible candidates.
- Call `keyword_search_results` for the shortlist and label each Top20 product as strictly relevant or not. Record ASIN, brand, form, monthly units, and seed overlap.
- Normalize the evidence into `raw/sorftime/keyword-selection-input.json`. Run `scripts/analyze_keyword_drift.py` and save `raw/sorftime/keyword-drift-analysis.json`.
- Accept only the script-selected `primary_research_keyword`; never let the LLM change coefficients or choose a winner outside the fixed rules in [keyword-drift.md](references/keyword-drift.md).
- If the winner differs from the seed but remains within the same product concept, continue automatically and record `keyword_handoff=true`. Ask only when the winning term changes the product category or intended product concept.
- If no candidate passes the hard gates, retain the seed for exploration, mark selection `insufficient_evidence`, and keep the market gate at `VERIFY`.

### 3. Collect full Sorftime evidence using the selected primary keyword

- Use the primary keyword for category discovery, Top100/category structure, keyword demand and trend, Top20 products, product details, listing dates, monthly units, reviews, brands, and negative reviews.
- Query `keyword_trend` for the primary keyword and the 2-3 highest-scoring auxiliary terms, then rerun the keyword analysis with trend evidence.
- Save decision-driving responses or normalized extracts under `raw/sorftime/`.
- Retry one failed call after checking the live tool schema and parameters. Do not reuse stale parameter names when the exposed MCP schema differs.
- Increment the source-usage ledger after every Sorftime call, including candidate discovery, exploratory, and failed calls.
- Analyze the non-brand basket and brand family separately. Never add branded search volumes to generic addressable demand or treat their ratio as market share.

### 4. Validate Google Web Trends with SerpApi

- Collect US Web Search for the selected primary keyword over a five-year range.
- Prefer SerpApi when `SERPAPI_KEY` is available. Read the key from the environment only; never pass it in report text, save it in raw responses, or print it in logs.
- Run:

```powershell
python scripts/fetch_serpapi_google_trends.py `
  --keyword "<primary research keyword>" `
  --geo US `
  --date "today 5-y" `
  --output-dir research/<run>/raw/google-trends
```

- The fetcher makes exactly one Web Search request and saves redaction-safe raw JSON plus a compatible CSV export.
- If SerpApi is unavailable or fails, accept a user-supplied Web Search CSV. Record the attempted source and failure reason without hiding the fallback.
- Save the CSV as `raw/google-trends/web_search_us_5y.csv`.
- Run:

```powershell
python scripts/analyze_google_trends.py `
  --web raw/google-trends/web_search_us_5y.csv `
  --output raw/google-trends/analysis.json
```

- Treat the 0–100 index as relative interest, never Amazon search volume.
- Compare Google Web direction with the accepted Amazon keyword basket; retain the original seed as context when keyword handoff occurred.
- Record the SerpApi request count and returned Web timeline-point count.

### 5. Cross-check with Tavily

- Use Tavily to discover authoritative off-Amazon sources, then read selected sources.
- Prefer regulators, academic papers, official brand/ingredient documentation, and established trade sources.
- Cross-check material claims across independent domains where practical.
- Do not promote generic commercial market-size pages into high-confidence demand evidence.
- Record Tavily search and extraction calls separately; count only retained sources in the output summary.

### 6. Evaluate the three gates

**Market capacity**

- Classify the primary-keyword direction, seed-to-primary handoff, keyword-family drift, and seasonality.
- Keep generic/synonym demand separate from branded demand; brand growth can confirm query migration while increasing brand-capture risk.
- Compare Top10 monthly units across ranks 1, 3, 5, and 10.
- Apply the joint rejection rule only when both six-month decline and weak head-product units are evidenced.

**Competition**

- Calculate six-month new-listing share, review concentration, brand listing concentration, unit concentration, and price-band structure from a consistent set.
- Keep Sorftime three-month or Top100 proxies separate from methodology metrics.
- State a concrete entry position; do not stop at low/medium/high competition.

**Differentiation**

- Select five representative competitors.
- Target at least 20 informative negative reviews per competitor and 100 total.
- Cluster repeated product complaints across competitors; separate logistics-only noise.
- Convert only repeated, material, feasible issues into product improvements and validation questions.

### 7. Validate and report

Write `data.json`, then run:

```powershell
python scripts/validate_research_data.py research/<run>/data.json
```

Write `report.md` from validated evidence. Lead with decision and confidence, then show `用户输入词 → 主调研词`, the scoring table and handoff reason, the three gates, evidence conflicts, missing data, differentiation opportunities, and next actions.

Add a **数据源统计** section to both Markdown and HTML. Show:

- total data-source calls and number of providers;
- each provider's tool/API names and call counts;
- known successful, failed, or mixed status without guessing;
- returned data volume by meaningful unit, such as products, reviews, sources, search queries, or weekly trend points;
- a note when historical return counts were not recorded.

Generate the portable HTML without external libraries:

```powershell
python scripts/render_report.py `
  research/<run>/data.json `
  --output research/<run>/html/report.html
```

Then verify the fixed deliverable contract:

```powershell
python scripts/validate_deliverables.py research/<run>
```

Open the HTML and check desktop and mobile widths. Preserve the navy background, white cards, royal-blue headers, KPI cards, evidence tables, charts, audit callouts, and action cards defined in the visual specification.

### 8. Deliver to Feishu when requested

- Require the complete Bitable link, preferably including `table=tbl...`.
- Inspect the real table schema before writing.
- Append one structured summary record; never create or rename columns silently.
- If an attachment column exists, upload `report.html` and attach it to the same record.
- If the target or schema is missing, finish all local artifacts and ask only for the Bitable link.

## Decision discipline

- `GO`: all three gates have sufficient evidence and no material red flag.
- `VERIFY`: evidence is missing, conflicting, definition-mismatched, strongly seasonal, or differentiation is not yet validated.
- `NO-GO`: a gate rejection rule is met or no credible entry position exists.
- A later gate cannot cancel a failed earlier gate.
- Missing evidence is never favorable evidence.

## Completion checklist

- Raw sources and retrieval dates saved.
- Sorftime metric scopes are explicit.
- Candidate generation includes LLM semantic expansion and Sorftime extensions, with no guessed metrics.
- `primary_research_keyword` comes from the fixed scoring script; hard gates, coefficients, scores, and exclusions are reported.
- Keyword drift candidates are classified, result-overlap checked, and brand/non-brand demand kept separate.
- Google Trends uses Web Search only.
- SerpApi is used first for Google Trends when configured; its key is absent from artifacts and logs.
- Tavily claims carry source URLs and authority notes.
- `source_usage` totals reconcile with its detailed tool-call rows, and Markdown/HTML contain the same usage statistics.
- `data.json` validation passes.
- Markdown and HTML conclusions agree.
- HTML opens without horizontal overflow.
- The fixed deliverable set is present; unavailable sources are explicitly represented as missing rather than silently omitted.
- No financial analysis appears.
- No secrets or browser state are present in deliverables.
