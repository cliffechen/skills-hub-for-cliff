# AMZOn-site-Keyword-Trend-Analysis

亚马逊站内关键词趋势选品 skill：**只看需求端、以趋势为主线**。丢一个种子词（或一个竞品 ASIN，或让它在类目里扫描），它会扩出周边候选词，判断每个词的需求是不是真的、在往哪走、新卖家能不能分到，并预测到你能上架的那个月（默认 +4–6 个月）这个词处在什么位置。

不看成本、利润、供应链、库存和广告盈亏——"推荐"只代表**需求面值得做**，是否立项还要你自己算账、找货。默认美国站、膳食补充剂优先，其他类目也能跑。

## 输入 → 处理 → 输出

| 环节 | 内容 |
|---|---|
| 输入 | 种子关键词 / 竞品 ASIN / 无种子扫描；上架提前期（默认 4–6 个月） |
| 处理 | 扩词 → 需求真实性 → 多源趋势诊断（7 类原型）→ 进入窗口（需求流向）→ 需求缺口 → 定性预测（三情景 + 证实/证伪信号） |
| 输出 | Excel（8 个 sheet）+ 离线 HTML 趋势图；每个候选词给 推荐 / 观察 / 放弃、预测与置信度、复查清单、功效/品牌红旗 |

## 依赖

- 三个 MCP：**卖家精灵（sellersprite）**、**SIF**、**Sorftime**，需各自在 Agent 客户端里配置好。
- Python 3.10+，`openpyxl`（生成 Excel）。HTML 为内联 SVG，无外部脚本，可离线打开。

## 关键规则（实测沉淀）

- **三家的搜索量都是 ABA，只算 1 个独立源**；结论至少要有 2 个独立源（站内搜索 / 类目或单品销量 / Google / TikTok）。
- **先剔除脉冲再判读**：单期超过中位数 2.5 倍且销量不跟随的尖峰会污染工具给出的同比和峰值月，必须用多年曲线复核。
- **类目节点从头部 ASIN 反查**（`asin_prediction` 的 `nodeIdPath`），不要按名称搜。
- 证据分级 FACT / ESTIMATE / ASSUMPTION / UNKNOWN；关键项 UNKNOWN 时结论最多"观察"。
- 功效与品牌词只做红旗提示，不改变趋势结论。

## 目录

```text
AMZOn-site-Keyword-Trend-Analysis/
├── SKILL.md                         # 铁律 + 第 0–9 步流程
├── README.md
├── references/
│   ├── tool-map.md                  # 每步对应的 MCP 工具、参数、已知坑
│   ├── trend-reading.md             # 脉冲剔除、7 类原型、季节性、领先-滞后、置信度、预测模板
│   ├── supplement-seeds.md          # 补剂种子词、场景词、季节日历
│   ├── output-schema.md             # payload JSON 结构
│   └── blocked-claims-default.json  # 功效方向黑名单（仅用于红旗）
└── scripts/
    ├── scan_flags.py                # 写入功效/品牌红旗
    ├── build_xlsx.py                # payload → Excel
    └── build_html.py                # payload → 离线 HTML 趋势报告
```

## 用法示例

```text
用 AMZOn-site-Keyword-Trend-Analysis 跑一下 "blue spirulina powder"，美国站，预计 5 个月后上架。
```
