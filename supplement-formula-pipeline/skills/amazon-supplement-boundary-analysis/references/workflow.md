# Workflow

## 1. Case Setup

Create one isolated case folder per run:

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
├── inputs/
├── sources/
├── scratch/
└── deliverables/
```

Copy the Sif Excel into `inputs/` or keep it in `outputs/inputs/{asin}/`. Do not edit the original user download.

## 2. Sif Excel Parsing

Extract at least:

- Sheet names and row counts.
- Relevance levels and counts.
- Weekly search volume sums by relevance.
- Keyword clusters: core ingredient, adjacent ingredients, functional terms, brand/competitor terms, noise, and risk terms.
- Top high-relevance keywords by score, search volume, conversion rate, and bid.
- High-volume low-relevance terms that may tempt but distort positioning.

## 3. Station Data Validation

Use Sorftime MCP for:

- `product_detail` for ASIN title, brand, category, price, rating, launch date, sales.
- `product_traffic_terms` to identify actual organic/ad exposure.
- `competitor_product_keywords` to cross-check competitor keyword exposure.
- `keyword_detail` for key extension terms.
- `keyword_trend` for unstable or trend-driven terms.

**降级提示：** 如果 Sorftime MCP 不可用（连接错误、超时或返回空结果），自动降级到 agent 内置 web search。搜索策略见 SKILL.md 的 Web Search 兜底策略章节。

## 4. Off-Site Cross-Check

Use Exa or Apify only when needed:

- Safety or regulatory status may have changed.
- A proposed ingredient extension is scientifically or semantically uncertain.
- The user wants trend/user-discussion context.
- Direct sources or current references are required.

Prefer official, peer-reviewed, or primary sources for safety/regulatory claims.

**降级提示：** 如果 Exa/Apify MCP 不可用，使用 agent 内置 web search 搜索 `USPTO {成分名}` 或 `FDA {成分名} dietary supplement` 获取法规和 IP 背景。

## 5. Boundary Judgment

Classify terms and ingredients into:

- Strong anchor: direct core ingredient match.
- Natural extension: ingredient or function logically extends the anchor.
- Borrowable but risky: high traffic but brand/IP/compliance or relevance risk.
- Avoid/noise: unrelated, prohibited, misleading, or likely to dilute positioning.

## 6. Deliverables

Produce:

- Executive report.
- Solution comparison.
- Radar chart HTML and PNG.
- Supplement Facts variants if the user selects a direction.

The report should explain why each solution can or cannot carry a traffic boundary.

Language requirement:

- Write formal reports and synthesized conclusions in Chinese by default.
- Preserve exact English names, ASINs, ingredient names, keywords, URLs, and regulatory terms where needed.
- Use English only when the user explicitly requests an English deliverable.
- Translate upstream structured-risk scaffolding into Chinese in final reports. The structure can be inherited, but English headings, table headers, risk levels, and posture labels must not leak into formal Chinese deliverables.
- Run `scripts/validate_chinese_deliverable.py` on the final Markdown reports before handing off the case.
