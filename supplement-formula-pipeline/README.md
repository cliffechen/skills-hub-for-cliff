# Amazon Supplement Ingredient × Traffic Boundary Analysis

面向 Amazon US 保健品类目的可复用分析平台。从 `Sif AI 关键词调研报告 + 锚定 ASIN + Supplement Facts` 出发，判断产品的核心主成分、可承接流量边界、成分延伸方向和合规/IP 风险，输出分析报告、方案对比、雷达图和候选 Supplement Facts。

项目包含两条并行工作流：

1. **Boundary Analysis 工作流**（`skills/amazon-supplement-boundary-analysis/`）— 从 Sif AI 关键词 Excel + 锚定 ASIN + Supplement Facts 出发，输出成分流量边界报告、方案对比、雷达图、候选 Supplement Facts。
2. **风险查验 → 安全重建 → 配方优化 → 受众收口 工作流**（`skills/` 下的 Skill 1-5）— 对产品成分做风险查验、安全替代方案设计和配方升级优化。

---

## Quick Start

```bash
python -m pip install -r requirements.txt
python scripts/check_portability.py
```

如果自检通过，项目即可在当前设备上用于任意 agent 平台的工作流。

详细设置文档：

- Agent 启动说明：`docs/agent-setup.md`
- Codex 启动说明：`docs/codex-setup.md`
- GitHub 上传前检查：`docs/github-upload-checklist.md`

---

## 项目结构

```text
.
├── AGENTS.md                                ← 通用项目指令
├── CLAUDE.md                                ← Claude Code 指针
├── SKILL.md                                 ← 套件/项目编排入口
├── PLATFORM-ADAPTER.md                      ← 跨平台适配指南
├── skills/
│   ├── ingredients-breakdown-compliance-check/  ← Skill 1：成分风险查验
│   │   ├── SKILL.md
│   │   └── references/
│   ├── supplement-safe-rebuild/                 ← Skill 2：安全重建
│   │   ├── SKILL.md
│   │   └── references/
│   ├── formula-reconstruction/                  ← Skill 3：配方优化
│   │   ├── SKILL.md
│   │   └── references/
│   ├── amazon-supplement-boundary-analysis/     ← Skill 4：成分流量边界分析
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   ├── assets/
│   │   ├── references/
│   │   └── scripts/
│   └── supplement-audience-satellite-formula-finalizer/  ← Skill 5：受众收口
│       ├── SKILL.md
│       ├── agents/
│       └── references/
├── scripts/
│   ├── check_portability.py                 ← 项目级环境自检
│   └── analyze_autocomplete.py              ← 亚马逊下拉框搜索词分析
├── docs/                                    ← 设置和检查文档
│
├── research-inputs/                         ← 调研前置文件暂存区（Sif Excel 等，Git 忽略）
│   └── {成分名}/                             ← 按成分分子文件夹存放
│
├── output-risk-check/                       ← Skill 1 交付物：上游风险查验报告
│   └── {成分名}/
│       └── {成分名}-upstream-risk-report.md
│
├── output-safe-rebuild/                     ← Skill 2 交付物：安全重建简报
│   └── {成分名}/
│       └── {成分名}-safe-rebuild-brief.md
│
├── output-formula-reconstruction/           ← Skill 3 交付物：配方优化方案 + SF HTML
│   └── {成分名}/
│       ├── {成分名}-formula-reconstruction.md
│       └── {成分名}-supplement-facts-{时间戳}.html
│
├── outputs/                                 ← Skill 4/5 运行产物（Git 忽略）
│   ├── cases/                               ← 正式案例交付物
│   │   └── {ASIN}-{核心成分}-{时间戳}/
│   │       ├── inputs/                      ← 案例输入文件
│   │       ├── sources/                     ← 中间数据源
│   │       ├── deliverables/                ← 最终交付物
│   │       └── scratch/                     ← 临时文件
│   └── scratch/                             ← 测试、中间稿
│
├── examples/                                ← 公开脱敏样例（进 Git）
│   └── ghk-cu-peptide-supplement/           ← 完整样例：Skill 1 + 2 + 3 全套
│
├── requirements.txt
└── README.md
```

