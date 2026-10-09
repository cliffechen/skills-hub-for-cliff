# 营销话术：成分链路式损失厌恶（默认）＋按需原理

交付 Excel 的「营销话术」sheet 按本文件写。它是**候选池**：不替换「文案总表」的主文案，每条注明建议位置，由用户或美工挑选。

- **默认生成**：A+ 与品牌故事批次默认生成 **16 条成分链路式损失厌恶话术**（下面第 1 节），全部 A+ 可用。用户可在 plan 阶段关闭或改数量。listing 副图批次不生成。
- **按需**：其他心理学原理和站外话术（第 3、4 节）只在用户要求时才写。
- **事实**：每条话术必须能对应 F 编号；成分机理事实来自成分档案或本次调研（见 `ingredient-research.md`），不新增未确认的事实。
- **成品参照**：B0XXXXXXXX v5（`工作区/05-输出/` 中 v5 的 copy.json）是用户认可的效果，写法、列和语气以它为准。

## 1. 成分链路式损失厌恶（默认）

**机制**：人对"失去"的感受比"得到"更强烈。让顾客意识到"我可能缺了这个成分"，比单说"补充它有好处"更有推动力。

### 1.1 先画链路（写进 plan，用户确认）

```
缺口（为什么可能不够）→ 作用（成分在身体里做什么）→ 年龄（为什么随年龄更重要）→ 生活结果（顾客能感受到的场景）
```

- 每一环都要有 F 编号；链路内容来自成分档案 `references/ingredients/{成分}.md`，没有档案就按 `ingredient-research.md` 去查。
- 生活结果只能落在**本产品允许的功效方向**上（plan 里确定的 allowed claims，见 `ingredient-research.md`）。
- 成分的来源（如"由肠道转化"）不等于功效方向（如"肠道健康"）。

### 1.2 一句话两个方向读

| | 写在哪 | 内容 |
|---|---|---|
| **正读** | 图上（话术本身） | 每天一份 [成分] → 我能 [生活结果] |
| **反读** | 只写在表格里，**图上不写** | 我可能缺 [成分] → [身体功能] 跟不上 → 随年龄 [变化] |

图上只写链路中的**事实环节**，让顾客自己推出反读；不写"不吃就会 XXX"。

### 1.3 16 条的分配

- **单一成分**：缺口 / 作用 / 年龄 / 生活结果 各 4 条。
- **多成分**（如钙＋D3＋K2）：主成分走完整链路，约 10–12 条；每个辅助成分写 1–2 条"它为什么在这里"（例如 [辅助成分] helps your body use [主成分].*），同样填正读/反读。总数仍约 16。
- **生活结果**的 4 条优先对应构图里已有的人物或场景（例如三张人物照各一条），建议位置写明对应的照片。

### 1.4 句型模板（按链路环节）

| 环节 | 模板 | 是否带 * |
|---|---|---|
| 缺口 | Not every [body / diet] can [get / make] enough [成分]. [份量] a day can. | 通常不带 |
| 缺口 | You can't feel whether you get enough [成分]. You can read [剂量] on the label. | 不带 |
| 作用 | Your [cells / bones / muscles] [自然过程]. [成分] supports that [过程].* | 带 |
| 作用 | Every [身体部位] has a [比喻：cleanup crew / building crew]. [成分] supports it.* | 带 |
| 年龄 | [身体功能] matters more with age. [份量] a day supports it.* | 带 |
| 年龄 | [身体部位] don't stay the same. Your support shouldn't either.* | 带 |
| 生活结果 | Every [场景动作] starts in your [身体部位]. Support it daily.* | 带 |
| 生活结果 | Your [时刻] runs on [身体功能]. One serving a day supports it.* | 带 |

具体成分的示例句见对应的成分档案。

### 1.5 JSON 字段与等级

