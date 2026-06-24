---
name: formula-reconstruction
description: 将上游风险报告和安全重建简报转化为科学支持、市场驱动、关键词优化的配方升级方案。当已有 Skill 1（合规查验）和 Skill 2（安全重建）输出，需要决定如何让新配方比对标产品更有竞争力时使用。
---

# 配方重构

## 概述

当两份上游交付物均已就绪时，使用本 skill：

- Skill 1 输出：`{name}-upstream-risk-report.md`
- Skill 2 输出：`{name}-safe-rebuild-brief.md`

## 适用场景

当已有 Skill 1（合规查验）和 Skill 2（安全重建）输出，需要决定如何让新配方比对标产品更有竞争力时使用本 skill。

- 支持通过自然语言在任意 agent 聊天中激活
- 输出固定结构的中文报告，可直接用于下游 prompt 或规划文档
- 不依赖特定 MCP 名称，兼容主流 agent 平台

本 skill 是**进攻性优化层**。Skill 2 回答"如何安全"；
本 skill 回答"如何赢"——在 Skill 2 已定义的安全边界内。

通过三角定位三个维度来做配方决策：

1. **关键词竞争** — 哪些搜索词在亚马逊上具有最佳的流量/竞争比，
   以及配方应如何与这些词对齐以获取广告和自然排名优势。
2. **市场需求** — 真实消费者实际需要什么、抱怨什么、
   希望存在什么，来源包括亚马逊评论、Reddit 讨论和网络研究。
3. **科学证据** — 哪些成分、剂量和组合
   在有效水平上有可信文献支持。

每次运行开始时，读取：

- `references/prompt-library.md`
- `references/workflow.md`
- `references/output-template.md`

## 所需输入

1. Skill 1 输出（上游风险报告）— 重点关注：
   - Observed Ingredient Table（观察到的成分表）
   - Ingredient Classification（成分分类）
   - Risk Matrix（风险矩阵）
2. Skill 2 输出（安全重建简报）— 重点关注：
   - Functional Goal Map（功能目标图）
   - Unsafe-to-Safe Substitution Map（不安全到安全替换图）
   - Candidate Rebuild Directions（候选重建方向）
3. 用于竞争上下文的目标关键词或 ASIN
4. **自动补全建议**（`.txt`，每行一个）— 亚马逊搜索栏
   下拉词，针对种子产品/成分。通过
   `scripts/analyze_autocomplete.py` 分析以提取四个配方设计
   信号维度（成分关联、剂量/强度、剂型、人群/场景）。
5. **Sif 关键词 Excel** — 目标 ASIN 的 Sif AI 关键词研究报告
6. **产品研究报告**（上游 Skill：Product Research）— 由先前
   研究工作流产出的市场概览 markdown

## 数据源

### 关键词竞争（亚马逊）
- **sorftime MCP**：`product_traffic_terms`、`keyword_detail`、`keyword_trend`、
  `keyword_extends`、`keyword_search_results`、`competitor_product_keywords`
- 关键指标：月搜索量, ABA 周排名, SPR (进入难度), PPC 竞价,
  点击集中度, 搜索结果自然位产品数

### 市场需求（消费者洞察）
- **sorftime MCP**：`product_reviews`（正面 + 负面分开拉取）,
  `similar_product_feature`、`category_report`
- **Apify MCP**：`parseforge/reddit-posts-scraper` — 搜索目标成分或
  产品在 r/Supplements, r/Nootropics, r/Fitness, r/aging 等
  subreddit 的真实用户讨论
- **exa MCP**：`web_search_exa` — 搜索消费者论坛、健康博客、
  新闻中的需求信号和趋势

### 科学证据
- **exa MCP**：`web_search_exa` — 搜索 PubMed, Examine.com,
  NIH ODS, Cochrane Library 等权威来源
- **web search / web fetch**：补充获取具体文献摘要和剂量数据

## 工作流

1. **读取上游交付物** — 确认安全边界和可用成分池。
2. **自动补全信号分析** — 运行 `scripts/analyze_autocomplete.py`
   解析下拉框搜索词，提取四维配方设计信号（成分关联、剂量/强度、剂型偏好、
   人群/场景）。这些信号是消费者用搜索行为表达的真实需求，优先级高于
   纯科学机制推导。
3. **关键词竞争分析** — 找到最优推广锚定词。
4. **市场需求挖掘** — 从三个渠道提取用户痛点和未满足需求。
5. **科学验证** — 为候选成分找到文献支持和有效剂量。
6. **配方方向综合** — 综合五个维度输出两层配方方向：
   - **Tier A（消费者信号驱动）**：2-3 个方向，成分选择优先级为
     消费者搜索信号 > 竞品广告截流信号 > 评论中的成分提及 > 科学机制互补
   - **Tier B（科学机制驱动）**：2 个方向，成分选择基于通路互补、
     协同研究和文献支持的组合逻辑，作为补充视角
7. **保存交付物** — 保存到 `formula-reconstruction-result/{name}/` 下，命名为 `{name}-formula-reconstruction.md`。
8. **HTML Supplement Facts 标签** — 用户确认配方方向后，生成独立 HTML 标签文件（英文、白底黑字、FDA 标准格式），文件名含生成日期和时间。

## 输出要求

除非用户明确要求使用其他语言，否则始终以中文回答。
保留精确的英文成分名称、品牌标记、拉丁名称、关键词术语和 URL。

始终包含以下章节：

1. `Executive Summary`（执行摘要）
2. `Upstream Inheritance`（上游继承）
3. `Autocomplete Signal Analysis`（自动补全信号分析）
4. `Keyword Competition Matrix`（关键词竞争矩阵）
5. `Market Demand Insights`（市场需求洞察）
6. `Scientific Evidence Table`（科学证据表）
7. `Candidate Formula Directions`（候选配方方向）
8. `Risk & Feasibility Notes`（风险与可行性说明）
9. `HTML Supplement Facts Label`（HTML 成分标签）— 作为独立 `.html` 文件生成，
   **仅在**用户确认配方方向后生成。文件名格式：
   `{name}-supplement-facts-{YYYY-MM-DD}-{HHmm}.html`。仅英文，
   白底，FDA 标准布局。详见 `references/workflow.md`
   步骤 7 和 `references/output-template.md` 第 9 节完整规格。

## 核心策略原则

- **关键词决定推广方向，不决定配方安全性** — 安全性由 Skill 1/2 兜底。
- **"打竞品词但成分更强"** 是核心策略 — 例如广告打 "osteo biflex triple
  strength" 但做 4X/5X 成分，让产品在成分上更有竞争力。
- **蓝海词优先** — 优先选择 SPR 低、PPC 便宜、搜索量适中的关键词作为
  推广锚点，而非一味追求最大搜索量的红海词。
- **科学性是底线** — 不能为了关键词竞争力加入没有文献支持的成分。
- **输出是配方方向决策简报，不是制造配方** — 不提供精确的制造工艺或
  克隆级 BOM。

## 防护栏

- 不要生产可克隆级的制造配方或 BOM。
- 不要推荐上游报告中标记为"规避"的品牌或专有成分。
- 不要使用疾病、治疗或优越性宣称。
- 不要将关键词排名预测呈现为保证结果。
- 不要忽视 Skill 1 和 Skill 2 设定的安全边界。
- 在所有宣称建议中优先使用保守的结构/功能语言。
