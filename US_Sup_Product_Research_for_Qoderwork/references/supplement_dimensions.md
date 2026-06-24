# 膳食补充剂（Dietary Supplement）分析维度定义

> 本文件定义场景 5（膳食补充剂定向分析）的属性标注维度、解析规则和交叉分析建议。
> 适用市场：Amazon US，品类：Dietary Supplements 大类。

---

## 维度总览

| # | 维度名称 | 解析来源 | 必选 | 用于交叉分析 |
|---|----------|----------|------|-------------|
| 1 | 成分大类 | 标题 + 五点 | ⛔ 是 | ✅ |
| 2 | 剂型 | 标题 | ⛔ 是 | ✅ |
| 3 | 剂量标注 | 标题 + 五点 | ⛔ 是 | ✅ |
| 4 | 功效方向 | 标题 + 五点语义 | ⛔ 是 | ✅（仅当标题未提及功效时做交叉） |
| 5 | 目标人群 | 标题 + 五点 | ⛔ 是 | ✅ |
| 6 | 包装规格 | 标题 | ⛔ 是 | ✅ |
| 7 | 认证标签 | 标题 + 五点 | ⛔ 是 | ✅ |
| 8 | 配方类型 | 标题 + 五点 | ⛔ 是 | ✅ |
| 9 | 价格带 | category_report | ⛔ 是 | ✅ |

---

## 维度 1：成分大类

按大类归类，不按具体成分。一个产品可能同时属于多个大类（如含 Vitamin D + Zinc 的复合产品归入「维生素类+矿物质类」），但主分类取标题中**最先出现**或**最突出**的成分所属大类。

| 大类 | 匹配关键词（标题/五点，不区分大小写） |
|------|--------------------------------------|
| 维生素类 | vitamin, vit, multivitamin, multi-vitamin, biotin, folate, folic acid, niacin, riboflavin, thiamine, retinol, tocopherol, ascorbic acid |
| 矿物质类 | mineral, calcium, magnesium, zinc, iron, selenium, chromium, potassium, iodine, copper, manganese |
| 草本/植物类 | ashwagandha, turmeric, curcumin, ginger, ginseng, echinacea, elderberry, milk thistle, saw palmetto, valerian, maca, rhodiola, berberine, fenugreek, black seed, moringa, green tea extract, garlic, oregano oil, mushroom, reishi, lion's mane, cordyceps, chaga |
| 氨基酸/蛋白类 | amino acid, collagen, protein, creatine, glutamine, l-theanine, l-carnitine, bcaa, taurine, glycine, NAC, n-acetyl cysteine |
| 益生菌/消化类 | probiotic, prebiotic, digestive enzyme, fiber, psyllium, lactobacillus, bifidobacterium, CFU |
| 脂肪酸类 | omega-3, omega 3, fish oil, krill oil, cod liver oil, DHA, EPA, flaxseed oil, algal oil |
| 抗氧化/抗衰类 | NMN, NR, NAD, CoQ10, coenzyme q10, resveratrol, astaxanthin, glutathione, PQQ, quercetin, urolithin, spermidine |
| 特殊功能类 | melatonin, 5-HTP, GABA, DHEA, glucosamine, chondroitin, MSM, hyaluronic acid, lutein, saw palmetto, biotin（高剂量美容用途时） |
| 复合/综合类 | multivitamin, multi, prenatal, postnatal, one-a-day, daily pack, greens powder, superfood |

**解析优先级**：标题 > 五点描述第一条 > 五点描述其余

**注意**：
- 如果标题中出现 "multivitamin" 或 "multi"，直接归入「复合/综合类」，不再拆分子成分
- 如果标题同时出现两个不同大类的成分（如 "Vitamin D3 + Zinc"），主分类取标题中先出现的，副分类记录第二个
- 「特殊功能类」是兜底分类，仅当产品不属于前 8 类时使用

---

## 维度 2：剂型

| 剂型 | 匹配关键词 |
|------|-----------|
| Capsules | capsule, capsules, veggie capsule, vegetable capsule, veg cap |
| Softgels | softgel, softgels, soft gel, liquid softgel |
| Gummies | gummy, gummies, gummi |
| Tablets | tablet, tablets, caplet, caplets |
| Powder | powder, mix, scoop |
| Liquid / Drops | liquid, drops, tincture, spray, syrup, elixir |
| Chewable | chewable, chew, lozenge |
| 其他/未知 | 以上均未匹配 |

**解析规则**：
- 正则：`\b(capsules?|softgels?|soft\s*gels?|gumm(?:y|ies|i)|tablets?|caplets?|powder|liquid|drops?|tincture|spray|chewable|chew|lozenge)\b`（不区分大小写）
- 标题中通常在产品名末尾或数量后出现，如 "Vitamin D3 5000 IU, 360 Softgels"
- 如果标题未提及剂型，从五点描述中提取

