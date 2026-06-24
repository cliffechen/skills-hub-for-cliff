---
name: supplement-formula-pipeline
description: Amazon US 保健品竞品分析与差异化配方开发全套工具链。包含 5 个串联 skill：成分风险查验、安全重建、配方优化、成分流量边界分析、受众卫星配方收口。从竞品 ASIN / Supplement Facts / Sif 关键词 Excel 出发，输出风险报告、安全替代方案、配方升级方案、雷达图和最终配方简报。适用于：竞品分析、差异化配方开发、成分 IP/合规风险识别、关键词流量边界判断、Supplement Facts 生成。
---

# Supplement Formula Pipeline — 保健品竞品分析与配方研发

## 概述

本项目是一套面向 Amazon US 保健品卖家的完整竞品分析与配方研发工具链，包含 5 个串联 skill：

| # | Skill | 作用 | 入口文件 |
|---|-------|------|----------|
| 1 | 成分风险查验 | 拆解成分、识别商标/专利/合规风险 | `skills/ingredients-breakdown-compliance-check/SKILL.md` |
| 2 | 安全重建 | 在安全边界内做方向重建 | `skills/supplement-safe-rebuild/SKILL.md` |
| 3 | 配方优化 | 关键词+市场需求+科学文献驱动的配方升级 | `skills/formula-reconstruction/SKILL.md` |
| 4 | 成分流量边界分析 | Sif 关键词解析+流量边界报告+雷达图 | `skills/amazon-supplement-boundary-analysis/SKILL.md` |
| 5 | 受众卫星配方收口 | 以受众为根基的最终配方简报+实验室清单 | `skills/supplement-audience-satellite-formula-finalizer/SKILL.md` |

## 快速启动

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 环境自检
python scripts/check_portability.py
```

详细启动说明见 `docs/agent-setup.md`。

## 核心工作流

### 流水线模式（Skill 1 → 2 → 3 → 5）

```
竞品 ASIN → Skill 1（风险查验）→ Skill 2（安全重建）→ Skill 3（配方优化）→ Skill 5（受众收口）
```

每个 skill 的输出是下一个 skill 的输入。可按需单独调用任意一步，也可一键全流程。

### 边界分析模式（Skill 4）

从 Sif AI 关键词 Excel + 锚定 ASIN + Supplement Facts 出发，独立输出：
- 成分流量边界报告
- 方案对比
- 雷达图（HTML + PNG，含权重评分）
- 候选 Supplement Facts

## MCP 数据层

| 层级 | 工具 | 用途 |
|------|------|------|
| 站内层 | Sorftime MCP | ASIN 详情、关键词、竞品、趋势（优先使用） |
| 站外层 | AnySearch MCP | 法规、科学文献、品牌官网（主要站外发现） |
| 站外备用 | Exa MCP | AnySearch 不可用时的备用 |
| 社媒层 | Apify MCP | Reddit 讨论抓取，用于市场需求挖掘 |

当所有 MCP 不可用时，自动降级到 agent 内置 web search（详见各 skill 的 Web Search 兜底策略章节）。

## 标准交付物

```text
output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md
output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md
output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md
output-formula-reconstruction/{产品英文短名}/{产品英文短名}-supplement-facts-*.html
outputs/cases/{ASIN}-{核心成分}-{时间戳}/deliverables/
```

## 雷达图评分维度与权重

| 维度 | 权重 | 理由 |
|------|------|------|
| 主成分锚定度 | 25% | 决定产品搜索身份和用户认知锚点 |
| 功能闭环度 | 20% | 配方功能逻辑自洽性，影响复购和口碑 |
| 流量延伸能力 | 15% | 承接相邻关键词流量的天花板 |
| 延伸合理性 | 15% | 延伸成分在科学和合规上是否站得住 |
| 合规/IP 安全性 | 15% | 法律底线，触发可能导致下架或诉讼 |
| 差异化/前瞻性 | 10% | 加分项而非生存项 |

## 常用脚本

```bash
# 创建案例工作区
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py \
  --asin <ASIN> --core-ingredient "<成分名>" --sif-excel "<Excel路径>"

# 解析 Sif Excel
python skills/amazon-supplement-boundary-analysis/scripts/analyze_sif_excel.py \
  "<Excel路径>" --output-dir "<输出目录>" --name <前缀名>

# 解析亚马逊下拉框搜索词
python scripts/analyze_autocomplete.py <suggestions.txt> \
  --output-dir <输出目录> --name <前缀名>

# 生成雷达图
python skills/amazon-supplement-boundary-analysis/scripts/generate_radar.py \
  <scores.json> --output-dir "<输出目录>" --name <前缀名>
```

## 默认参数

- 市场：Amazon US
- 品类：dietary supplement / health supplement
- 默认包装：90 粒（capsules 或 softgels）
- 输出语言：中文为主，保留英文品牌名、商标、拉丁学名、法规编号和 URL

## 边界规则

- 不为了吃大流量词硬加成分
- 不把品牌词、专利叙事或 branded ingredient 当成普通成分自由使用
- 不使用疾病治疗、逆转衰老、修复器官等高风险 claim
- 风险查验不等于法律意见，安全重建不等于可直接生产的配方
- Supplement Facts 草案必须标注为探索方案

## 参考文件

按需读取以下文件获取详细信息：

- `AGENTS.md` — 完整项目指令和技术栈说明
- `docs/agent-setup.md` — 各 agent 平台启动说明
- `docs/output-organization.md` — 输出组织规则
- `skills/*/references/` — 各 skill 的工作流、输出合同、评分标准等
