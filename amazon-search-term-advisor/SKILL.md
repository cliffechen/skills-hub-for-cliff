---
name: amazon-search-term-advisor
description: >-
  Turn a raw Amazon Advertising "Sponsored Products Search term report" (in
  either English or Chinese column headers) into a polished 4-tab Excel
  workbook (Customer Search Terms, Targeting, Untargeted Search Terms, Action
  Recommendations) with per-row Spend %, Sales %, Orders %, CTR, CVR, CPC, and
  ACOS, aggregated and sorted by sales, plus a statistically-derived action
  column (harvest / negate / scale up / scale down / observe) with a written
  reason per term. Use WHENEVER the user uploads or points at an SP /
  Sponsored Products search term report (an Amazon Ads search-term export
  identifiable by columns like Customer Search Term / 客户搜索词, Targeting /
  投放, Impressions / 展示量, Clicks / 点击量, Spend / 花费, Total Sales /
  总销售额, Total Orders / 总订单数) and wants it analyzed, cleaned,
  summarized, broken out by search term vs. target, wants to find untargeted
  / un-harvested search terms, or wants operational next-steps / bid
  decisions / negative-keyword candidates from it — even if they don't say
  "skill" or name all the tabs. Also trigger on "analyze my search term
  report", "which search terms aren't targeted", "build the search term
  analysis", "harvest keywords from this ad report", "make the workbook",
  "tell me what to do with these search terms", "which terms should I
  negate/scale", or the Chinese equivalents such as "分析这份搜索词报告" /
  "找出没有投放的搜索词" / "做一下这个词表" / "给我实操建议" / "哪些词该否定/加
  预算". Output sheet names and headers automatically match the input
  report's language. Do NOT use for bulk keyword research, rank tracking, or
  a search-query-performance (SQPR/Brand Analytics) report — those are
  different inputs.

---
 
#  amazon-search-term-advisor
 
## 关于本 Skill
 
- **作者**：Ginv | 公众号 「Adobe of Amazon」
- **用途**：分析SP搜索词报告并输出3张统计表 + 1张决策表
---
 
## 触发条件
 
Use WHENEVER the user uploads or points at an SP /
  Sponsored Products search term report (an Amazon Ads search-term export
  identifiable by columns like Customer Search Term / 客户搜索词, Targeting /
  投放, Impressions / 展示量, Clicks / 点击量, Spend / 花费, Total Sales /
  总销售额, Total Orders / 总订单数) and wants it analyzed, cleaned,
  summarized, broken out by search term vs. target, wants to find untargeted
  / un-harvested search terms, or wants operational next-steps / bid
  decisions / negative-keyword candidates from it — even if they don't say
  "skill" or name all the tabs. Also trigger on "analyze my search term
  report", "which search terms aren't targeted", "build the search term
  analysis", "harvest keywords from this ad report", "make the workbook",
  "tell me what to do with these search terms", "which terms should I
  negate/scale", or the Chinese equivalents such as "分析这份搜索词报告" /
  "找出没有投放的搜索词" / "做一下这个词表" / "给我实操建议" / "哪些词该否定/加
  预算". Output sheet names and headers automatically match the input
  report's language. Do NOT use for bulk keyword research, rank tracking, or
  a search-query-performance (SQPR/Brand Analytics) report — those are
  different inputs.


# Amazon Sponsored Products — Search Term Analysis Workbook

Converts one raw SP search-term report into a client-ready `.xlsx` with four
tabs — three statistical/aggregation tabs plus a fourth tab that turns those
numbers into a per-term action recommendation. A bundled script does the
whole transform deterministically; your job is to run it, recalculate,
verify, and deliver.

## The four tabs (exact sheet names, in this order)

1. **Customer Search Terms** — every unique customer search term
2. **Targeting** — every unique target (keywords, product/ASIN targets, and
   auto match-types)
3. **Untargeted Search Terms** — customer search terms with **no matching
   target** (the keyword-harvest list)
4. **Action Recommendations** — one row per customer search term with a
   recommended action (harvest / negate / scale up / scale down / observe /
   maintain) and a plain-language reason, so the workbook is directly
   actionable and not just descriptive statistics. See "Tab 4 logic" below.

Tabs 1–3 each have these 13 columns, in order:

`<label> · Impressions · Clicks · Spend · Spend % · Sales · Sales % · Orders · Orders % · CTR · CVR · CPC · ACOS`

where `<label>` is **Customer Search Term** (tabs 1 & 3) or **Targeting** (tab 2).

## Bilingual input/output

