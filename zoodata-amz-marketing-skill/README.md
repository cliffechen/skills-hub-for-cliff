# zoodata-amz-marketing-skill

这是一个集中打包的 Amazon US 市场数据分析 skill 套件。它把 `zoodata` 数据层和一组 `amazon-*` 分析技能放在同一个文件夹里，避免散落在 skills hub 根目录。

默认优先使用已配置的 **Sorftime MCP**；如果明确指定 `--provider zoodata`，才会走 ZooData API。

## 包含哪些 skill

| 目录 | 用途 | 典型结果 |
|---|---|---|
| [`zoodata/`](./zoodata/) | 共享数据层，查商品、类目、市场、评论、价格带、品牌、历史趋势 | 结构化 JSON |
| [`amazon-analysis/`](./amazon-analysis/) | 综合市场、竞品、机会、定价分析 | 市场概览、Top 产品、竞品对比 |
| [`amazon-market-entry-analyzer/`](./amazon-market-entry-analyzer/) | 市场进入判断 | GO / CAUTION / AVOID、进入建议、风险点 |
| [`amazon-opportunity-discoverer/`](./amazon-opportunity-discoverer/) | 机会产品扫描 | Top 10 机会、S/A/B/C 评级、风险告警 |
| [`amazon-competitor-intelligence-monitor/`](./amazon-competitor-intelligence-monitor/) | 竞品情报 | 竞品矩阵、品牌排名、价格地图、趋势告警 |
| [`amazon-pricing-command-center/`](./amazon-pricing-command-center/) | 定价分析 | RAISE / HOLD / LOWER、价格带、BuyBox 提示 |
| [`amazon-review-intelligence-extractor/`](./amazon-review-intelligence-extractor/) | 评论洞察 | 痛点、购买因素、正负面主题、用户画像 |
| [`amazon-daily-market-radar/`](./amazon-daily-market-radar/) | 每日市场监控 | RED / YELLOW / GREEN 告警、行动建议 |
| [`amazon-market-trend-scanner/`](./amazon-market-trend-scanner/) | 品类趋势扫描 | 趋势品类、新品、新进入者与风险 |
| [`amazon-keywords/`](./amazon-keywords/) | 关键词分析 | 拓词、搜索结果、ASIN 流量词、关键词诊断 |

## 怎么使用

### 自然语言

在 Codex/Agent 中直接提出业务问题，例如：

- “分析一下美国亚马逊 `algae calcium supplement` 市场，给我进入建议。”
- “帮我找 `magnesium glycinate gummies` 里适合新手卖家的机会产品。”
- “查 ASIN `B01LP0U5X0` 的详情、价格趋势和评论痛点。”
- “监控我的 5 个 ASIN，每天看价格、BSR、竞品和评论异常。”

Agent 会根据问题选择本套件里的具体 skill，并调用共享 CLI。

### 命令行

```bash
# 检查当前 provider；有 sorftime_mcp 配置时会自动走 Sorftime MCP
python zoodata/scripts/zoodata.py check

# 商品搜索
python amazon-analysis/scripts/zoodata.py products --keyword "yoga mat"

# 市场进入分析
python amazon-market-entry-analyzer/scripts/zoodata.py market-entry --keyword "algae calcium supplement"

# 单个 ASIN 详情
python amazon-analysis/scripts/zoodata.py product --asin B01LP0U5X0

# 历史趋势
python amazon-analysis/scripts/zoodata.py history --asins B01LP0U5X0 --start-date 2025-01-01 --end-date 2025-02-01

# 显式指定 provider
python amazon-analysis/scripts/zoodata.py --provider sorftime-mcp products --keyword "yoga mat"
python amazon-analysis/scripts/zoodata.py --provider zoodata products --keyword "yoga mat"
```

## 数据源设置

推荐方式：在 Codex 中配置 `sorftime_mcp`。配置存在时，CLI 会自动选择 `sorftime-mcp`。

可选环境变量：

```bash
export SORFTIME_MCP_URL='https://mcp.sorftime.com'
# 或
export SORFTIME_MCP_KEY='...'
```

如果要强制使用 ZooData API：

```bash
export ZOODATA_API_KEY='hms_live_xxx'
export AMAZON_DATA_PROVIDER=zoodata
```

不要把真实 key 写入仓库。

## 交付物 / 结果是什么

这个套件本身不是固定生成一个网页，而是给 Agent 提供数据能力和分析工作流。

直接跑 CLI 时，结果默认是 JSON，核心字段包括：

- `success`：请求是否成功
- `data`：商品、类目、市场、评论、历史趋势等数据主体
- `_query`：实际调用的 endpoint 和参数
- `_provider`：当前 provider，例如 `sorftime-mcp`

Agent 使用这些 JSON 后，通常会整理成中文报告、竞品矩阵、Top 产品清单、GO/CAUTION/AVOID 判断、定价建议、评论痛点或每日告警。

## 目录结构

```text
zoodata-amz-marketing-skill/
├── zoodata/
├── amazon-analysis/
├── amazon-competitor-intelligence-monitor/
├── amazon-daily-market-radar/
├── amazon-keywords/
├── amazon-listing-audit-pro/
├── amazon-market-entry-analyzer/
├── amazon-market-trend-scanner/
├── amazon-opportunity-discoverer/
├── amazon-pricing-command-center/
└── amazon-review-intelligence-extractor/
```

## 注意事项

- Sorftime MCP 的字段会被适配成原 ZooData CLI 的兼容输出。
- 某些 Sorftime 工具返回的是更宽泛的 keyword-only 数据，做正式决策前建议用更窄关键词复测。
- `reviews/analysis` 在 Sorftime MCP 下是兼容 fallback，不等同于 ZooData 的预聚合 11 维评论分析。
