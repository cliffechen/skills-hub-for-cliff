# Amazon Listing 优化指南（A9/A10 + COSMO + Alexa Shopping）

本文件定义了 2025-2026 年 Amazon 美国站 Listing 优化的四大系统要求和最佳实践。所有 SEO 优化建议必须同时兼顾这些系统。

> **2026 年重要变化**：Rufus AI 已整合进 Alexa Shopping（购物版 Alexa），融合了 Rufus 的产品专业知识 + Alexa 的个性化能力（购物历史、对话历史、Alexa+ 上下文），成为更强大的 AI 购物助手。

## 四大系统概览

| 系统 | 核心逻辑 | 关注点 | 权重方向 |
|------|---------|-------|---------|
| **A9/A10 算法** | 关键词匹配 + 转化排序 | 关键词相关性、转化率、销量速度 | 传统搜索排名 |
| **COSMO 知识图谱** | 语义理解 + 购买意图映射 | 产品与用户意图的关系，不只是关键词匹配 | AI 推荐和关联推荐 |
| **Alexa Shopping** | 对话式购物助手（Rufus 升级） | 完整回答消费者问题 + 个性化推荐 + 跨设备连续性 | 对话式搜索（转化率比非AI用户高60%） |
| **AI 智能概览** | 搜索结果和产品页的 AI 摘要 | Listing 内容是否能被 AI 准确提取和呈现 | 搜索结果首屏展示 |

**核心原则**：关键词让你被考虑到（A9），意图信号让你被推荐（COSMO），价值沟通让你被选中（Alexa Shopping），结构化信息让你被正确摘要（AI 概览）。

## A9/A10 算法优化

### Product Title（产品标题）

| 规则 | 说明 |
|------|------|
| **长度** | ≤200 字符（含空格），核心信息放前 80 字符 |
| **结构** | `[品牌名] [核心成分/产品名] [规格/浓度] — [一句话功能描述], [补充信息]` |
| **关键词** | 最高搜索量关键词放标题，尽量靠前 |
| **人类可读** | 不为算法牺牲可读性，标题必须让消费者一眼看懂 |
| **避免** | 关键词堆砌、ALL CAPS、特殊符号、促销词 |

示例（膳食补充剂）：
```
[Brand] Magnesium Glycinate 400mg — Highly Bioavailable Magnesium for Muscle, Nerve, and Sleep Support, Non-GMO, Gluten-Free, 120 Vegan Capsules
```

### Bullet Points（五点描述）

| 规则 | 说明 |
|------|------|
| **数量** | 5 条（Amazon 标准） |
| **结构** | 每条：`[功能主题大写] — [一句话详细说明]` |
| **内容** | 一条一个卖点，不混合多个信息 |
| **关键词** | 长尾关键词自然嵌入，不堆砌 |
| **预反异议** | 至少一条回应消费者常见顾虑（如"gentle on stomach"） |
| **长度** | 每条 150-250 字符 |

示例（膳食补充剂 Magnesium Glycinate）：
```
HIGHLY BIOAVAILABLE MAGNESIUM — Chelated to glycine for superior absorption compared to magnesium oxide or citrate, delivering 400mg of elemental magnesium per serving.

SUPPORTS RESTFUL SLEEP — Promotes relaxation and healthy sleep patterns naturally. Many users report falling asleep faster and waking refreshed.

MUSCLE AND NERVE SUPPORT — Contributes to normal muscle function and nerve signaling. Ideal for active individuals and those with physically demanding lifestyles.

GENTLE ON DIGESTION — Unlike other magnesium forms, glycinate is well-tolerated and less likely to cause digestive discomfort or laxative effects.

CLEAN FORMULA — Non-GMO, gluten-free, vegan capsules. No artificial colors, flavors, or preservatives. Third-party tested for purity and potency.
```

### Backend Search Terms（后台搜索词）

| 规则 | 说明 |
|------|------|
| **容量** | 最多 249 bytes（不是字符！） |
| **内容** | 标题和 bullet points 未覆盖的同义词、拼写变体、西班牙语翻译 |
| **避免** | 重复标题中已有的词、品牌名（自己的）、ASIN、"for" "and" 等停用词 |
| **技巧** | 包含常见拼写错误、口语化表达、场景词 |

### Product Description