### 文件夹职责速查

| 文件夹 | 用途 | 进 Git？ |
|---|---|---|
| `research-inputs/` | 调研前置文件暂存区（Sif Excel、截图等） | ❌ |
| `output-risk-check/` | Skill 1 交付物：上游风险查验报告 | ❌ |
| `output-safe-rebuild/` | Skill 2 交付物：安全重建简报 | ❌ |
| `output-formula-reconstruction/` | Skill 3 交付物：配方优化方案 + SF HTML | ❌ |
| `outputs/cases/` | Skill 4/5 正式案例交付物 | ❌ |
| `examples/` | 公开脱敏样例 | ✅ |
| `skills/` | 可复用能力定义（5 个 skill 的脚本、模板、参考文档） | ✅ |
| `docs/` | 设置和检查文档 | ✅ |

### 调研前置文件存放规则

每次开始新成分调研时，将 Sif Excel 等前置文件放到 `research-inputs/{成分名}/` 下：

```text
research-inputs/
  sam-e/
    Sif关键词调研-US-B071D973TN-2026-04-24 14点39分.xlsx
  urolithin-a/
    Sif关键词调研-US-BXXXXXXXXX-2026-XX-XX XX点XX分.xlsx
```

该文件夹被 `.gitignore` 忽略，不进入版本控制。

---

## 功能总览

**项目的 6 大核心功能模块：Skill 1 风险查验、Skill 2 安全重建、Skill 3 配方优化、Boundary Analysis 流量边界分析、MCP 数据查询、Python 脚本工具。**

### 功能 1：成分上游风险查验（Skill 1）

对指定 ASIN / 品牌 / 成分 / Supplement Facts 进行结构化风险分析，输出中文风险档案。覆盖商标风险、专利风险、合规风险、市场风险四个维度，并给出下游重建姿态建议。

**输出**：7 章节结构化报告（Executive Summary → Input Snapshot → Observed Ingredient Table → Ingredient Classification → Risk Matrix → Missing Evidence Points → Rebuild Posture Summary）

### 功能 2：安全重建方案设计（Skill 2）

基于 Skill 1 的风险档案，保留功能目标和品类线索，避开品牌成分、专利实现、高风险 claim，输出 2–3 个安全替代方向。

**输出**：7 章节结构化简报（Executive Summary → Rebuild Brief Snapshot → Functional Goal Map → Unsafe-to-Safe Substitution Map → Candidate Rebuild Directions → Claim Guardrails → Residual Risks & Required Review）

### 功能 3：配方优化升级（Skill 3）

基于 Skill 1/2 的交付物，从关键词竞争、市场需求、科学证据三个维度，设计具有竞争力的配方升级方案。输出分两层：**Tier A（消费者信号驱动，2-3 个方向）** 基于下拉框搜索词、评论、竞品截流等消费者行为数据；**Tier B（科学机制驱动，2 个方向）** 基于通路互补、协同研究等科学文献逻辑。包含流量边界分析和推广策略建议。

**输出**：9 章节结构化方案 + 可选 HTML Supplement Facts 标签（Executive Summary → Upstream Inheritance → Autocomplete Signal Analysis → Keyword Competition Matrix → Market Demand Insights → Scientific Evidence Table → Candidate Formula Directions [Tier A + Tier B] → Risk & Feasibility Notes → HTML Supplement Facts Label）

### 功能 4：成分流量边界分析（Boundary Analysis）

从 Sif AI 关键词 Excel 出发，结合 Sorftime 站内数据和站外交叉验证，判断产品的流量边界、成分延伸方向和合规风险，输出报告 + 方案对比 + 雷达图。

**输出**：成分流量边界报告、方案对比、雷达图（HTML + PNG）、候选 Supplement Facts

### 功能 5：MCP 数据查询

通过 Sorftime MCP 查询亚马逊站内数据（产品详情、关键词、竞品、趋势、评论等），通过 Exa MCP 查询站外信息（法规、文献、品牌官网），通过 Apify MCP 抓取 Reddit 用户讨论。

### 功能 6：Python 脚本工具

