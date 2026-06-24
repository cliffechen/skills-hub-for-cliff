# Example: B09ZQ74495 Upstream Report

Reuse this as a worked Chinese example. Replace product-specific facts when analyzing another target.

## 1. Executive Summary

审查对象：`B09ZQ74495`，Amazon US，`ALGAECAL` 基础版。  
总体判断：风险核心不在 `Calcium` 本身，而在 `AlgaeCal®` branded source、`Lithothamnion/Mesophyllum superpositum` 物种/来源故事，以及骨密度增长类强 claim。  
最大确认风险：品牌源料层 + exclusive source story + 强 clinical efficacy 话术。  
最大未闭环问题：公开证据尚不足以完全闭环其当前可执行专利/独占范围。

## 2. Input Snapshot

- 输入类型：`ASIN`
- 市场：Amazon US
- 材料：listing、官网基础版页、HCP PDF、物种页、MSA、Google Patents、PubMed
- 证据质量：以官方页和文献为主，强于单一 listing

## 3. Observed Ingredient Table

| ingredient_name | alias | source_or_form | dosage_if_visible | claim_link | confidence |
| --- | --- | --- | --- | --- | --- |
| Calcium | plant-based calcium | `as AlgaeCal® L. superpositum` | `750 mg / 3 capsules` | bone strength, bone density | Strong |
| `AlgaeCal®` | `AlgaeCal(R)` | branded source layer | not separately disclosed | hero source identity | Strong |
| `Lithothamnion superpositum` / `Mesophyllum superpositum` | South American red algae | species/source layer | not separately disclosed | 13 minerals, exclusive algae story | Moderate |
| Magnesium | native magnesium | `as AlgaeCal® source` | `65 mg / 3 capsules` | partner nutrient | Strong |
| Vitamin D3 | cholecalciferol | added vitamin | `25 mcg (1000 IU)` | calcium absorption | Strong |

## 4. Ingredient Classification

| ingredient_name | category | why |
| --- | --- | --- |
| Calcium | `generic` | 通用营养素 |
| Magnesium | `generic` | 通用营养素 |
| Vitamin D3 | `generic` | 通用维生素 |
| `AlgaeCal®` | `branded` | 注册标记与品牌使用明显 |
| `Lithothamnion/Mesophyllum superpositum` | `likely proprietary` | 与独家红藻和 owner-specific 故事绑定 |

## 5. Risk Matrix

| ingredient_name_or_claim | TM_risk | patent_risk | compliance_risk | marketplace_risk | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `AlgaeCal®` | high | medium | medium | medium | Strong | branded layer，不宜复用 |
| exact species/source story | low | medium | medium | medium | Moderate | official materials tie it to exclusivity |
| `only calcium supplement clinically supported to increase bone density` | low | low | high | high | Strong | 高敏感优效表达 |
| `increase BMD` / fracture-adjacent wording | low | low | high | high | Strong | 靠近疾病和临床结果表达 |

## 6. Missing Evidence Points

| question | why_it_matters | best_next_document_or_source |
| --- | --- | --- |
| 商标注册范围多宽？ | 决定 branded wording 禁区 | USPTO record |
| 当前可执行专利边界是什么？ | 决定 patent risk 真实强度 | claim-by-claim patent review |
| 两个物种命名是否同一商业对象？ | 决定 source layer 是否必须完全避开 | taxonomy / supplier dossier |

## 7. Rebuild Posture Summary

| item | posture | rationale |
| --- | --- | --- |
| `Calcium` | `keep concept` | 通用营养素层 |
| `Vitamin D3` | `keep concept` | 常规协同 |
| algae-derived calcium category cue | `keep concept` | 仅保留通用品类层 |
| `AlgaeCal®` | `avoid` | branded source |
| exact species/source line | `legal review` | exclusivity and taxonomy uncertainty |
| bone density increase claim | `avoid` | high compliance risk |
