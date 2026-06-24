# GHK-Cu Peptide Supplement 上游风险查验报告

## 1. Executive Summary

审查对象：`B0GLN695WP`，Amazon US，品牌 `DQQI`，产品名 `GHK-Cu Copper Peptide Supplement, 120 Vegan Capsules`。  
总体判断：**低至中等风险**。GHK-Cu（铜肽 glycyl-L-histidyl-L-lysine copper complex）本身是一种已被广泛研究的天然三肽-铜络合物，不属于任何单一品牌的专有成分。该产品配方极度简单——仅含 GHK-Cu 120 mcg + 微晶纤维素 + 素食胶囊壳，无品牌源料层、无专利配方组合、无复杂成分嵌套。  
最大确认风险：**剂量极低**（120 mcg/粒，建议每日 2 粒 = 240 mcg），远低于文献中常见的口服研究剂量（通常 mg 级别），可能引发功效质疑和差评风险；listing 中的 claim（skin repair、anti-aging、hair growth support）在此剂量下缺乏充分临床支撑。  
最大未闭环问题：GHK-Cu 口服补充剂的生物利用度和有效口服剂量尚无充分的人体临床共识；该产品标注 `Primary Supplement Type: Magnesium` 属性与实际成分不符，存在合规隐患。

## 2. Input Snapshot

- 输入类型：ASIN + Supplement Facts 文本 + Sif AI 关键词调研 Excel
- 市场：Amazon US
- 材料：Amazon listing 详情、Supplement Facts、用户评论（1 条差评）、Sorftime 流量词数据、Sif 关键词报告（110 个高/中/低相关词 + 986 个几乎不相关词）
- 证据质量：以 Amazon listing 和站内数据为主，缺乏品牌官网、第三方检测报告、专利文献等深层证据

## 3. Observed Ingredient Table

| ingredient_name | alias | source_or_form | dosage_if_visible | claim_link | confidence |
| --- | --- | --- | --- | --- | --- |
| GHK-Cu (Copper Peptide) | glycyl-L-histidyl-L-lysine copper complex; 铜肽; 铜三肽 | 合成三肽-铜络合物，胶囊剂型 | 120 mcg / capsule（建议 2 粒/日 = 240 mcg） | skin repair, radiant skin elasticity, anti-aging, hair growth support | Strong |
| Microcrystalline Cellulose | MCC; 微晶纤维素 | 填充辅料 | 未标注 | 无功能声称 | Strong |
| Vegetarian Capsule | 素食胶囊壳 | HPMC 或类似植物胶囊 | N/A | vegan 卖点 | Strong |

## 4. Ingredient Classification

| ingredient_name | category | why |
| --- | --- | --- |
| GHK-Cu (Copper Peptide) | `generic` | GHK-Cu 是一种天然存在的三肽-铜络合物（首次由 Loren Pickart 于 1973 年从人血浆中分离），化学结构已公开，不属于任何单一品牌的注册商标成分。多家供应商可提供合成 GHK-Cu 原料。 |
| Microcrystalline Cellulose | `generic` | 通用药用辅料，USP/NF 标准品 |
| Vegetarian Capsule | `generic` | 通用植物胶囊壳 |

## 5. Risk Matrix