- **环境自检**：验证依赖、文件结构、脚本可运行性
- **案例工作区创建**：为每次分析创建隔离的文件夹结构
- **Sif Excel 解析**：提取关键词聚类、搜索量、相关性等结构化数据
- **雷达图生成**：从评分 JSON 生成 HTML + PNG 双格式雷达图
- **下拉框搜索词分析**：解析亚马逊搜索框下拉建议，提取四维配方设计信号（成分关联、剂量/强度、剂型偏好、人群/场景）

---

## 可直接调用的 Prompts

下面包含 21 个可直接调用的 Prompts，分为 6 类。每个 Prompt 都标注了【输入文件】和【交付物路径】，可以直接复制到 agent 对话框中使用。根据实际情况替换 `{占位符}` 中的内容。

**完整工作流（Prompt 1–2）：一键全流程调研、从成分名开始的调研**
**单步 Skill（Prompt 3–5）：分别调用 Skill 1/2/3**
**Boundary Analysis（Prompt 6–8）：流量边界分析、Sif Excel 解析、雷达图生成**
**MCP 数据查询（Prompt 9–12）：产品全景、关键词深度、类目市场、竞品对比**
**Supplement Facts 生成（Prompt 13–14）：HTML 标签生成、3 版变体**
**辅助功能（Prompt 15–20）：环境自检、案例创建、结果查看、文献检索、Reddit 挖掘、潜力选品**
**全维度配方开发（Prompt 21）：含下拉框信号的增强版 Skill 3**

---

### 一、完整工作流 Prompts

#### Prompt 1：一键完整调研（Skill 1 → Skill 2 → Skill 3 全流程）


> **【输入文件】**：无需文件，提供 ASIN 即可（Sorftime MCP 自动拉取数据）
> **【交付物路径】**：
> - `output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md`
> - `output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md`
> - `output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md`

```
请对 ASIN {B0XXXXXXXXX} 进行完整的补充剂成分调研。

Step 1：先用 sorftime MCP 获取产品详情（product_detail）、评论（product_reviews，正面和负面分开拉取）、流量词（product_traffic_terms）。

Step 2：激活 skill1（ingredients-breakdown-compliance-check），基于收集到的信息生成上游风险查验报告，保存到 output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md。

Step 3：激活 skill2（supplement-safe-rebuild），基于 Step 2 的输出生成安全重建简报，保存到 output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md。

Step 4：激活 skill3（formula-reconstruction），基于 Step 2 和 Step 3 的输出，结合关键词竞争数据、市场需求和科学文献，生成配方优化升级方案，保存到 output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md。
```

> 示例：将 `{B0XXXXXXXXX}` 替换为 `B0GLN695WP`，`{产品英文短名}` 替换为 `ghk-cu-peptide-supplement`。

---

#### Prompt 2：从成分名开始的完整调研

> **【输入文件】**：无需文件，提供成分英文名即可
> **【交付物路径】**：同 Prompt 1（自动按搜索到的产品命名）

```
请对成分「{成分英文名}」进行完整的补充剂调研。

先用 sorftime MCP 的 product_search 搜索 Amazon US 上含有该成分的热销产品，选取 Top 3 产品获取详情和评论。

然后按 skill1 → skill2 → skill3 的顺序完成全流程调研，所有交付物按项目规范保存。
```

> 示例：将 `{成分英文名}` 替换为 `Urolithin A`、`NMN`、`Spermidine` 等。

---

### 二、单步 Skill Prompts

#### Prompt 3：仅执行 Skill 1 — 上游风险查验

> **【输入文件】**：无需文件，提供 ASIN 即可（Sorftime MCP 自动拉取数据）
> **【交付物路径】**：`output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md`

```
请对 ASIN {B0XXXXXXXXX} 执行 skill1（上游风险查验）。

先用 sorftime MCP 获取 product_detail 和 product_reviews（正面+负面），然后激活 ingredients-breakdown-compliance-check，生成结构化风险档案。

输出保存到 output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md。
```

#### Prompt 4：仅执行 Skill 2 — 安全重建

> **【输入文件】**：`output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md`（Skill 1 输出）
> **【交付物路径】**：`output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md`