---

## 维度 3：剂量标注

**二分法**：仅区分「有标注剂量」和「无标注剂量」。

| 分类 | 判定规则 |
|------|----------|
| 有标注剂量 | 标题或五点中出现 `数字 + 剂量单位` 的组合 |
| 无标注剂量 | 标题和五点中均未出现可识别的剂量信息 |

**剂量单位正则**：
```
\d[\d,]*\.?\d*\s*(mg|mcg|µg|ug|IU|iu|CFU|cfu|billion\s*CFU|g|gram|ml|oz|ppm|mcg\s*DFE|mg\s*NE|RAE)
```

**常见格式示例**：
- `5000 IU` / `5,000IU` / `125 mcg (5000 IU)`
- `1000 mg` / `1,000mg`
- `50 Billion CFU` / `100B CFU`
- `600mg EPA / 400mg DHA`

**注意**：
- 包装数量（如 "360 Softgels"、"90 Count"）不是剂量，不要误判
- 正则需排除 `\d+\s*(count|ct|capsules|softgels|tablets|gummies|pack|bottle)` 的匹配
- 百分比（如 "95% Curcuminoids"）算作剂量标注

---

## 维度 4：功效方向

从标题和五点描述中的 claim 关键词推测功效方向。

| 功效方向 | 匹配关键词 |
|----------|-----------|
| 免疫支持 | immune, immunity, immune support, immune defense, immune health |
| 关节/骨骼健康 | joint, bone, joint support, bone health, joint health, flexibility, mobility, cartilage |
| 消化健康 | digestive, gut, gut health, digestion, bloating, regularity, probiotic（功效层面） |
| 能量/代谢 | energy, metabolism, metabolic, stamina, vitality, fatigue, B-complex（功效层面） |
| 抗氧化/抗衰 | antioxidant, anti-aging, longevity, cellular health, NAD, mitochondria, anti-inflammatory |
| 认知/脑健康 | brain, cognitive, memory, focus, mental clarity, nootropic, neuroprotection |
| 心血管健康 | heart, cardiovascular, blood pressure, cholesterol, circulation, CoQ10（功效层面） |
| 美容/皮肤/头发 | skin, hair, nails, beauty, collagen（功效层面）, glow, complexion, anti-wrinkle |
| 运动/健身 | workout, muscle, recovery, performance, pre-workout, post-workout, strength, endurance |
| 睡眠/放松 | sleep, relax, calm, stress, anxiety, mood, melatonin（功效层面）, GABA（功效层面） |
| 男性健康 | testosterone, prostate, male, men's health, libido（男性语境） |
| 女性健康 | prenatal, postnatal, menopause, PMS, women's health, fertility, hormonal balance |
| 儿童健康 | kids, children, toddler, pediatric, growing, development |
| 眼部健康 | eye, vision, lutein（功效层面）, macular, eye health |
| 体重管理 | weight, appetite, fat burn, thermogenic, keto, metabolism（体重语境） |
| 通用/未明确 | 标题和五点中无明确功效 claim |

**解析规则**：
- 一个产品可标注 1-3 个功效方向（如 "Immune & Energy Support"）
- 优先从标题提取；标题无功效 claim 时从五点描述提取
- 标注为「⚠️ 推测」——功效方向是从文本语义推测的，非官方分类
- 如果标题和五点均无功效 claim，标注为「通用/未明确」

---

## 维度 5：目标人群

| 人群 | 匹配关键词 |
|------|-----------|
| Men | men, men's, male, for men, man |
| Women | women, women's, female, for women, her |
| Kids | kids, children, child, toddler, baby, infant, pediatric |
| Seniors | senior, elderly, 50+, over 50, aging, mature |
| Athletes | athlete, sport, workout, gym, bodybuilding, fitness |
| Prenatal | prenatal, pregnancy, pregnant, expecting, postnatal, postpartum |
| 通用 | 以上均未匹配（大多数保健品不指定人群） |

**解析规则**：
- 正则匹配标题中的人群关键词
- 大多数产品为「通用」，这是正常的
- "Women's Multivitamin" → Women；"Men's Daily" → Men

---

## 维度 6：包装规格

| 规格段 | 判定规则 |
|--------|----------|
| ≤30ct | 数量 ≤ 30 |
| 31-60ct | 31 ≤ 数量 ≤ 60 |
| 61-90ct | 61 ≤ 数量 ≤ 90 |
| 91-120ct | 91 ≤ 数量 ≤ 120 |
| 121-180ct | 121 ≤ 数量 ≤ 180 |
| 180ct+ | 数量 > 180 |
| 未知 | 无法从标题提取数量 |

**正则**：
```
(\d[\d,]*)\s*(count|ct|capsules?|softgels?|gumm(?:y|ies|i)|tablets?|caplets?|chewables?|servings?|doses?|pack)
```

