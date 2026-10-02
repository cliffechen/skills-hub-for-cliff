# 成分科普：用 ELI5 的方法讲清成分对人体的作用

交付 Excel 的「成分科普」sheet 按本文件写。方法改编自 [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)（MIT 协议）：先认清受众，再吃透内容，最后按"本质 → 类比 → 展开 → So what"组织解释。

- **默认生成**：A+ 与品牌故事批次默认生成，约 6–7 个主题（多成分约 6–9 个）；用户可在 plan 阶段关闭或改数量。listing 副图批次不生成。
- **用途**：每条既是 A+ 教育图的文案候选（图上短版），也是 FAQ、详情、客服回答的底稿（展开版）。
- **内容来源**：成分档案 `references/ingredients/{成分}.md`；没有档案时按 `ingredient-research.md` 调研。具体成分的完整示例见对应档案。
- **成品参照**：B0H1CZ8NLF v5 的「成分科普」sheet 是用户认可的效果。

## 受众

普通美国成年顾客：对补剂有兴趣，但不是专业人士。

- 不用术语；必须用的术语当场翻译，例如 "mitophagy = the cell's cleanup-and-renewal process"、"elemental calcium = the amount of calcium your body actually counts"。
- 一句话只讲一个意思。
- 类比取材于日常：家务、厨房、汽车保养、建筑、运动、通勤。
- 不居高临下（ELI5 原则："Never talk down to anyone"）：讲清楚，而不是讲幼稚。

## 每个主题的四步结构

| 字段 | 写什么 | 句型 |
|---|---|---|
| 一句话本质（essence） | 一句话说清是什么/做什么 | [成分] is [是什么] that [做什么].* |
| 类比（analogy） | 一个日常画面 | Think of it like [日常画面]. |
| 展开（detail） | 2–3 句，补上"怎么回事" | [身体部位] [正常过程]. Over time, [变化]. Research has observed that [成分] supports [过程].* |
| So what | 和顾客有什么关系 | That's part of how your body keeps up with [生活场景].* |
| 图上短版（on_image） | 标题 ≤ 约 45 字符＋正文 ≤ 约 120 字符，用 `\n` 分开 | [比喻式标题]\n[成分] supports [过程].* |

## 主题顺序（按顾客的提问链）

1. **它是什么？**（What is it?）
2. **它从哪来？**（Where does it come from?）——食物或原料来源（如石榴、海藻），以及身体里是否需要转化
3. **为什么光靠饮食不一定够？**（Why isn't food always enough?）——对应营销话术链路的"缺口"
4. **它在身体里做什么？**（What does it do?）——对应链路的"作用"
5. **为什么和年龄有关？**（Why does it matter with age?）——对应链路的"年龄"
6. **每天怎么吃？**（How do I take it?）——用 listing/标签事实：份量、粒数、用法；剂量写清有效量（如元素钙、元素镁）
7. **配方里还有什么？**（What else is in it?）——载体与辅料

- 主题 3–5 和营销话术的成分链路一一对应，两张 sheet 讲的是同一条链。
- **多成分产品**：主成分走 1–5；每个有功效作用的辅助成分加一个主题 "What does [辅助成分] add?"（它为什么在这个配方里）；载体和辅料并入第 7 题。
- 成分简单时可合并主题，但顺序不变。

## 事实与出处

- 第 1–5 题通常超出 listing，属于**成分机理事实**：在事实底座里单独编号，来源写"通用科普（非 listing）"或"研究（非本品）"，并在 `source` 列写出处方向（作者、年份、期刊、研究对象）。
- 需要查证时用 WebSearch，只保留**定性结论**，不搬运百分比。
- 第 6–7 题只用 listing 或标签事实。

## 合规

- 机理写成 "research has observed / studies suggest"，主语是成分，不是本品；不写"本品让你……"。
- 功能句带 `*`，放置的图要有 FDA 声明。
- 不写疾病、治疗、逆转/抗衰；aging 只作情绪背景，例如 "matters more with age"。
- 只写本产品允许的功效方向（plan 里确定的 `meta.claims.allowed`）；成分的来源（如"由肠道转化""来自海藻"）不等于功效方向。
- 配方载体（MCT oil、lecithin、piperine 等）只写"含有"，不写"促进吸收"，除非有依据。
- 图上不出现研究细节（作者、剂量、人群）；这些只放在 `source` 列，供用户核对。

## JSON 结构（`explainers` 数组）

```json
{"id": "EX-01", "question": "What is [成分]?\n它是什么？", "essence": "…", "analogy": "…", "detail": "…",
 "so_what": "…", "on_image": "标题\n正文", "zh": "中文释义", "placement": "M-3 / 【新增】教育图",
 "facts": "F11", "source": "通用科普（非 listing）：出处方向…", "level": "✅|⚠️", "risk": "…"}
```

## 自检

1. 只读"一句话本质"，外行能复述出来吗？
2. 类比有没有说错机理（比喻不能夸大效果）？
3. 每条都有事实编号；非 listing 的事实标明了来源类型和出处方向。
4. 带 `*` 的句子，放置的图有 FDA 声明。