```
请基于已有的风险查验报告 output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md，执行 skill2（安全重建）。

激活 supplement-safe-rebuild，读取上游报告中的 Observed Ingredient Table、Ingredient Classification、Risk Matrix、Missing Evidence Points、Rebuild Posture Summary 五部分作为输入。

输出保存到 output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md。
```

#### Prompt 5：仅执行 Skill 3 — 配方优化升级

> **【输入文件】**：
> - `output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md`（Skill 1 输出）
> - `output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md`（Skill 2 输出）
> **【交付物路径】**：`output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md`

```
请基于已有的 Skill 1 和 Skill 2 交付物，执行 skill3（配方优化升级）。

输入文件：
- output-risk-check/{产品英文短名}/{产品英文短名}-upstream-risk-report.md
- output-safe-rebuild/{产品英文短名}/{产品英文短名}-safe-rebuild-brief.md

激活 formula-reconstruction，结合以下数据源：
1. sorftime MCP：product_traffic_terms、keyword_detail、keyword_trend、keyword_extends、competitor_product_keywords
2. sorftime MCP：product_reviews（正面+负面分开拉取）
3. exa MCP：搜索 PubMed、Examine.com、NIH ODS 等科学文献
4. 可选：Apify MCP 抓取 Reddit 讨论（r/Supplements、r/Nootropics 等）

输出保存到 output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md。
```

---

### 三、Boundary Analysis 工作流 Prompts

#### Prompt 6：完整成分流量边界分析

> **【输入文件】**：Sif AI 关键词调研 Excel（存放于 `research-inputs/{成分名}/`）
> **【交付物路径】**：`outputs/cases/{ASIN}-{核心成分}-{时间戳}/deliverables/` 下全部文件

```
请对 ASIN {B0XXXXXXXXX}（核心成分：{成分英文名}）执行完整的成分流量边界分析。

Sif Excel 文件路径：{Excel文件绝对路径}

请按以下步骤执行：
1. 运行 create_case_workspace.py 创建案例文件夹
2. 运行 analyze_sif_excel.py 解析关键词报告
3. 用 sorftime MCP 获取 product_detail、product_traffic_terms、competitor_product_keywords、keyword_detail、keyword_trend
4. 撰写成分流量边界报告和方案对比
5. 生成雷达图（HTML + PNG）

所有交付物保存到 outputs/cases/ 下的案例文件夹中。
```

#### Prompt 7：仅解析 Sif Excel 关键词报告

> **【输入文件】**：Sif AI 关键词调研 Excel（存放于 `research-inputs/{成分名}/`）
> **【交付物路径】**：指定的 `{输出目录路径}` 下生成 JSON + MD + CSV 文件

```
请解析 Sif AI 关键词调研 Excel 文件。

文件路径：{Excel文件绝对路径}
输出目录：{输出目录路径}
文件前缀：{asin小写}-sif

运行命令：
python skills/amazon-supplement-boundary-analysis/scripts/analyze_sif_excel.py "{Excel文件绝对路径}" --output-dir "{输出目录路径}" --name {asin小写}-sif

解析完成后，请总结关键词聚类分布、高相关词 Top 10、高搜索量低相关性的风险词。
```

#### Prompt 8：生成雷达图

> **【输入文件】**：评分 JSON（手动提供或从分析中生成）
> **【交付物路径】**：指定输出目录下的 `{前缀}-radar-chart.html` + `{前缀}-radar-chart.png`

```
请基于以下评分生成雷达图。

评分 JSON 内容：
{
  "title": "{产品名} 成分与流量边界雷达图",
  "subtitle": "评分范围 0-10",
  "axes": ["主成分锚定度", "功能闭环度", "流量延伸能力", "延伸合理性", "合规/IP安全性", "差异化/前瞻性"],
  "series": [
    {"name": "方案A: {方案名}", "scores": [8, 7, 6, 7, 9, 8], "color": "#e76f51"},
    {"name": "方案B: {方案名}", "scores": [7, 8, 7, 6, 8, 7], "color": "#2a9d8f"}
  ]
}

请将评分 JSON 保存为临时文件，然后运行 generate_radar.py 生成 HTML 和 PNG。
```

