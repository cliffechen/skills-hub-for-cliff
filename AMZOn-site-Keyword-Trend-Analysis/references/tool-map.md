# 工具地图（三个 MCP × 趋势选品各步）

工具名前缀：`mcp__sellersprite__`、`mcp__sif__`、`mcp__sorftime__`。这些工具可能是延迟加载的，用前先 ToolSearch `select:<全名>` 批量加载。

## 通用约定
- 站点代码：sellersprite / SIF 用 `US`；**sorftime 英国站是 `GB`**，且不同工具的枚举不同（`amz_site` / `keyword_support_site` / `site`），默认值是 `Unknow`，**必须显式传 `US`**。
- 周：**SIF 周以周日为起点**；**sellersprite `aba_research_weekly` 的 date 必须是当周周六**（yyyyMMdd）；月份格式 yyyyMM。
- 控点数：sellersprite 多数工具支持 `returnFields`，只取需要的字段。
- 报错 `secret_expired / secret_invalid / secret_no_remaining / secret_unauthorized`：记 `unknowns`，降级，不重试。
- 每条拉回的序列都要在 payload 里写 `source`、`granularity`、`tag`（FACT/ESTIMATE）、数据窗口。

## 第1步 发现候选
| 入口 | 工具 | 关键参数 |
|---|---|---|
| A 扫描 | sellersprite `aba_research_monthly` | `request.marketplace=US`、`date=yyyyMM`、`searchModel`：3 持续增长 / 4 快速飙升 / 5 潜力 / 2 异动；`departments` 限 Health；`order.field=growth_rate_trend_min`（近3月）或 `yearly_growth_rate`；`minSearches` 设绝对量下限 |
| A 扫描 | sellersprite `aba_research_weekly` | 同上，`date` 为周六；看近期异动 |
| A 扫描 | sellersprite `keyword_research` | `keywords`、`minSearchNearlyCr`（近3月增长率）、`minSearchMonthCr`（同比）、`withYearlyGrowth=true`（新细分市场）、`minSearches` |
| A 扫描 | sellersprite `product_research` | `keyword`、`minUnitsCr`（销量增长率）、`badgeNR`、`availableMonth`、`variation=Y` |
| A 扫描 | sorftime `potential_product` | `amz_site=US`、`search_name`、销量区间（价格仅作定位，不做成本判断） |
| B 扩展 | SIF `market_screen_keyword_opportunities` | `keyword_root`、`topN`；返回 `entry_signal`、`search_volume`（单周）、`click_share_top3`、`cvr` |
| B 扩展 | sorftime `keyword_extends` | `keyword`、`keyword_support_site=US` |
| B 扩展 | sellersprite `keyword_miner` | `keyword` 取相关词；`keywordList` 精准批量 |
| C 反查 | sellersprite `traffic_keyword`；SIF `market_get_asin_keyword_signals` | ASIN |
| D 站外 | sellersprite `google_trend` | `request.marketplace`、`keyword`、`monthly=true` |
| D 站外 | sorftime `tiktok_product_search` / `tiktok_category_trend` | `site=US`；`trend_index` 0 月销量 / 1 环比 / 23 近3月上架销量占比 |
| D 站外 | sorftime `reddit_post_search` | `search_name`；`post_type` 3 抱怨 / 6 创新 |

## 第2步 需求真实性
- SIF `market_get_keyword_root_trend`：`keyword`、`granularity=month`。看 `exact_keyword_demand_pct` / `longtail_demand_pct`；精确词降而词根综合量稳 = 需求转移到长尾；两条同降 = 品类萎缩。
- sellersprite `keyword_miner`（`keywordList`）：购买率、供需比等做佐证。

