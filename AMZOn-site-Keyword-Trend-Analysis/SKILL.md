---
name: amzon-site-keyword-trend-analysis
description: AMZOn-site-Keyword-Trend-Analysis｜亚马逊站内关键词趋势选品（只看需求端、以趋势为主线）：用卖家精灵、SIF、Sorftime 三个 MCP 的时间序列做关键词/产品的趋势诊断，并预测未来 3–6 个月走势（方向、阶段、峰谷时点、三情景、证实/证伪信号），输出 Excel + 离线 HTML 趋势图。不看成本、供应链、库存、广告盈亏。默认美国站、膳食补充剂优先。用户说"趋势选品/找增长词/哪些词在起量/预测这个词接下来怎么走/这个品值不值得提前布局/季节性判断"时使用。
---

# AMZOn-site-Keyword-Trend-Analysis · 亚马逊站内关键词趋势选品（需求端）

回答三个问题：**什么在起量？它是真趋势还是假热度？到你能上架的时候它会走到哪？** 不回答"能不能赚钱、货从哪来"。

默认：美国站、膳食补充剂、预测时点 = 今天 + 4–6 个月（上架提前期，可由用户改）。

## 铁律

1. **只看需求端。** 不算单位经济、CPC/CVR 盈亏、MOQ、供应商、头程、库存。结论里不得出现成本或供给判断；结论末尾固定写"本结论不含供给与利润判断"。
2. **一个结论至少两个独立信号源。** 站内搜索、类目/单品销量、站外领先（Google/TikTok/Reddit）算不同源；同一个 MCP 里的两个工具如果底层同为 ABA，只算一个源。不足两个源 → 结论最多"观察"。
3. **证据分级。** 每条证据标 `FACT`（原始返回）/ `ESTIMATE`（第三方估算：销量、搜索量推算）/ `ASSUMPTION`（分析假设）/ `UNKNOWN`。不编数、缺失不填 0。
4. **单次峰值不是季节性，增长率不过基数不算增长。** 判读规则见 `references/trend-reading.md`。
5. **预测是定性判断，不是承诺。** 只给方向、阶段、峰谷时点、三情景、置信度、证实/证伪信号；不画伪精确预测线。
6. **功效/品牌红旗只标记，不进闸门。** 红旗不改变趋势结论，只让用户知道此方向有风险（`scripts/scan_flags.py`）。
7. **用量先报备。** 第 1 步开始前先列出准备调用的工具与大概次数，默认最多 10 个候选进入第 3 步。
8. 工具报 `secret_*`（额度/授权）或空返回：记入 `unknowns`，降级到其他源，不重复重试。

## 流程

脚本路径 `${CLAUDE_SKILL_DIR}/scripts/`，Windows 用 `python`。工具用法、参数、坑见 `references/tool-map.md`。

### 第0步：定题
确认：站点（默认 US）、品类/种子词或"全面扫描"、预测时点（默认 +4–6 个月）、入口。先调 `mcp__sorftime__get_time` 取当前日期并写入 `meta.as_of`。算出目标月份，后面所有"到时候会怎样"都对着这个月份说。

### 第1步：发现候选（选一条或组合）
- **A 趋势扫描**（没种子词）：sellersprite `aba_research_monthly`/`weekly`（searchModel 3/4/5，Health 类）、`keyword_research`（近3月/同比增长）、`product_research`（销量增长率、新品）、sorftime `potential_product`。
- **B 种子词扩展**：SIF `market_screen_keyword_opportunities`、sorftime `keyword_extends`、sellersprite `keyword_miner`。
- **C ASIN 反查**：sellersprite `traffic_keyword`、SIF `market_get_asin_keyword_signals`。
- **D 站外先行**：sellersprite `google_trend`、sorftime `tiktok_product_search`/`tiktok_category_trend`、`reddit_post_search`。
- **E 场景/季节日历**：用 `references/supplement-seeds.md` 的场景词、季节表倒推，再走 B。

筛出候选后按"增长率 + 绝对量双门槛"压到 ≤10 个；门槛是可调起点，要在报告里写明用了什么值。

