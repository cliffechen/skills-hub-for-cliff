# ZooData — 面向 AI Agent 的电商数据层

> 亚马逊商品、类目、市场、竞品、评论、价格带、品牌和历史趋势的结构化数据入口。当前版本优先走 Sorftime MCP，ZooData API 作为显式后备。

## 这个 Skill 做什么

这是整个 ZooData Skills 仓库的基础数据层。它提供统一命令入口，让 Agent 能查询亚马逊类目、市场指标、商品搜索、竞品、实时 ASIN 详情、评论、价格带、品牌和历史趋势。

适合在这些场景使用：

- 想查“有哪些数据接口可用”
- 想直接拿某个关键词、类目或 ASIN 的结构化数据
- 想让其他 Amazon 分析技能复用同一套数据入口
- 想在 Sorftime MCP 与 ZooData API 之间切换 provider

## 安装

```bash
npx skills add SerendipityOneInc/ZooData-Skills
```

安装时选择 **ZooData**。

## 数据源设置

CLI 会优先使用 **Sorftime MCP**：如果 Codex 中已经配置 `sorftime_mcp`，或设置了 `SORFTIME_MCP_URL` / `SORFTIME_MCP_KEY`，就会自动走 Sorftime。

```bash
# 自动选择已配置的 Sorftime MCP
python scripts/zoodata.py check
python scripts/zoodata.py products --keyword "yoga mat"

# 显式指定 provider
python scripts/zoodata.py --provider sorftime-mcp products --keyword "yoga mat"
python scripts/zoodata.py --provider zoodata products --keyword "yoga mat"
```

如果要使用原 ZooData API：

1. 到 [zoodata.ai/api-keys](https://zoodata.ai/en/api-keys) 获取 key
2. 设置环境变量并强制 provider：
   ```bash
   export ZOODATA_API_KEY='hms_live_xxxxxx'
   export AMAZON_DATA_PROVIDER=zoodata
   ```

## 怎么使用

### 自然语言

安装 skill 后，可以直接问 Agent：

- “这个数据层有哪些接口？”
- “查一下 ASIN `B01LP0U5X0` 的实时详情。”
- “搜索 `yoga mat` 相关商品，按销量排序。”
- “拉一下这个类目的市场数据和价格带。”

### 命令行

```bash
# 商品搜索
python scripts/zoodata.py products --keyword "yoga mat"

# 单个 ASIN 详情
python scripts/zoodata.py product --asin B01LP0U5X0

# 历史趋势
python scripts/zoodata.py history --asins B01LP0U5X0 --start-date 2025-01-01 --end-date 2025-02-01

# 输出单行 JSON
python scripts/zoodata.py --format compact products --keyword "yoga mat"
```

## 交付物 / 结果是什么

这个基础 skill 的直接输出是结构化 JSON。典型字段包括：

- `success`：请求是否成功
- `data`：商品、类目、市场、评论、历史趋势等数据主体
- `_query`：实际调用的 endpoint 和参数
- `_provider`：当前数据源，例如 `sorftime-mcp`，以及底层 MCP tool 信息

Agent 会基于这些 JSON 进一步整理成中文报告、表格、对比清单、评分结论或行动建议。直接使用 CLI 时，交付物就是 JSON。

## API / 能力覆盖

| # | Endpoint | Purpose |
|---|----------|---------|
| 1 | `categories` | 浏览 / 搜索类目树 |
| 2 | `markets/search` | 市场级指标：销量、价格、集中度 |
| 3 | `products/search` | 商品搜索与选品筛选 |
| 4 | `products/competitors` | 竞品发现 |
| 5 | `realtime/product` | 实时 ASIN 详情：评分、BSR、BuyBox、变体 |
| 6 | `realtime/reviews` | 原始评论 |
| 7 | `reviews/analysis` | 评论聚合分析或兼容 fallback |
| 8 | `products/price-band-overview` | 价格带概览 |
| 9 | `products/price-band-detail` | 价格带明细 |
| 10 | `products/brand-overview` | 品牌集中度 |
| 11 | `products/brand-detail` | 品牌明细 |
| 12 | `products/history` | 价格、BSR、销量历史趋势 |
| 13 | `keywords/*` | 关键词详情、趋势、拓词、搜索结果、ASIN 流量词 |

## 额度

额度消耗取决于 provider 和 endpoint。Sorftime MCP 按 MCP 账户额度计；ZooData 响应里会返回 `meta.creditsConsumed`。

## 底层来源

共享 CLI 保留原 ZooData 命令形态，并在 Sorftime MCP 可用时自动映射到 Sorftime 的 Amazon 工具。