**注意**：
- "2 Pack" 或 "Pack of 2" 表示多瓶装，需要识别单瓶数量
- "90 Servings" 和 "90 Capsules" 含义不同（一份可能是 2 粒），但标题层面统一按数字归类
- 优先匹配最大的数字+单位组合（如 "Vitamin D3 5000 IU 360 Softgels" → 360ct）

---

## 维度 7：认证标签

| 标签 | 匹配关键词 |
|------|-----------|
| Non-GMO | non-gmo, non gmo, no gmo |
| Organic | organic, usda organic |
| Vegan | vegan, plant-based, plant based |
| Vegetarian | vegetarian |
| Gluten-Free | gluten-free, gluten free, no gluten |
| GMP | gmp, good manufacturing practice, cgmp |
| Third-Party Tested | third-party tested, third party tested, 3rd party, independently tested, USP verified, NSF certified |
| Dairy-Free | dairy-free, dairy free, lactose-free |
| Soy-Free | soy-free, soy free |
| Sugar-Free | sugar-free, sugar free, no sugar, zero sugar |
| Keto-Friendly | keto, keto-friendly |
| 无认证标签 | 以上均未匹配 |

**解析规则**：
- 一个产品可有多个认证标签（如 "Non-GMO, Vegan, Gluten-Free"）
- 标题和五点描述都要扫描
- 认证标签数量本身也是一个分析指标（标签越多通常定价越高）

---

## 维度 8：配方类型

| 类型 | 判定规则 |
|------|----------|
| 单一成分 | 标题中仅出现一种核心成分（如 "Vitamin D3 5000 IU"） |
| 复合配方 | 标题中出现 2+ 种成分，或含 "complex"、"blend"、"formula"、"with"（连接多成分） |
| 综合维生素 | 含 "multivitamin"、"multi"、"one-a-day"、"daily pack" |

**解析规则**：
- "Vitamin D3 with K2" → 复合配方
- "Turmeric Curcumin with BioPerine" → 复合配方（BioPerine 是辅助成分）
- "Vitamin D3 5000 IU" → 单一成分
- "Women's One Daily Multivitamin" → 综合维生素
- 综合维生素优先级高于复合配方（即含 "multi" 时直接归入综合维生素）

---

## 维度 9：价格带

直接从 `category_report` 返回的价格字段取值，按以下分段：

| 价格带 | 范围 |
|--------|------|
| ≤$10 | 价格 ≤ 10 |
| $10-20 | 10 < 价格 ≤ 20 |
| $20-30 | 20 < 价格 ≤ 30 |
| $30-50 | 30 < 价格 ≤ 50 |
| $50+ | 价格 > 50 |

---

## 推荐交叉分析组合

以下维度对在保健品类目中有较高的分析价值：

| 交叉组合 | 分析意义 |
|----------|----------|
| 成分大类 × 剂型 | 哪些成分偏好哪种剂型？Gummies 在哪些成分大类中渗透率高？ |
| 成分大类 × 价格带 | 不同成分大类的定价分布，发现高溢价或低价竞争的成分方向 |
| 剂型 × 价格带 | Gummies vs Capsules 的价格差异，剂型溢价空间 |
| 功效方向 × 配方类型 | 单一成分 vs 复合配方在不同功效方向的分布 |
| 目标人群 × 功效方向 | 不同人群关注的功效方向差异 |
| 认证标签数量 × 价格带 | 认证标签是否带来溢价？ |
| 成分大类 × 包装规格 | 不同成分的主流包装规格 |

**⛔ 至少完成 3 对交叉分析**，优先选择前 3 对（成分×剂型、成分×价格、剂型×价格）。

---

## 保健品壁垒评估特殊说明

在 Step 2.4 进入壁垒评估中，保健品类目的壁垒评估需注意：

| 壁垒类型 | 保健品特殊考量 |
|----------|---------------|
| Review 壁垒 | 保健品 Review 门槛通常较高（消费者重视口碑），Top10 均值可能 > 5000 |
| 资金壁垒 | 首批备货、检测、FBA 与广告启动成本，需考虑高端成分的单位成本压力 |
| 技术壁垒 | GMP 认证工厂是基本门槛；部分成分需要特殊工艺（如肠溶胶囊、缓释技术） |
| 合规壁垒 | ⚠️ 本 Skill 不做合规分析，仅标注「需另行评估 FDA/FTC 合规」 |
| 原料与检测壁垒 | 原料形态、COA、第三方检测、稳定性和批次一致性 |
| 品牌壁垒 | 保健品品牌忠诚度较高，消费者倾向复购信任品牌 |

**⛔ 合规壁垒一栏**：固定填写「需另行评估——本 Skill 不覆盖 FDA/FTC/专利/商标合规分析，请使用专用合规 Skill」。不做任何合规判断。
