---
name: amazon-supplement-boundary-analysis
description: 成分流量边界分析 —— 从 Sif AI 关键词 Excel 报告、锚定 ASIN 和 Supplement Facts 出发，分析 Amazon US 保健品的成分与流量边界。用于解析关键词调研、结合 Sorftime/AnySearch/Exa 证据、判断成分延伸机会和风险、生成边界报告、方案对比、雷达图和候选 Supplement Facts。
---

# Amazon Supplement Boundary Analysis

## Core Workflow

Use this skill to run a reusable `ingredient x traffic boundary` analysis for Amazon US supplements.

1. Create an isolated case folder with `scripts/create_case_workspace.py`.
2. Parse the Sif Excel with `scripts/analyze_sif_excel.py`.
3. Query Sorftime for ASIN detail, product traffic terms, competitor keywords, keyword detail, and keyword trends.
4. Use Exa/Apify only for light off-Amazon validation when ingredient adjacency, legality, safety, or trend context matters.
5. Write all deliverables into the case folder, not into the skill or project root.
6. Generate radar charts with `scripts/generate_radar.py`.

## Output Isolation Rule

Never put run outputs inside this skill folder. Put all case artifacts under:

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
```

Keep input copies under `outputs/inputs/` or the case folder `inputs/`. Keep scratch/intermediate files under `outputs/scratch/`.

## Language Rule

All formal deliverables for this project must be written in Chinese by default, including boundary reports, solution comparisons, evidence summaries, radar-chart notes, and Supplement Facts commentary. Preserve exact English product titles, ASINs, ingredient names, keyword literals, regulatory terms, and URLs where precision matters. Only produce English reports when the user explicitly requests English.

## Required Inputs

- Sif AI keyword research Excel file.
- Anchored ASIN.
- Supplement Facts as text.
- User-selected direction if generating Supplement Facts variants.

## Default Assumptions

- Marketplace: Amazon US.
- Category: dietary supplement / health supplement.
- Default package: 90 capsules or softgels.
- Default serving math: `Servings Per Container = 90 / Serving Size`.
- If the selected serving size does not divide 90 cleanly, adjust serving size or dosing before finalizing.
- Default other ingredients template: `Distilled Water, Maltitol Syrup, Maltitol Powder, Isomalt, Pectin, Citric Acid, Sodium Citrate, Natural Flavor, Natural Color, Carnauba Wax.`

## Standard Deliverables

Write these files into the case folder:

- `{name}-ingredient-traffic-boundary-report.md`
- `{name}-solution-comparison.md`
- `{name}-radar-chart.html`
- `{name}-radar-chart.png`
- Optional: `{name}-scheme-{direction}-supplement-facts-3-variants.md`
- Optional: `{name}-final-{ingredients}-softgel-formula.md`

## References

Read only what is needed:

- `references/workflow.md` for the full process.
- `references/output-contract.md` for folder and file naming.
- `references/scoring-rubric.md` for radar scoring dimensions.
- `references/supplement-facts-guidelines.md` for 90-count Supplement Facts rules.

## Scripts

Use scripts rather than rewriting repeated utility code:

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py --asin B0GKPTBN59 --core-ingredient "C15 Pentadecanoic Acid" --sif-excel "C:\path\to\sif.xlsx"
python skills/amazon-supplement-boundary-analysis/scripts/analyze_sif_excel.py "outputs\inputs\b0gkptbn59\sif.xlsx" --output-dir "outputs\cases\B0GKPTBN59-C15-Pentadecanoic-Acid-20260421-133715\sources"
python skills/amazon-supplement-boundary-analysis/scripts/generate_radar.py assets/radar_scores_template.json --output-dir "outputs\cases\case-name"
```

## Risk Rules

- Treat branded ingredient names, patented ingredient stories, brand names, and disease claims as boundary risks.
- Do not turn high-volume terms into ingredient recommendations unless the ingredient logic, traffic logic, and compliance boundary all hold.
- Do not include procurement difficulty, supplier availability, or raw material cost in scoring unless the user explicitly asks.
- Clearly label nutrition/formula drafts as exploratory, not final manufacturing or legal advice.

## Web Search 兜底策略

当 Sorftime MCP 或其他专用 MCP 不可用时，使用当前 agent 自带的网络搜索能力作为兜底。

### 优先级
1. **专用 MCP**（Sorftime、AnySearch、Exa、Apify）— 数据结构化程度高，优先使用
2. **Agent 内置 Web Search** — 任何主流 agent（Claude Code、OpenAI Codex、QoderWork 等）都自带网络搜索或网页抓取能力，当 MCP 不可用时自动降级到此层
3. **用户手动提供数据** — 最低优先级，仅在搜索也无法获取时请求用户粘贴

### 降级触发条件
- MCP 工具调用返回连接错误或超时
- MCP 返回空结果且关键词/ASIN 确实存在
- 当前 agent 环境未配置任何 MCP 服务

### 降级时的搜索策略
- 亚马逊产品数据：搜索 `site:amazon.com {ASIN}` 或 `{产品名} supplement facts`
- 关键词数据：搜索 `Amazon autocomplete {关键词}` 或 `{关键词} supplement search volume`
- 竞品数据：搜索 `site:amazon.com {核心关键词} supplement` 并手动提取 Top 结果
- 法规/IP 数据：搜索 `USPTO {成分名} trademark`、`FDA {成分名} dietary supplement`
- 评论/用户反馈：搜索 `site:reddit.com {成分名} supplement review`

### 降级输出标注
当使用 web search 兜底时，在报告的 Evidence Quality 部分明确标注：

> 本分析使用 web search 兜底获取部分数据，数据完整度可能低于 MCP 直连，建议在关键决策前用 Sorftime MCP 复核。