| 规则 | 说明 |
|------|------|
| **定位** | 补充 bullet points 未覆盖的信息，讲述品牌故事 |
| **不重复** | 不简单重复 bullet points 内容 |
| **长度** | 500-1000 字符 |
| **FDA 免责声明** | 必须放在 description 末尾 |

## COSMO 知识图谱优化

### COSMO 的 15 种常识关系

COSMO 不匹配关键词，而是映射产品到购买意图。它通过 15 种关系理解产品：

| 类别 | 关系类型 | 说明 | 优化方向 |
|------|---------|------|---------|
| **功能** | Used_For_Func | 产品用来做什么 | 明确说明核心功能 |
| **功能** | Used_To | 用来达成什么目标 | 描述使用目标 |
| **功能** | Capable_Of | 产品能做什么 | 列举产品能力 |
| **受众** | Used_For_Audience | 适合什么人群 | 说明适用人群 |
| **受众** | Used_By | 谁在使用 | 描述典型用户 |
| **受众** | xIs_A | 产品属于什么类别 | 明确产品分类 |
| **场景** | Used_For_Event | 什么场景/事件使用 | 描述使用场景 |
| **场景** | Used_On | 用在什么上 | 说明使用对象 |
| **场景** | Used_In_Location | 在哪里使用 | 描述使用地点 |
| **场景** | Used_In_Body | 作用于身体哪个部位 | 说明作用部位 |
| **分类** | Used_As | 作为什么使用 | 说明使用方式 |
| **分类** | Is_A | 是什么 | 清晰的产品定义 |
| **互补** | Used_With | 和什么一起用 | 描述搭配方案 |
| **互补** | xInterested_In | 用户还对什么感兴趣 | 覆盖相关兴趣 |
| **互补** | xWant | 用户想要什么 | 描述用户期望结果 |

### COSMO 优化策略

**核心转变**：从"堆关键词"转为"覆盖意图维度"。

| 策略 | 传统 A9 做法 | COSMO 优化做法 |
|------|-----------|--------------|
| **标题** | 塞满关键词 | 清晰表达产品是什么、为谁、解决什么问题 |
| **Bullets** | 每条一个关键词 | 每条覆盖不同的用户意图维度 |
| **后台词** | 重复标题词 | 补充标题未覆盖的关系维度 |
| **A+ Content** | 品牌展示 | 扩展意图覆盖（使用场景、搭配方案、适用人群等） |
| **属性字段** | 只填必填项 | 填满所有可选属性字段 |

**关键原则**：关键词在文案中只需出现一次，COSMO 会自动建立关联。重点是覆盖更多意图维度，而非重复关键词。

### 膳食补充剂的 COSMO 优化示例

以 Magnesium Glycinate 为例，覆盖意图维度：

| 意图维度 | 覆盖方式 |
|---------|---------|
| Used_For_Func | "Supports muscle relaxation and nerve function" |
| Used_To | "Promotes restful sleep and helps you wake refreshed" |
| Used_For_Audience | "Ideal for active adults, athletes, and those with busy lifestyles" |
| Used_For_Event | "Perfect for evening wind-down routines" |
| Used_In_Body | "Supports muscles, nervous system, and cardiovascular health" |
| Used_With | "Pairs well with Vitamin D3 and K2 for comprehensive mineral support" |
| xWant | "For those seeking better sleep quality and muscle recovery" |

## Alexa Shopping 优化（Rufus 升级版，2026）

### Alexa Shopping 是什么

2026 年，亚马逊将 Rufus AI 整合进 Alexa Shopping（购物版 Alexa），成为融合产品专业知识 + 用户购物历史 + Alexa+ 个性化上下文的更强 AI 购物助手。它通过亚马逊购物应用、网站和 Echo Show 设备提供服务，支持语音、触控或两者结合的交互方式。

**与旧版 Rufus 的关键区别**：

| 维度 | 旧版 Rufus | Alexa Shopping（2026） |
|------|-----------|---------------------|
| **数据源** | 仅产品 Listing + 评价 | Listing + 评价 + 用户购物历史 + Alexa 对话历史 + Alexa+ 个性化数据 |
| **交互入口** | 购物应用内的 Rufus 聊天 | 主搜索栏直接提问 + 专属聊天窗口 + Echo Show 语音/触控 |
| **个性化** | 无 | 家庭成员、宠物、爱好、饮食需求等个性化信息影响推荐 |
| **跨设备** | 仅 App | App + 网站 + Echo Show 对话连续性 |
| **功能扩展** | 问答 | 问答 + 商品对比 + 价格历史 + 定期购买 + 全网浏览 + 购物车管理 |

