# supplement-audience-satellite-formula-finalizer

保健品配方链路的最终收口 skill。它在风险查验、安全重建、关键词分析和配方方向判断完成后，把已选方向整理成一份以受众为根基、可交给实验室初审的中文最终配方简报，并附带极简 Supplement Facts HTML。

## 在 pipeline 中的位置

推荐顺序：

1. `ingredients-breakdown-compliance-check`：成分、商标、专利和合规边界判断
2. `supplement-safe-rebuild`：在安全边界内做方向重建
3. `formula-reconstruction` 或 `amazon-supplement-boundary-analysis`：关键词、市场需求、评论和候选方向判断
4. `supplement-audience-satellite-formula-finalizer`：把已选方向收成最终配方简报和实验室对接清单

这个 skill 不替代上游风险工作。如果上游结论不完整，只能做保守收口，并明确标出待确认项。

## 必要输入

- 已选方向，例如 `方案 B`
- 参考 ASIN 或竞品
- 已确认的 Supplement Facts 或标签文字
- Sif 关键词解析结果
- Sorftime 产品详情、流量词、关键词详情和评论
- 上游风险报告与 safe rebuild 简报
- solution comparison 或 formula reconstruction 简报
- 目标剂型、规格、市场和渠道

## 受众证据门槛

正式收口前，至少应满足：

- 评论样本：至少 10 条，其中正面不少于 5 条、负面不少于 3 条
- 关键词聚类：至少 3 个有效聚类
- 目标人群画像：至少明确一个核心人群、触发场景和主要痛点
- 对标产品信息：至少一个 ASIN 的产品详情和 Supplement Facts

如果证据不足，应先补齐；用户明确要求跳过时，需要标注为保守版本。

## 输出内容

正式配方简报默认包含：

1. `执行摘要`
2. `受众根基：人群、场景、痛点`
3. `原产品核心承接`
4. `主星-卫星架构`
5. `精简配方建议`
6. `营养师视角功能审视`
7. `关键词与人群承接`
8. `声明边界`
9. `实验室对接清单`
10. `剩余风险与待确认问题`

同时生成一份极简 HTML Supplement Facts 标签，只保留：

- `Supplement Facts`
- `Other Ingredients`
- `Suggested Use`
- `Caution`

不要在 HTML 中加入营销文案、实验室说明、人群分析或配方解释，除非用户明确要求。

## 输出位置

正式输出写入当前案例目录：

```text
outputs/cases/{case}/deliverables/final/{name}-final-formula-brief.md
outputs/cases/{case}/deliverables/final/{name}-final-supplement-facts.html
```

默认只生成这两份成对交付物。

## 目录结构

```text
supplement-audience-satellite-formula-finalizer/
|-- README.md
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- references/
    |-- audience-first-framework.md
    |-- output-template.md
    |-- output-contract.md
    `-- lab-handoff-checklist.md
```

## 护栏

- 先做人群，再谈成分
- 非用户明确要求时，卫星卖点只加 1-2 个
- 不使用疾病、治疗或替代药物语义
- 不因为流量大就默认加入高风险成分
- 不覆盖上游 `avoid` 或 `legal review` 结论
- 不把草案写成已可直接生产的配方
- 不提供详细制造参数、供应商复制路径或 clone-ready BOM