- 每行：`principle` 固定写"损失厌恶（成分链路）"，`channel` 为 "A+"，`level` 统一 ⚠️（依据含通用科普或研究、非 listing），必填 `positive_read` 和 `negative_read`；`risk` 以"链路环节：缺口/作用/年龄/生活结果。"开头。
- 带 `*` 的话术只能放在有 FDA 声明的图上，`placement` 写明是哪张图；不带 `*` 的可以放在没有 FDA 声明的图上。
- aging 可以作为情绪主题（用户 2026-10-02 决定），但不写逆转/抗衰。

### 1.6 禁止

- 明写"不吃就会 XXX"；too late, damage, disease, dying, sick；reverse / anti-aging / turn back。
- 本产品不允许的功效方向（scan 按 JSON 里的 `meta.claims.blocked` 拦截）。
- 疾病名称，包括 FDA 授权健康声明里的疾病词，除非用户在 plan 阶段确认使用并给出原文。

## 2. A+ 红线（以卖家后台当前 A+ 内容指南为准）

| 禁止类别 | 例子 | 替代写法 |
|---|---|---|
| 价格 / 促销 | $X/day, price, free, bonus, affordable, discount, sale | 写份量和用法 |
| 购买引导 | buy now, add to cart, get yours, order now, shop now | 让画面和事实本身收尾 |
| 时效 | now, new, latest, limited, hurry, only N left, today only, 节日 | 写长期成立的事实 |
| 评价 / 社会认同 | reviews, stars, 5-star, "customers love" | 用第三方检测、cGMP 等可核实的证据 |
| 保证 / 退款 | guarantee, refund, money-back, risk-free | 不写 |
| 排名 / 最高级 | best-selling, #1, top-rated, top-selling | 用具体事实代替 |

## 3. 按需：其他 A+ 可用原理（用户要求时才写）

| 原理 | 机制 | 模板 |
|---|---|---|
| 模糊厌恶 | 人更愿意选清楚知道是什么的选项 | Know exactly what's in ___. / Don't spend [天数] guessing ___. |
| 预期后悔 | 提前想到选错会后悔 | Check ___ before you commit to ___.（不带紧迫感） |
| 属性对比 | 有参照物才看得出好坏 | Not a ___. Not a ___. Just ___.（只对比属性，不点名竞品） |
| 具体性 | 具体数字比形容词可信 | [数字]. [数字]. One ___. |
| 权威 / 证据 | 第三方背书降低怀疑 | Checked by ___, not just by us.（只用事实底座里的检测/认证） |
| 低门槛承诺 | 第一步越小越容易开始 | [用量]. That's the whole routine. |
| 身份认同 | 人会买符合"我是谁"的东西 | For people who ___.（不贬低别人） |
| 好奇缺口 | 留一个问题让人往下读 | Why ___, not ___?（答案必须在后面的图里） |

## 4. 按需：站外原理（⛔ 不可放 A+，用户要求时才写）

用于广告、社媒、站外落地页，`channel` 写"站外"、`level` 写 ⛔。每条都要满足诚实要求（FTC：广告说法必须真实、有依据）；需要真实数据的地方用 `[N]` 占位。

| 原理 | 模板 | 诚实要求 |
|---|---|---|
| 稀缺 / 紧迫 | Current batch: [lot #]. Next batch ships [date]. | 稀缺必须真实 |
| 社会认同 | Join [N]+ people who ___. | 人数、评分必须是真数据 |
| 价格锚定 | About $[X] a day for [剂量] of [成分]. | 按当前售价真实计算 |
| 风险逆转 | [退款政策原文] | 政策必须真实存在 |
| 互惠 | Free guide: [指南名] | 赠品真实可领 |

## 5. 排位与自检

- 每张图最多放 1 条话术；最强的一句放最后一张图（峰终定律）。
- 每条都有 F 编号；损失厌恶行都有反读。
- 带 `*` 的话术，建议位置那张图有 FDA 声明。
- 没有命中 A+ 红线词、恐吓措辞和本产品不允许的功效方向（scan_copy 会检查）。