### Alexa Shopping 优化策略

#### 1. 主搜索栏自然语言查询优化

用户现在可以在亚马逊主搜索栏直接提出自然语言问题（如"哪种镁补充剂对睡眠最好"），搜索栏智能识别提问类型。

**优化方法**：
- Listing 中需包含消费者可能提出的自然语言问题和回答
- Bullet Points 采用问答结构（隐性回答一个具体问题）
- A+ Content 加入 FAQ 模块覆盖高频问题
- 标题前 80 字符必须直接回答"这是什么产品"

**消费者典型自然语言查询（膳食补充剂）**：
- "What's the best magnesium for sleep?"
- "Which magnesium won't upset my stomach?"
- "How much magnesium should I take daily?"
- "What's the difference between magnesium glycinate and citrate?"
- "Is this supplement vegan?"

#### 2. AI 智能概览优化

亚马逊在搜索结果顶部和产品详情页均展示 AI 生成的概览摘要。Alexa Shopping 从 Listing 全量内容中提取关键信息生成摘要。

**优化方法**：
- **首段关键信息**：Product Description 和 A+ Content 的首段必须包含产品最核心的信息（成分、规格、核心功效）
- **结构化信息**：使用清晰的标题和分隔，便于 AI 提取
- **一致性**：Title、Bullets、A+ Content 中的核心信息必须一致，避免 AI 提取到矛盾信息
- **完整句子**：AI 更容易从完整句子中提取摘要，关键词碎片不利于摘要生成
- **FAQ 模块**：A+ Content 中的 FAQ 直接成为 AI 概览的素材

#### 3. 搜索结果商品对比优化

Alexa Shopping 可从搜索结果中生成并列商品对比表，自动提取功能、价格、评价等信息。

**优化方法**：
- **规格信息标准化**：确保浓度、剂型、每瓶粒数、每份含量等关键规格在 Listing 中清晰且格式一致
- **差异化信息明确**：与竞品的核心差异（如"唯一使用 glycinate 形态而非 oxide 混合"）要在 Bullets 中明确表达
- **属性字段填全**：填满 Amazon 后台所有可选属性字段（dietary preferences、allergen info、form type 等），AI 对比表会读取这些字段
- **对比友好的文案结构**：每条 Bullet 的主题词（大写部分）应该是可对比的维度（如"ABSORPTION"、"SERVING SIZE"、"CERTIFICATIONS"）

#### 4. 个性化数据对齐

Alexa Shopping 利用用户的个性化信息（家庭成员、宠物、爱好、饮食需求、健康状况）来调整推荐。

**优化方法**：
- 在 Listing 中明确覆盖常见的个性化标签：
  - 饮食需求：vegan, gluten-free, non-GMO, dairy-free, keto-friendly
  - 生活方式：active lifestyle, athletes, busy professionals, seniors
  - 健康目标：sleep support, immune support, joint health, energy
  - 家庭场景：family-friendly, suitable for adults
- 在 A+ Content 中加入"适合谁"模块，让 Alexa 更容易匹配到对应的用户画像
- 后台属性字段中的 dietary preference 和 allergen info 必须准确填写

#### 5. 跨设备购物体验优化

Alexa Shopping 对话在 App、网站和 Echo Show 之间保持连续性——用户在 Echo 上的研究可以无缝衔接到 App 上的购买。

**优化方法**：
- Listing 信息在各设备上的呈现需一致
- 图片文案（Infographic）在移动端需清晰可读（Echo Show 和手机端屏幕都较小）
- A+ Content 的图片文字需要足够大，在 Echo Show 的触控界面上也能清楚阅读
- 考虑用户在 Echo 上做前期研究、在 App 上做最终购买的场景，Listing 需提供足够的决策信息

#### 6. 定期购买与复购优化

Alexa Shopping 支持创建定时任务（定期补充、自动复购），这直接影响补充剂的 LTV（客户终身价值）。

**优化方法**：
- 在 Bullets 或 A+ Content 中说明产品的建议使用周期（如"90-day supply"、"2 capsules daily"）
- 清晰标注每瓶可用天数，便于用户设定复购周期
- 提及"Subscribe & Save"兼容性（如适用）

