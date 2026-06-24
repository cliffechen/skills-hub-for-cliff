# Example: B0DNBL1D2J Fatty15 Upstream Report

Reuse this as a worked Chinese example. Replace product-specific facts when analyzing another target.

## 1. Executive Summary

审查对象：`B0DNBL1D2J`，Amazon US，`Fatty15 C15:0 Pentadecanoic Acid Supplement`，审查日期为 2026 年 4 月 5 日。  
总体判断：这个产品的风险重心不在“单一成分补充剂”本身，而在 `fatty15` 品牌系统、`FA15(TM)` branded ingredient 身份、`essential fatty acid` 定位、以及 `longevity / mitochondria / liver / 3X vs fish oil` 这一整层高敏感 claim 叙事。  
最大确认风险：`FA15(TM)` 与 `fatty15` 的品牌/授权体系，以及 DiscoverC15/Seraphina 对 C15:0 商业化和 use claims 的强专利故事。  
最大未闭环问题：当前公开材料还不足以证明 generic `pentadecanoic acid / C15:0` 在目标商业场景下与其专利/授权体系完全切开。

## 2. Input Snapshot

- 输入类型：`ASIN`
- 市场：Amazon US
- 材料：Amazon listing、fatty15 官网 `FA15` 页、fatty15 science 页、DiscoverC15 patents 页、3 篇 PubMed 文献
- 证据质量：品牌官方页与 PubMed 证据较强，专利覆盖边界仍需进一步法律复核

## 3. Observed Ingredient Table

| ingredient_name | alias | source_or_form | dosage_if_visible | claim_link | confidence |
| --- | --- | --- | --- | --- | --- |
| Pentadecanoic acid | `C15:0` | generic chemical ingredient layer | listing dose not fully visible; official science materials often discuss `100 mg/day`, human RCT used `200 mg/day` | cellular health, metabolism, liver, gut, mitochondria | Moderate |
| `FA15(TM)` | pure C15:0 powder | branded ingredient layer | not separately disclosed on listing panel in reviewed materials | hero ingredient identity | Strong |
| `fatty15` | product and brand name | brand system | not applicable | longevity nutrient story | Strong |
| Vegan capsule | capsule shell | delivery layer | not highlighted | delivery only | Low |

## 4. Ingredient Classification

| ingredient_name | category | why |
| --- | --- | --- |
| Pentadecanoic acid / `C15:0` | `generic` | 通用化学成分名本身可在更广语境下出现 |
| `FA15(TM)` | `branded` | 官网明确把它作为 pure branded C15:0 powder 使用 |
| `fatty15` | `branded` | 产品和品牌名 |
| `The Longevity Nutrient` | `likely proprietary` | 强 owner-specific 营销身份，不是通用成分名 |
| capsule shell | `unclear` | 当前公开材料里具体配方细节不足 |

## 5. Risk Matrix

| ingredient_name_or_claim | TM_risk | patent_risk | compliance_risk | marketplace_risk | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `FA15(TM)` | high | high | medium | medium | Strong | 品牌原料层，且与专利/授权故事强绑定 |
| `fatty15` brand system | high | medium | medium | medium | Strong | house brand and product identity |
| `pentadecanoic acid / C15:0` as generic ingredient | low | medium | medium | medium | Moderate | 成分名偏 generic，但 use/commercialization 仍可能交叉到现有专利池 |
| `C15:0 is an essential fatty acid` | low | low | high | high | Moderate | 2024 mini-review 认为其 essentiality 仍具争议 |
| `3X cellular benefits of fish oil` | low | low | high | high | Strong | comparative superiority claim |
| `slow aging / repairs cells / activates key longevity pathways` | low | low | high | high | Strong | longevity and repair language is highly sensitive |
| `liver support / fatty liver / mitochondrial health` | low | low | high | high | Strong | Amazon and FDA claim exposure both rise here |

## 6. Missing Evidence Points

| question | why_it_matters | best_next_document_or_source |
| --- | --- | --- |
| 当前最终 Supplement Facts 和辅料表是什么？ | 需要闭环 label-level identity review | final label images or official panel |
| DiscoverC15 / Seraphina 的专利 claims 具体覆盖到什么 use/commercialization 场景？ | 决定 C15:0 generic concept 是否能安全商业化 | claim-by-claim patent review |
| `FA15(TM)` 的注册与保护范围到底多宽？ | 决定 ingredient naming red lines | USPTO trademark record |
| `essential fatty acid` 定位是否足够稳？ | 决定 claim posture 能否保留 | broader literature and regulatory review |

## 7. Rebuild Posture Summary

| item | posture | rationale |
| --- | --- | --- |
| `pentadecanoic acid / C15:0` generic chemistry concept | `keep concept` | 可保留概念，但商业化前仍需 patent/legal review |
| `FA15(TM)` | `avoid` | 明确 branded ingredient |
| `fatty15` | `avoid` | 明确品牌名 |
| `essential fatty acid` framing | `legal review` | 文献仍有争议，claim 风险高 |
| `longevity / repairs cells / 3X vs fish oil` | `avoid` | claim 风险太高 |
| broad cellular wellness direction | `replace` | 可保留大方向，但需更保守语言 |
| liver / mitochondrial claims | `replace` | 需大幅收窄，不建议原样继承 |