### 第2步：需求真实性
- SIF `market_get_keyword_root_trend`：精确词 vs 长尾，判断是需求转移还是品类萎缩。
- sellersprite `keyword_miner`（keywordList 精准批量）：购买率、相关度。
- 必须有**精准词**（能描述成分/形态/人群/场景，搜索结果基本同一购买任务）；没有 → 标"需求不可触达"，不进第3步。

### 第3步：趋势诊断（核心）
每个候选拉 ≥2 个独立源的序列：
- 站内搜索：SIF `market_get_keyword_history`（多年周度）+ `market_get_keyword_demand`（生命周期、动量、季节、weeks_to_peak）；sellersprite `keyword_research_trends`/`aba_research_trend`；sorftime `keyword_trend`。
- 销量侧：先从该词 Top1–3 点击 ASIN 调 `asin_prediction` 反查 `nodeIdPath`（最后一段即 sorftime `node_id`），再查 sorftime `category_trend`、sellersprite `market_product_demand_trend`；单品用 `asin_prediction`/`product_trend`。不要按名称搜类目（见 tool-map）。
- **三家的搜索量都是 ABA，只算 1 个源**；判读前先按 trend-reading §1.1 剔除脉冲、单品事件，并复核工具给出的峰值月。
- 站外：`google_trend`、`tiktok_category_trend`。

按 `references/trend-reading.md` 归入 7 类原型之一，并写下依据。

### 第4步：进入窗口（需求视角）
需求是否外溢给新品？SIF `market_get_keyword_competition`（集中度趋势、conversion_gap）、`market_get_keyword_root_competitors`；sellersprite `market_listing_date_distribution`/`market_listing_trend_distribution`；sorftime `category_trend` 的 `NewProductSalesAmountShare`。只判断"需求流向有没有给后来者留位置"，不谈成本。

### 第5步：需求缺口
sorftime `product_customers_say`、`reddit_post_search`（post_type 3 抱怨 / 6 创新）、sellersprite `review`；SIF `search_ctr` 高而 `cvr` 低的词 = 未满足需求信号。输出成"需求句"：谁、什么场合、想解决什么。

### 第6步：未来预测（定性）
对每个候选，按预测时点写：
- 方向与阶段（原型 + 当前季节位置）；
- 距峰/谷多少周（SIF `weeks_to_peak`，核对多年峰值月）；
- 保守/基准/乐观三情景（各一两句，说明依赖什么）；
- 置信度（高/中/低：由一致的独立源数与历史年数决定，规则见 trend-reading）；
- **证实信号 / 证伪信号**：下次复查看什么、什么时候看。
领先-滞后链检查：站外先动、站内跟上 = 成立；只有站外动 = 早期，放"观察"。

### 第7步：结论与监测
每个候选给 `推荐 / 观察 / 放弃` 和一句理由；任何关键项 UNKNOWN → 最多"观察"。同时产出 `watchlist`（复查什么、何时、触发条件）。

### 第8步：红旗 + 出报告
```bash
python ${CLAUDE_SKILL_DIR}/scripts/scan_flags.py <payload.json>
python ${CLAUDE_SKILL_DIR}/scripts/build_xlsx.py <payload.json>
python ${CLAUDE_SKILL_DIR}/scripts/build_html.py <payload.json>
```
payload 结构见 `references/output-schema.md`。输出到 `meta.out_dir`（默认当前目录），文件名 `{topic}_趋势选品_v{n}_{YYYYMMDD}_{AM|PM}{hhmm}.xlsx/.html`。

### 第9步：对话总结
简短：报告路径；每个候选一行（词 + 原型 + 结论 + 预测一句话）；红旗；UNKNOWN 与降级情况；下次复查建议。不复述整张表。

## 参考文件
- `references/tool-map.md`：每步工具、关键参数、返回字段、已知坑
- `references/trend-reading.md`：7 类原型、季节性/基数/领先滞后判读、置信度规则、预测输出模板
- `references/supplement-seeds.md`：补剂种子词、场景词、季节日历、类目获取
- `references/output-schema.md`：payload JSON 结构