---

### 四、MCP 数据查询 Prompts

#### Prompt 9：产品全景分析

> **【输入文件】**：无需文件，提供 ASIN 即可
> **【交付物路径】**：直接在聊天中输出（无文件保存）

```
请用 sorftime MCP 对 ASIN {B0XXXXXXXXX} 进行全景分析：

1. product_detail — 获取产品标题、品牌、价格、评分、月销量、上架时间
2. product_reviews — 分别拉取正面评论（Positive）和负面评论（Negative）
3. product_traffic_terms — 获取产品的自然流量词
4. product_trend — 获取月销量趋势
5. competitor_product_keywords — 获取竞品在核心关键词下的曝光位置

请汇总为一份产品全景报告。
```

#### Prompt 10：关键词深度分析

> **【输入文件】**：无需文件，提供关键词即可
> **【交付物路径】**：直接在聊天中输出（无文件保存）

```
请用 sorftime MCP 对关键词「{关键词}」进行深度分析：

1. keyword_detail — 获取月搜索量、CPC、点击集中度等核心指标
2. keyword_trend — 获取搜索量和排名历史趋势
3. keyword_extends — 获取延伸词/长尾词
4. keyword_search_results — 获取搜索结果自然位产品清单

站点：US

请分析该关键词的竞争程度、进入难度和推广价值。
```

#### Prompt 11：类目市场分析

> **【输入文件】**：无需文件，提供类目关键词即可
> **【交付物路径】**：直接在聊天中输出（无文件保存）

```
请用 sorftime MCP 分析类目市场。

先用 category_name_search 搜索「{类目关键词}」找到对应的 nodeId，然后：

1. category_report — 获取 Top 100 产品数据
2. category_trend — 获取销量趋势（SalesCount）
3. category_keywords — 获取类目核心关键词

请分析该类目的市场规模、竞争格局、新品机会和进入门槛。
```

#### Prompt 12：竞品对比分析

> **【输入文件】**：无需文件，提供 ASIN 列表即可
> **【交付物路径】**：直接在聊天中输出（无文件保存）

```
请对以下 ASIN 进行竞品对比分析：

- {ASIN_1}
- {ASIN_2}
- {ASIN_3}

对每个 ASIN 用 sorftime MCP 获取 product_detail 和 product_traffic_terms，然后对比：
1. 价格、评分、月销量
2. 核心流量词重叠度
3. 各自独占的流量词
4. Supplement Facts 成分差异

输出一份结构化的竞品对比表。
```

---

### 五、Supplement Facts 生成 Prompts

#### Prompt 13：生成 HTML Supplement Facts 标签

> **【输入文件】**：手动提供配方信息（成分列表、剂量、剂型等）
> **【交付物路径】**：`output-formula-reconstruction/{产品英文短名}/{产品英文短名}-supplement-facts-{日期}-{时间}.html`

```
请基于以下配方信息生成 FDA 标准格式的 HTML Supplement Facts 标签：

产品名：{产品名}
剂型：{Capsules / Softgels / Tablets}
每瓶数量：{90}
每次用量：{2} {capsules/softgels}
每瓶份数：{45}

成分列表：
- {成分1}: {剂量} {单位}（{%DV 或 †}）
- {成分2}: {剂量} {单位}（{%DV 或 †}）
- {成分3}: {剂量} {单位}（{%DV 或 †}）

Other Ingredients: {辅料列表}

标签为英文、白底黑字、FDA 标准布局。
保存到 output-formula-reconstruction/{产品英文短名}/{产品英文短名}-supplement-facts-{日期}-{时间}.html。
```

#### Prompt 14：基于已有配方方向生成 3 版 Supplement Facts 变体

> **【输入文件】**：`output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md`（Skill 3 输出）
> **【交付物路径】**：`output-formula-reconstruction/{产品英文短名}/` 下生成 3 个 HTML 文件

```
请基于 output-formula-reconstruction/{产品英文短名}/{产品英文短名}-formula-reconstruction.md 中的 {Direction A/B/C}，生成 3 个 Supplement Facts 变体：

- 变体 1：保守版（最低有效剂量）
- 变体 2：标准版（中间剂量）
- 变体 3：高剂量版（文献支持的上限剂量）

每个变体都生成独立的 HTML 文件，遵循 FDA 标准格式。
默认包装：90 粒，默认剂型：{capsules/softgels}。
```

