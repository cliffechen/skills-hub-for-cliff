# Radar Scoring Rubric

Score each dimension from 0 to 10. Higher is better.

| Dimension | Meaning | High score means |
| --- | --- | --- |
| 主成分锚定度 | Whether the solution still centers on the core ingredient | Keywords and formula can clearly return to the anchor |
| 功能闭环度 | Whether ingredients form a coherent nutrition/function chain | Ingredients have distinct roles and explain each other |
| 流量延伸能力 | Whether the solution can carry adjacent keyword pools | Adjacent traffic is meaningful and not merely large |
| 延伸合理性 | Whether the ingredient/keyword extension feels natural | Users and Amazon can understand the relationship |
| 合规 / IP 安全性 | Whether risks are controlled | Avoids prohibited ingredients, disease claims, brands, patents |
| 差异化 / 前瞻性 | Whether the solution has future advantage | It is not a generic copy or ingredient pile |

## Current Default Radar Dimensions

Use these unless the user changes them:

```json
[
  "主成分锚定度",
  "功能闭环度",
  "流量延伸能力",
  "延伸合理性",
  "合规 / IP 安全性",
  "差异化 / 前瞻性"
]
```

## Scoring Discipline

- Explain every score in text.
- Do not score procurement, supplier availability, or ingredient cost by default.
- Lower compliance/IP score for branded ingredient names, patent-heavy ingredient stories, or drug/disease claims.
- Lower anchor score when a hot ingredient takes over the product identity.

## 维度权重定义

雷达图的六个维度采用不等权重，权重分配基于各维度对保健品产品竞争力的影响程度：

| 维度 | 权重 | 定义理由 |
| --- | --- | --- |
| 主成分锚定度 | 25% | 最核心维度。主成分决定产品的搜索身份和用户认知锚点，锚定失败则整个产品定位崩塌 |
| 功能闭环度 | 20% | 配方的功能逻辑是否自洽，成分之间是否形成协同而非堆料，直接影响复购和口碑 |
| 流量延伸能力 | 15% | 能在多大范围内承接相邻关键词流量，决定产品的天花板 |
| 延伸合理性 | 15% | 延伸的成分是否在科学和合规上站得住脚，防止为了流量硬加成分 |
| 合规/IP 安全性 | 15% | 法律底线，一旦触发可能导致下架或诉讼，但大多数情况下不是日常竞争的主要变量 |
| 差异化/前瞻性 | 10% | 加分项而非生存项。有差异化更好，但没有也不致命 |

### 加权总分计算

加权总分 = Σ(维度得分 × 权重)，满分 10 分。

在方案对比时，加权总分可作为快速排序参考，但不应替代对各维度的逐项审查。两个方案可能总分接近但风险分布完全不同。