The report may come in **English or Chinese (简体中文)** column headers — the
builder auto-detects this from the input and mirrors it in the output:

| | English input | Chinese input |
|---|---|---|
| Sheet 1 | Customer Search Terms | 客户搜索词 |
| Sheet 2 | Targeting | 投放 |
| Sheet 3 | Untargeted Search Terms | 未投放搜索词 |
| Sheet 4 | Action Recommendations | 实操建议 |
| Headers (tabs 1–3) | Impressions / Clicks / Spend / Spend % / Sales / Sales % / Orders / Orders % / CTR / CVR / CPC / ACOS | 展示量 / 点击量 / 花费 / 花费占比 / 销售额 / 销售额占比 / 订单量 / 订单占比 / 点击率(CTR) / 转化率(CVR) / 单次点击成本(CPC) / 广告成本占比(ACOS) |
| TOTAL row label | TOTAL | 总计 |
| Default output filename | `<input>_Analysis.xlsx` | `<input>_分析.xlsx` |

Detection is column-name based (e.g. `客户搜索词`/`投放`/`展示量`/`点击量`/
`花费`/`总销售额`/`总订单数` for the Chinese Amazon Ads export vs.
`Customer Search Term`/`Targeting`/`Impressions`/`Clicks`/`Spend`/
`Total Sales`/`Total Orders` for English), not the user's chat language — a
Chinese-language user uploading an English-header report still gets an
English-header workbook, and vice versa. Give your own chat summary
(row counts, totals, top untargeted terms, action counts) in whichever
language the user is chatting in, regardless of which language the workbook
itself is in.

## Tab 4 logic — how "Action Recommendations" decides what to say

Tab 4 is a decision layer on top of tabs 1–3, not a second copy of the same
numbers. **Every threshold is derived from the report's own data — there is
no hardcoded target ACOS or minimum-order count to configure**, so the sheet
stays valid across accounts/categories without editing the script:

- **ACOS "high"/"low"** → quartiles (Q1/Q3) of ACOS among that report's own
  sales-generating rows (needs ≥4 such rows; skipped otherwise). A term above
  Q3 is underperforming relative to its own peer group in this exact report;
  below Q1 is outperforming.
- **"Is the sample big enough to call it?"** → a 95% Wilson score confidence
  interval on CVR (Orders/Clicks). A term only gets the high-confidence
  `negate` / `scale_up` verdict when the interval is both narrow enough to
  trust and clearly separated from the account's blended CVR.
- **Obvious-but-small-sample outliers aren't buried in "observe."** Real
  reports are full of terms that don't clear the strict 95%-CI bar simply
  because clicks are moderate, yet the numbers are still an unmistakable red
  flag or green flag to a human. Two secondary, clearly-labeled tiers catch
  these instead of silently defaulting to "Maintain":
  - `likely_negate` — zero orders, and a Poisson check on "how many orders
    would this many clicks be expected to produce at the account's own
    average CVR" shows that seeing exactly zero has <12% probability by
    chance. (Example: 131 clicks / \$76 spend / 0 orders on an account
    averaging 1.7% CVR — the 95% Wilson interval alone won't confirm
    `negate`, but expecting ~2.3 orders and getting zero is too obvious to
    hide in "maintain.")
  - `likely_scale_up` — at least 2 real orders, and the term's actual CVR is
    ≥3× the account average, even though the small click count keeps the CI
    too wide for the strict `scale_up` verdict.
- **Priority order per term** (first match wins): `harvest` (untargeted term
  with ≥1 order — same low-risk logic as tab 3) → `negate` (CI-confirmed) →
  `scale_up` (CI-confirmed) → `scale_down` (worst ACOS quartile) →
  `likely_negate` (Poisson-obvious) → `likely_scale_up` (ratio-obvious) →
  `watch_small` (CI too wide, no obvious pattern either) → `watch_nodata`
  (zero clicks) → `maintain`.
- **Every row gets a plain-language "Why" column** stating the actual numbers
  behind the call (e.g. the CI bounds, the expected-vs-actual order count, or
  which quartile), so it reads as a reason, not a black-box label.
- **Rows are sorted action-first** (harvest/negate/scale-up/scale-down before
  the observe/maintain rows) and **color-tinted by action** (green =
  opportunity, red = cut spend, amber = not enough data, grey = no action)
  so the sheet is scannable without reading every row.
- A methodology footnote (account average CVR, ACOS Q1/Q3 for this run) is
  printed under the table so the reasoning is auditable.

## Workflow

1. **Locate the report.** It's the uploaded `.xlsx`/`.csv` with a
   `Customer Search Term` column. If several files are attached, pick that one.