---

### 六、辅助功能 Prompts

#### Prompt 15：环境自检

> **【输入文件】**：无
> **【交付物路径】**：直接在终端输出

```
请运行项目环境自检：python scripts/check_portability.py

检查依赖是否安装、文件结构是否完整、脚本是否可运行。
```

#### Prompt 16：创建案例工作区

> **【输入文件】**：Sif Excel（存放于 `research-inputs/{成分名}/`）
> **【交付物路径】**：`outputs/cases/{ASIN}-{核心成分}-{时间戳}/`（自动创建）

```
请为 ASIN {B0XXXXXXXXX}（核心成分：{成分英文名}）创建案例工作区。

运行命令：
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py --asin {B0XXXXXXXXX} --core-ingredient "{成分英文名}" --sif-excel "{Sif Excel路径}"
```

#### Prompt 17：查看已有调研结果

> **【输入文件】**：无
> **【交付物路径】**：直接在聊天中输出

```
请列出 output-risk-check/、output-safe-rebuild/ 和 output-formula-reconstruction/ 下所有已完成的调研案例，汇总每个案例的：
1. 产品/成分名称
2. 已完成的 Skill 步骤（Skill 1/2/3）
3. 关键发现摘要（从 Executive Summary 中提取）
```

#### Prompt 18：站外科学文献检索

> **【输入文件】**：无需文件，提供成分英文名即可
> **【交付物路径】**：直接在聊天中输出

```
请用 exa MCP 搜索成分「{成分英文名}」的科学文献：

1. 搜索 PubMed / NIH ODS / Examine.com 上的系统综述和 RCT
2. 重点关注：口服有效剂量范围、生物利用度、安全性上限（UL）
3. 查找是否有相关专利（Google Patents）

输出一份结构化的科学证据摘要表，包含：成分名、有效剂量范围、证据等级、关键发现、来源。
```

#### Prompt 19：Reddit 用户需求挖掘

> **【输入文件】**：无需文件，提供成分英文名即可
> **【交付物路径】**：直接在聊天中输出

```
请用 Apify MCP 的 parseforge/reddit-posts-scraper 抓取 Reddit 上关于「{成分英文名}」的用户讨论。

目标 subreddit：r/Supplements、r/Nootropics、r/Fitness、r/aging、r/SkincareAddiction

请分析：
1. 用户最关心的功效方向
2. 常见的使用痛点和不满
3. 用户自发推荐的搭配成分
4. 对剂量和剂型的偏好

输出一份市场需求洞察摘要。
```

#### Prompt 20：潜力选品搜索

> **【输入文件】**：无需文件，提供筛选条件即可
> **【交付物路径】**：直接在聊天中输出

```
请用 sorftime MCP 搜索 Amazon US 上的潜力补充剂产品：

条件：
- 月销量 > {500}
- 价格 ${20}–${60}
- 评论数 < {200}（新品机会）
- 评分 > {4.0}
- 搜索名称：{supplement 关键词}

用 potential_product 或 product_search 工具搜索，按潜力指数排序。
输出 Top 10 产品清单，包含 ASIN、标题、价格、月销量、评分、评论数。
```

---

#### Prompt 21：全维度配方开发（Skill 3 增强版 — 含下拉框信号）

> **【输入文件】**（4 项全部提供才能形成全面的成分开发）：
> 1. **对标 ASIN 的成分表**（Supplement Facts 转文字版）— 手动从产品页面抄录或截图 OCR
> 2. **Sif 关键词拓展表**（Excel）— 存放于 `research-inputs/{成分名}/`
> 3. **上游市场调研报告**（Markdown）— 由 Product Research Skill 生成的市场总览分析，存放于 `research-inputs/{成分名}/`
> 4. **核心关键词下拉框搜索词**（`.txt`，每行一个）— 从亚马逊搜索框手动采集或用工具抓取，存放于 `research-inputs/{成分名}/`
>
> **【交付物路径】**：`output-formula-reconstruction/{产品英文短名}/` 下生成 `.md` 配方方案 + `.html` Supplement Facts