## 第3步 趋势诊断
| 源 | 工具 | 得到什么 |
|---|---|---|
| 站内搜索 | SIF `market_get_keyword_history`（`keywords` ≤10，`granularity=month` 或 `week`） | 多年 ABA 搜索量/排名序列、Top3 点击与转化集中度 |
| 站内搜索 | SIF `market_get_keyword_demand`（`keywords` ≤20） | 生命周期诊断、动量、`season_position`、`peak_months`、`weeks_to_peak`、`yoy_change`；**读 `seasonal_strength`，"数据不足"时没有峰谷字段，不代表无季节性** |
| 站内搜索 | sellersprite `keyword_research_trends` | 搜索量、购买量、购买率、同比/环比/近3月增长 |
| 站内搜索 | sellersprite `aba_research_trend`（`timeGranularity` W/M） | ABA 排名与搜索量序列 |
| 站内搜索 | sorftime `keyword_trend` | 搜索量、排名、CPC 走势（CPC 只当"热度/竞争升温"信号，不做成本判断） |
| 类目销量 | sorftime `category_trend`（`node_id`、`trend_index`） | `SalesCount`、`NewProductSalesAmountShare`、`Top3ProductSalesAmountShare`、`AvgRatingCount` 等 |
| 类目销量 | sellersprite `market_product_demand_trend` | 类目 PV、搜索购买比、退货率（退货率仅记录） |
| 单品 | sellersprite `asin_prediction`（近14个月）/ `asin_sales_trend`；sorftime `product_trend`（`product_trend_type`） | 头部/新品销量曲线 |
| 站外 | `google_trend`、sorftime `tiktok_category_trend` | 领先指标 |

独立源计法：站内搜索（ABA）= 1 源，即使来自不同 MCP；类目/单品销量 = 1 源；Google = 1 源；TikTok = 1 源；Reddit = 定性辅助，不单独计源。

**同源核对（实测）**：SIF `market_get_keyword_history`、sellersprite `aba_research_trend` / `keyword_research_trends` 的月搜索量逐月一致，Sorftime `keyword_trend` / `keyword_extends` 形状相同但量级约高 1.4–1.5 倍——三者都是 ABA。只取一家做量级（默认 SIF），其他只用来核对形状；报告里不得把它们写成"多源印证"。

**数据矛盾优先级**：SIF `market_screen_keyword_opportunities` 的单周 `search_volume` 可能与 `market_get_keyword_demand` / 月量折算对不上（实测 8,740 vs 14,944）。以 `market_get_keyword_history` 月量 ÷ 4.3 和 `market_get_keyword_demand` 的周序列为准，筛选工具的周量只用于排序。

**Google 最新点**：`google_trend` 最后一个点常是未完成周期（数值偏低），默认丢弃，只用到上一个完整点。

## 第4步 进入窗口（需求视角）
- SIF `market_get_keyword_competition`：`concentration_profile.trend.divergence`、`market_structure.conversion_gap`（点击集中但转化分散 = 头部守位不稳）。
- SIF `market_get_keyword_root_competitors`：`rank1_count` 高 = 真领导者。
- sellersprite `market_listing_date_distribution` / `market_listing_trend_distribution`：需要 `nodeIdPath`、`month`、`newProduct`（月数，补剂建议 6）。
- sorftime `category_trend`：`NewProductSalesAmountShare`。

## 第5步 需求缺口
- sorftime `product_customers_say`（`asin`、`site=US`）；sellersprite `review`；sorftime `reddit_post_search`。
- SIF `market_screen_keyword_opportunities` 里 `search_ctr` 高、`cvr` 低的词。

## 获取类目节点（nodeIdPath / node_id）
**首选：从头部 ASIN 反查。** 先用 SIF `market_get_keyword_competition` 或 `market_get_keyword_history` 拿到该词 Top1–3 点击 ASIN，再调 sellersprite `asin_prediction`（或 `asin_detail`），返回的 `nodeIdPath`（如 `3760901:23675621011:3773631:3773651`）就是这个细分市场的真实节点：
- 整串用于 sellersprite 的 `market_*`、`product_research(nodeIdPath=…)`；
- 最后一段（如 `3773651`）就是 sorftime `category_trend` / `category_report` 的 `node_id`。
多个头部 ASIN 落在不同节点时，分别记录，以点击份额最大的为主。

按名称搜节点不可靠（实测）：sorftime `category_search_from_product_name` 只返回宽泛大类，`category_name_search("organ")` 返回了无关类目；只在反查失败时兜底，并人工核对名称。sellersprite `product_node` 可按关键词查，同样需人工核对。

## 已知不可靠的调用
- sellersprite `product_research` 只传 `keyword`（模糊匹配）时，实测返回大量无关商品且 `totalUnits` 为空。要用它，必须带 `nodeIdPath`（从上面反查得到），或改 `matchType=3` 精准匹配，并检查返回标题是否相关。
- sorftime `get_time` 偶发连接重置：失败就用环境日期，记入 unknowns。
- sorftime `reddit_post_search` 噪音大（实测 53 条仅 2 条相关）：用更具体的词（成分 + 人群/场景），只作定性旁证。