2. **Run the builder** (from this skill's `scripts/` folder):
   ```bash
   python scripts/build_workbook.py <input_report.xlsx> <Output_Analysis.xlsx>
   ```
   It prints the row count of each tab and the source Spend/Sales/Orders totals
   — glance at these to confirm it read the file correctly.
3. **Recalculate and verify zero errors.** The builder writes formulas but not
   their values. Use the xlsx skill's recalc helper:
   ```bash
   cp /mnt/skills/public/xlsx/scripts/recalc.py .
   cp -r /mnt/skills/public/xlsx/scripts/office . 2>/dev/null
   python recalc.py <Output_Analysis.xlsx> 180
   ```
   The report has thousands of formulas, so allow a generous timeout. Require
   `"total_errors": 0`. If any appear, fix and re-run before delivering.
4. **Sanity-check** (optional but cheap): reload with `data_only=True` and
   confirm each of tabs 1–3's TOTAL row shows Spend %, Sales %, Orders % =
   100%, that tab 1's grand totals match the source totals the builder
   printed, and that tab 4's row count equals tab 1's row count (one
   recommendation per unique customer search term).
5. **Deliver** the file with `present_files` and give a short, bullet-led
   summary in the user's house style: tab row counts, account-level totals
   (Spend, Sales, ACOS), the top few untargeted terms worth harvesting, and
   the action-count breakdown from tab 4 (e.g. how many negate candidates,
   how many scale-up candidates) so the user knows where to look first.

## Rules the transform already enforces — keep them

These are deliberate. If output looks "off," re-read here before changing the
script, because these choices are usually the reason it's correct.

- **Aggregate before computing ratios.** The same search term (or target)
  recurs across campaigns/ad groups. Group case-insensitively, sum
  Impressions/Clicks/Spend/Sales/Orders into one row, then derive the ratios.
  This is why "Remove duplicates" and "case-insensitive matching" matter, and
  why each tab's percentages sum to 100%.
- **Percentages are per-tab.** Spend %, Sales %, Orders % divide each row by
  **that tab's own TOTAL**, not the global total. Tab 3 has its own smaller
  totals — that's intended.
- **Untargeted = exact-text miss against the Targeting column.** A search term
  is untargeted if its exact text (case-insensitive) is not an entry in
  Targeting. ASIN targets (`asin="b0..."`) and auto match-types (close-match,
  loose-match, substitutes, complements) never equal a real shopper query, so
  they don't pollute the result — what's left are genuine keywords you're
  paying for via broad/auto/product targeting but haven't added as exact terms.
  Only include terms with **≥ 1 impression**.
- **Sort by Sales descending.** Ties break by Spend, then Impressions, so the
  biggest wasted-spend / zero-sales terms rise to the top of the zero-sales
  block — exactly what an advertiser wants to see first.
- **Formulas, not hardcoded values.** Ratios and totals are live Excel
  formulas so the sheet recalculates if numbers change. Divisions are guarded
  with `IF(denominator=0, 0, …)` so there are never `#DIV/0!` errors (most rows
  have zero sales, so ACOS especially must be guarded). A guarded ACOS of 0
  means "no sales," and renders as `-`.
- **Formatting.** Navy bold header, frozen header row, autofilter on **data
  rows only** (the TOTAL row sits just below the filter range so filtering
  never hides it), Arial 10, currency as `$#,##0.00`, percentages at 2
  decimals, integers thousands-separated, and all zeros shown as `-` to keep
  large tables legible.

## Input quirks the builder handles

- **Header trailing spaces / case** (e.g. `"7 Day Total Sales "`) — matched by
  normalized comparison.
- **Attribution window varies** — `7 Day` vs `14 Day` Total Sales/Orders are
  both found by matching on "Total Sales" / "Total Orders" (or `总销售额` /
  `总订单数` for Chinese reports, e.g. `7天总销售额`).
- **Chinese column headers** — the standard Amazon 卖家平台 export uses
  `客户搜索词` / `投放` / `展示量` / `点击量` / `花费` / `7天总销售额` /
  `7天总订单数(#)`. The Chinese "contains" matches are deliberately specific
  (`总销售额`, `总订单数`) so they don't misfire on adjacent SKU-level columns
  in the same report, like `7天内广告SKU销售额` or `7天总销售量(#)`.
- **`.csv` or `.xlsx`** input both work, in either language.

If a required column truly can't be found, the script stops and lists the
columns it did see — inspect the report and, if a header was renamed or is in
a language not yet supported, extend `FIELD_ALIASES` in
`scripts/build_workbook.py` (`load()`).
