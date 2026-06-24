---
name: ingredients-breakdown-compliance-check
description: 对保健品产品、ASIN、品牌、配方或成分进行结构化成分风险档案分析。用于审查 Supplement Facts、拆分嵌套成分行、分类通用/品牌/专有成分、评估商标/专利/合规/市场风险，并为下游安全重建准备交接信息。
---

# 成分拆解与合规审查

## 概述

当需要对保健品或健康产品的 Listing 进行结构化上游风险报告时，使用本 skill。

## 适用场景

当需要对保健品或健康产品的 Listing 进行结构化上游风险报告时使用本 skill。

- 支持通过自然语言在任意 agent 聊天中激活
- 输出固定结构的中文报告，可直接用于下游 prompt 或规划文档
- 不依赖特定 MCP 名称，兼容主流 agent 平台

## 识别目标

本 skill 是上游报告生成器，应识别：

- 产品中疑似存在的成分
- 哪些部分是通用的，哪些是品牌的或可能是专有的
- 商标、专利、合规和市场风险的位置
- 仍缺少哪些证据
- 下游安全重建工作流应保留、替换、规避或上报的内容

每次运行开始时，读取：

- `references/prompt-library.md`
- `references/workflow.md`
- `references/report-template.md`

需要固定输出的中文实际示例时，读取 `references/examples/b09zq74495-upstream.md`。
需要第二个中文实际示例（单成分、叙事密集型保健品）时，读取 `references/examples/b0dnbl1d2j-upstream.md`。

## 支持的输入

本 skill 适用于：

- `ASIN`
- 品牌名称
- 产品标题
- 成分名称
- `Supplement Facts`
- 成分面板文本
- Listing 截图

可选上下文：

- 目标市场
- 剂型
- 用户已知的成分表
- 特定的知识产权或合规关注点

## 工作流

1. 标准化目标和市场。
2. 从 Listing、官方网站、PDF、专利、文献和监管/IP 记录中收集最强的可用证据。
3. 将嵌套行拆分为营养素、品牌、来源/物种、工艺和剂量层。
4. 为非显而易见的成分和来源名称建立别名。
5. 按 `references/report-template.md` 中的确切顺序生成固定输出。
6. 当证据不完整时，在 `Missing Evidence Points` 中明确标注不确定性。
7. 以下游安全重建工作交接姿态结束。

## 输出要求

除非用户明确要求使用其他语言，否则始终以中文回答。保留精确的英文成分名称、标记、拉丁名称、法规编号和 URL。

始终包含以下章节：

1. `Executive Summary`（执行摘要）
2. `Input Snapshot`（输入快照）
3. `Observed Ingredient Table`（观察到的成分表）
4. `Ingredient Classification`（成分分类）
5. `Risk Matrix`（风险矩阵）
6. `Missing Evidence Points`（缺失证据点）
7. `Rebuild Posture Summary`（重建姿态总结）

## 证据规则

- 优先使用官方或一手来源，而非博客或转售商文案。
- 成分风险与宣称风险分开。
- 品牌来源层与宿主营养素层分开。
- 不要将缺少 `TM`、`(R)` 或类似商标标记作为某术语为通用术语的证据。
- 不要将结果呈现为法律建议或明确的自由实施许可。

## Web Search 兜底策略

当专用 MCP（Sorftime、AnySearch、Exa、Apify）不可用时，自动降级到 agent 内置网络搜索：

- 产品数据：`site:amazon.com {ASIN}` 或 `{产品名} supplement facts`
- 法规/IP：`USPTO {成分名} trademark`、`FDA {成分名} dietary supplement`
- 用户反馈：`site:reddit.com {成分名} supplement review`

降级时在报告中标注数据来源为 web search 兜底，建议关键决策前用 MCP 复核。

## 防护栏

- 不要指导用户复制受保护的成分系统。
- 不要将分层行合并为一个无差异的成分。
- 不要将亚马逊文案单独作为决定性法律证据。
- 除非官方来源直接支持，否则不要声称 FDA 批准。
- 优先使用"保留概念"、"替换"、"规避"和"法律审查"，而非模仿性语言。