#### 7. 价格历史透明化

用户现在可在产品详情页查看长达一年的价格变动历史。

**对 Listing 文案的影响**：价格策略不在文案范畴内，但了解此功能有助于文案定位——如果产品定位高品质，文案应更强调价值（value）而非价格（price）。

### Alexa Shopping 优化的 Bullet Points 示例

在原有 Rufus 问答结构基础上，进一步优化为 Alexa Shopping：

```
WHY MAGNESIUM GLYCINATE? — Magnesium glycinate is one of the most bioavailable forms of magnesium, meaning your body absorbs more of it. Unlike magnesium oxide (which has a low absorption rate), glycinate delivers magnesium efficiently to where your body needs it.

WILL THIS HELP ME SLEEP? — Magnesium glycinate promotes relaxation by supporting GABA function, a neurotransmitter that calms the nervous system. Many users find it easier to fall asleep and stay asleep when taking magnesium glycinate before bed.

IS THIS GENTLE ON MY STOMACH? — Yes. Magnesium glycinate is known for being gentle on digestion. Unlike magnesium citrate or oxide, it is less likely to cause loose stools or stomach discomfort.

90-DAY SUPPLY — Each bottle contains 180 vegan capsules (2 capsules per serving = 400mg elemental magnesium). Take with water in the evening for best sleep support. Compatible with Subscribe & Save for automatic monthly delivery.

CLEAN, THIRD-PARTY TESTED — Non-GMO, gluten-free, dairy-free, vegan. No artificial colors, flavors, or preservatives. Every batch tested for purity, potency, and heavy metals in a GMP-certified facility.
```

注意与之前的 Rufus 版本相比的变化：
- 增加了"90-DAY SUPPLY"——覆盖复购和 Alexa 定时任务场景
- 增加了"Subscribe & Save"提及——覆盖自动复购场景
- "CLEAN" bullet 增加了"dairy-free"——覆盖更多饮食个性化标签
- 保持 The Ordinary 风格：教育性、客观、短句

## A+ Content 优化

### Premium A+ 模块策略

| 模块类型 | COSMO 价值 | Alexa Shopping 价值 | AI 概览价值 | The Ordinary 风格参考 |
|---------|-----------|-------------------|-----------|---------------------|
| **对比图表** | 覆盖 Used_As, xIs_A | 帮助 Alexa 区分产品 | 被 AI 对比表提取 | "What Should I Use?" 风格 |
| **FAQ 模块** | 覆盖所有意图维度 | 直接喂给 Alexa + 主搜索栏问答 | 成为 AI 概览素材 | 教育性问答风格 |
| **品牌故事** | 覆盖 Used_By, xInterested_In | 建立品牌认知 | 品牌信息被摘要提取 | "Clinical Formulations with Integrity" |
| **使用指南** | 覆盖 Used_With, Used_For_Event | 回答 "how to use" + 复购周期 | 用法信息被摘要提取 | "Build Your Regimen" 步骤图 |
| **成分科普** | 覆盖 Used_For_Func, Capable_Of | 回答 "what is X" | 成分信息被摘要提取 | "Key ingredients:" 风格 |
| **适用人群** | 覆盖 Used_For_Audience | 对齐 Alexa 个性化标签 | 人群信息被摘要提取 | "Who is this for?" 模块 |
| **临床数据** | 覆盖 xWant | 回答 "does it work" | 数据被摘要引用 | Before/After + 数据来源 |
| **规格摘要** | — | 帮助 Alexa 商品对比 | 规格信息被结构化提取 | 清晰的成分+浓度+剂型表 |

### A+ Content 文案风格

遵循 The Ordinary 品牌指南：
- 教育优先，不推销
- 短句、清晰、有留白
- 数据标注来源
- 成分和功能用客观描述
- 对比不同产品帮消费者做选择
- 新增：加入"适合谁"和"规格摘要"模块，服务 Alexa 个性化推荐和对比功能

## Listing 优化的时效性

- A9/A10 关键词变更：3-7 天见效
- COSMO 语义更新：7-14 天生效
- Alexa Shopping 索引更新：7-14 天生效
- AI 智能概览更新：7-14 天生效
- 因此修改 Listing 后至少等 2 周再评估效果
