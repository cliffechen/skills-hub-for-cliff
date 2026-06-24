---
name: supplement-safe-rebuild
description: 将结构化的保健品成分风险档案转化为中文安全重建简报。当已有上游风险报告，需要在保留功能目标和品类线索的同时，避开品牌成分、专利关联实现、独占来源故事、高风险宣称和商业化暴露时使用。
---

# 保健品安全重建

## 概述

当上游风险报告已就绪时，使用本 skill。

## 适用场景

当已有上游风险报告，需要在保留功能目标的同时规避风险时使用本 skill。

- 支持通过自然语言在任意 agent 聊天中激活
- 输出固定结构的中文报告，可直接用于下游 prompt 或规划文档
- 不依赖特定 MCP 名称，兼容主流 agent 平台

本 skill 用于安全重建工作，而非反向复制。应保留：

- 功能目标
- 允许的品类线索
- 合理的营养逻辑

同时规避：

- 品牌成分名称
- 精确的受保护来源故事
- 专利关联的实现方式
- 高风险的骨密度或疾病相关宣称
- 市场化和商业化陷阱

每次运行开始时，读取：

- `references/prompt-library.md`
- `references/workflow.md`
- `references/output-template.md`

需要固定输出的中文实际示例时，读取 `references/examples/b09zq74495-rebuild.md`。
需要第二个中文实际示例（单成分但叙事密集型安全重建案例）时，读取 `references/examples/b0dnbl1d2j-rebuild.md`。

## 所需输入

优先使用五部分上游包：

- `Observed Ingredient Table`（观察到的成分表）
- `Ingredient Classification`（成分分类）
- `Risk Matrix`（风险矩阵）
- `Missing Evidence Points`（缺失证据点）
- `Rebuild Posture Summary`（重建姿态总结）

如果任何章节缺失，明确标注缺口并将不确定性向前传递，而非虚构安全结论。

## 工作流

1. 验证上游包。
2. 将功能层与受保护实现层分开。
3. 构建 `Functional Goal Map`（功能目标图）。
4. 构建 `Unsafe-to-Safe Substitution Map`（不安全到安全替换图）。
5. 起草 2 到 3 个 `Candidate Rebuild Directions`（候选重建方向）。
6. 添加 `Claim Guardrails`（宣称防护栏）。
7. 以 `Residual Risks & Required Review`（残留风险与必要审查）结束。

## 输出要求

除非用户明确要求使用其他语言，否则始终以中文回答。保留精确的英文标记、品牌名称、拉丁来源名称和 URL。

始终包含：

1. `Executive Summary`（执行摘要）
2. `Rebuild Brief Snapshot`（重建简报快照）
3. `Functional Goal Map`（功能目标图）
4. `Unsafe-to-Safe Substitution Map`（不安全到安全替换图）
5. `Candidate Rebuild Directions`（候选重建方向）
6. `Claim Guardrails`（宣称防护栏）
7. `Residual Risks & Required Review`（残留风险与必要审查）

## 防护栏

- 不要将结果呈现为法律建议。
- 不要解释逐条宣称的专利规避策略。
- 不要建议使用他人的商标或混淆性相似命名。
- 不要在没有充分证据的情况下声称等同于专有成分。
- 不要将结果转化为可克隆级 BOM 或制造工艺。
- 在宣称建议中优先使用保守的结构/功能语言，而非疾病或优越性宣称。