```
根据文件夹 "research-inputs/{成分名}" 下的所有前置调研信息，还有 ASIN:{B0XXXXXXXXX} 的 Supplement Facts（文字版）：

{粘贴 Supplement Facts 文字版内容}

从专利风险、关键词流量、消费者意图、相似功效成分横向拓展的角度出发，开发不脱离原核心成分和功效的 Supplement Facts。

请按以下顺序执行：
1. 读取 research-inputs/{成分名}/ 下的市场调研报告（.md）、Sif Excel、下拉框搜索词（.txt）
2. 运行 python scripts/analyze_autocomplete.py 解析下拉框搜索词，提取四维配方设计信号
3. 用 sorftime MCP 获取对标 ASIN 的产品详情、评论、流量词、竞品关键词
4. 用 exa MCP 搜索专利风险和科学文献
5. 激活 skill3（formula-reconstruction），综合所有数据源生成配方优化方案
6. 输出 Tier A（消费者信号驱动，2-3 个方向）+ Tier B（科学机制驱动，2 个方向）候选配方 + 对应的 HTML Supplement Facts 标签
```

> **使用说明**：
> - 成分表文字版需手动提供（从亚马逊产品页面复制或 OCR）
> - 下拉框搜索词可通过在亚马逊搜索框逐字母输入采集，或使用 AMZ Suggestion Expander 等工具批量抓取
> - 市场调研报告是上游 Product Research Skill 的交付物，如果没有可先用 Prompt 9（产品全景分析）替代
> - 四项输入中，下拉框搜索词和市场调研报告对配方设计影响最大，缺少任一项会降低方案质量

---

## MCP 数据层

| 层级 | 工具 | 用途 |
| --- | --- | --- |
| 表格层 | Excel MCP / openpyxl 脚本 | 读取 Sif Excel，拆关键词结构 |
| 站内层 | Sorftime MCP | 查 ASIN、关键词、竞品、趋势（优先使用） |
| 站外层 | Exa MCP | 查法规、科学资料、趋势、站外语义 |
| 社媒层 | Apify MCP | 抓 Reddit 讨论，用于市场需求挖掘 |

## 标准交付物

每次完整跑完一个成分/ASIN 后，交付物按以下结构沉淀：

```text
# Skill 1/2/3 交付物
output-risk-check/{产品英文短名}/
  {产品英文短名}-upstream-risk-report.md              ← Skill 1 输出

output-safe-rebuild/{产品英文短名}/
  {产品英文短名}-safe-rebuild-brief.md                 ← Skill 2 输出

output-formula-reconstruction/{产品英文短名}/
  {产品英文短名}-formula-reconstruction.md             ← Skill 3 输出
  {产品英文短名}-supplement-facts-*.html               ← HTML 标签

# Boundary Analysis 交付物
outputs/cases/{ASIN}-{核心成分}-{时间戳}/
  deliverables/
    {name}-ingredient-traffic-boundary-report.md
    {name}-solution-comparison.md
    {name}-radar-chart.html
    {name}-radar-chart.png
```

## 边界规则

- 不为了吃大流量词硬加成分
- 不把品牌词、专利叙事或 branded ingredient 当成普通成分自由使用
- 不使用疾病治疗、逆转衰老、修复器官等高风险 claim
- 不默认考虑采购难度、供应商、原料成本（由用户线下核实）
- Supplement Facts 草案必须标注为探索方案，不是最终法规标签或生产配方
- 风险查验不等于法律意见，安全重建不等于可直接生产的配方

## 默认参数

- 市场：Amazon US
- 品类：dietary supplement / health supplement
- 默认包装：90 粒
- 默认剂型：softgels 或 capsules
- 默认辅料：`Distilled Water, Maltitol Syrup, Maltitol Powder, Isomalt, Pectin, Citric Acid, Sodium Citrate, Natural Flavor, Natural Color, Carnauba Wax.`
- 输出语言：中文为主，保留英文品牌名、商标、拉丁学名、法规编号和 URL