| ingredient_name_or_claim | TM_risk | patent_risk | compliance_risk | marketplace_risk | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GHK-Cu (Copper Peptide) 成分本身 | low | low | low | low | Strong | 通用三肽，无品牌独占。Loren Pickart 早期专利（US 5,382,431 等）已过期。 |
| "Promotes Skin Repair" claim | low | low | medium | medium | Moderate | 口服 GHK-Cu 在 120 mcg 剂量下的皮肤修复功效缺乏人体临床证据支撑，可能被视为 misleading claim |
| "Anti-Aging" claim | low | low | medium | medium | Moderate | anti-aging 属于常见 structure/function claim，但需要有合理科学依据支撑；此剂量下证据薄弱 |
| "Hair Growth Support" claim | low | low | medium | high | Moderate | hair growth 是高敏感 claim 领域，竞争激烈且消费者期望高；口服 GHK-Cu 促进毛发生长的临床证据极为有限 |
| "High Potency" 标题用语 | low | low | medium | medium | Strong | 120 mcg 标注为 "High Potency" 缺乏行业标准支撑，可能被质疑为虚假宣传 |
| 属性标注 `Primary Supplement Type: Magnesium` | low | low | high | medium | Strong | 产品实际不含镁，属性填写错误，违反 Amazon 产品信息准确性要求，存在被下架或投诉风险 |
| 剂量合理性（120 mcg/capsule） | low | low | medium | high | Moderate | 文献中 GHK-Cu 外用浓度通常为 ppm 级别，口服研究多在 mg 级别；120 mcg 可能不足以产生可感知效果，已有差评反映"无效" |

## 6. Missing Evidence Points

| question | why_it_matters | best_next_document_or_source |
| --- | --- | --- |
| GHK-Cu 口服的有效剂量范围是多少？ | 决定当前 120 mcg 剂量是否具有功能意义，直接影响 claim 合理性 | PubMed 系统综述、口服 GHK-Cu 人体临床试验（如有） |
| GHK-Cu 口服生物利用度如何？ | 三肽口服后是否能被完整吸收并发挥活性，决定口服剂型的可行性 | 药代动力学文献、动物/人体吸收研究 |
| DQQI 品牌的第三方检测报告是否存在？ | listing 声称 "third-party tested"，但无公开证据 | 品牌官网、CoA 文件、NSF/USP 认证记录 |
| 产品属性中 `Primary Supplement Type: Magnesium` 是否为误填？ | 属性与实际成分不符可能导致 Amazon 合规问题 | Amazon Seller Central 产品属性核实 |
| 是否有其他品牌持有 GHK-Cu 口服补充剂相关的活跃专利？ | 虽然早期专利已过期，但需确认是否有新的配方/递送专利 | Google Patents、USPTO 检索 |
| Neurogan 品牌（竞品）是否对 GHK-Cu 补充剂品类有任何 IP 主张？ | Neurogan 在 GHK-Cu 关键词下占据高流量份额（Top3 点击集中度 84.4%），需了解其市场地位是否涉及 IP 壁垒 | Neurogan 官网、USPTO 商标/专利检索 |

## 7. Rebuild Posture Summary

| item | posture | rationale |
| --- | --- | --- |
| GHK-Cu (Copper Peptide) 成分概念 | `keep concept` | 通用三肽-铜络合物，无品牌独占，可自由使用 |
| 口服胶囊剂型 | `keep concept` | 口服补充剂是合法品类，但需解决剂量和生物利用度问题 |
| 120 mcg 剂量设定 | `replace` | 剂量过低，建议参考文献确定合理口服剂量（可能需提升至 mg 级别），或改用更高效的递送方式 |
| "High Potency" 宣称 | `avoid` | 在当前剂量下无法支撑此声称 |
| "Skin Repair / Anti-Aging" claim | `keep concept` | 可保留方向但需调整措辞，确保有合理科学依据支撑 |
| "Hair Growth Support" claim | `legal review` | 高敏感领域，需确认口服 GHK-Cu 在目标剂量下是否有足够证据支撑此 claim |
| Microcrystalline Cellulose 辅料 | `keep concept` | 通用辅料，无风险 |
| Vegetarian Capsule | `keep concept` | 素食胶囊是市场正面卖点 |
| 产品属性准确性 | `replace` | 必须修正 `Primary Supplement Type` 为正确分类（Peptide / Copper Peptide） |
| 配方复杂度 | `replace` | 当前配方过于单一（仅 GHK-Cu），建议考虑添加协同成分以增强功能闭环和市场竞争力 |
