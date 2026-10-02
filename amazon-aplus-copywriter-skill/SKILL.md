---
name: amazon-aplus-copywriter
description: 亚马逊图片文案编写（A+、品牌故事、listing主副图）：当用户提供Canva/设计稿构图（图中文字为占位符），并给出ASIN或手动产品信息、可选对标品牌文案库（markdown集），要求为构图逐个文字位写英文文案时使用。先读→出plan→用户确认→再写→验证→交付Excel。
---

# 亚马逊图片文案（A+ / Brand Story / Listing 主副图）

把设计稿里的**每一个文字位**替换成以产品事实为依据的英文文案，并交出一份美工能直接复制的表格。支持三类图：A+ 模块图、品牌故事图、listing 图库的主图/副图。默认：美国站、英文文案＋中文释义、Excel交付（用户可在plan阶段改成Word/Markdown）。

## 铁律

1. **先读 → 出 plan → 停下等用户确认 → 才写。** plan 回合结束时不产出任何最终文件。用户在选择题里做完决定即视为确认；若 plan 被要求修改，改完再确认一次。
2. **构图里的所有文字都是占位符**，包括品牌名、Logo、数字、徽章、Supplement Facts。不能把占位符当事实。
3. **事实只来自两处：** 产品事实底座（ASIN抓取或用户手动提供）＋用户在对话中确认的补充。通用科普若被采用，必须标注"非listing"并限定措辞。
4. **对标库只借结构与方法，不照抄原句。**

## 输入

检查当前文件夹，识别三类输入；缺哪类就问哪类。

| 输入 | 形态 | 处理 |
|---|---|---|
| 产品事实 | A. ASIN；B. 用户手动粘贴；C. 两者混用 | 见「第1步」 |
| 对标品牌库 | 文件夹里一组 markdown（任意品牌，可随时更换）；可缺省 | 读 `references/library-digest-guide.md` 提炼"规则卡"；没有库时用 `references/baseline-rules.md` |
| 构图 | PNG/JPG（Canva导出等） | 先按第0步判断图片类型，再逐张用 Read 查看，列出每个文字位 |

## 流程

### 第0步：判断图片类型

用文件名和像素比例判断，在 plan 里写明：

| 类型 | 线索 | 规则来源 |
|---|---|---|
| A+ 模块图 | 4:3、1464×600 等横图；文件名含 A+/连图 | 基线规则＋`references/aplus-specs.md` |
| 品牌故事 | 1464×625 背景、362×453 卡片；文件名含品牌故事/轮播 | 同上 |
| Listing 副图 | 1:1 正方形（1600×1600、2000×2000）；文件名含副图/主图/listing | `references/listing-images.md`（写法与 A+ 不同：每张独立、字更少、数字前置、标签放最后） |
| 主图 | 用户提到主图但没有文件 | 不写文案；plan 里确认“主图为纯白底产品图” |

同一批文件可能混有多类，分别套规则；交付时可以合并到一个 Excel，也可以分文件（默认按类型分文件）。

### 第1步：建立产品事实底座

**ASIN 模式**
- `web_fetch https://www.amazon.com/dp/{ASIN}`。结果过大时会存成文件，用 Grep `-o` 抽取（长行会被省略，必须用 `-o`）：
  - 标题：`productTitle` 附近，或 `<p tabindex="0">` 行
  - 五点：`a-list-item[^>]*>[^<]{30,2000}`
  - 详情：品牌、制造商、首次上架日期、尺寸、粒数、口味等
  - 品牌与店铺：`Visit the .* Store` / `访问 .* 品牌旗舰店`，以及店铺链接 slug（可能是品牌 slogan 线索）
  - 现有 A+/品牌故事：`aplus-media-library-service-media` 与相邻 `alt="..."`
  - **同品牌兄弟款标题**：页面里 `alt="{品牌} ..."` 的推荐位——用来识别构图是否借用了兄弟款素材（剂量、剂型不同）
- 页面常被本地化成中文（加 `?language=en_US` 也未必有效）。中文时照常抽取并回译，在 plan 和交付物里**明确标注"由中文页面回译，上线前以英文后台核对"**；或请用户贴英文五点。
- 抓取失败：告诉用户，转手动模式。不要用 curl/python 绕过。

**手动模式**：把 `references/manual-facts-template.md` 的填空项发给用户（或直接接收用户粘贴的内容），缺失的关键项（剂量/规格/份数/剂型/认证依据）列入 plan 的待确认项。

每条事实编号 F01、F02…，记录出处（listing标题/要点N/详情/标签图/用户确认+日期/通用科普）。

**成分机理事实**（补剂类）：识别主成分和有功效作用的辅助成分，先查 `references/ingredients/{成分}.md` 有没有档案；有且未过期就沿用，没有就按 `references/ingredient-research.md` 的调研清单查（剂量口径、来源与缺口、作用、年龄、允许/拦截的功效方向、原料风险、顾客疑虑）。这类事实接着编号，来源标"通用科普（非 listing）"或"研究（非本品）"并附出处方向，只保留定性结论。

### 第2步：读对标库 → 规则卡

按 `references/library-digest-guide.md` 读库，产出 ≤12 条的规则卡（每条注明来自哪个文件）。规则卡在 plan 里展示给用户。

### 第3步：读构图 → 文字位清单

逐张查看图片，记录：图号、文件名、每个文字位（位置、行数、字重/颜色/斜体等样式、原占位文字）、画面元素（人物、产品、食物、图标、徽章、他牌素材）。识别连图（跨图延续的标题或产品）。

同时识别**品牌调性位**：用户要求写品牌调性/腔调，或文件名含品牌调性、品牌标语、slogan、tagline、品牌宣言等语义，或占位文字本身要求写调性。触发条件详见 `references/brand-voice.md`。

### 第4步：输出 plan（对话中，然后停下）

plan 包含：
1. **事实底座**：F编号清单＋来源说明（含中文回译提示）。
2. **规则卡摘要**（来自对标库或基线规则）。
3. **逐图任务卡**：每张图回答消费者的哪个问题 → 主标题方向 → 关键数字（对象/单位/份量）→ 与上一张/下一张如何衔接；品牌调性位单独标出。A+ 整体按"问题→机制→核对/证据→场景→信任"排。
4. **冲突表**：按 `references/conflict-checklist.md` 逐项检查构图 vs 事实，列出问题与默认处理。
5. **合规方式**：识别品类；补剂/保健品启用 `references/compliance-supplements.md`；其他品类按基线规则＋品类常识，必要时提醒用户核对类目政策。
6. **成分链路与功效方向**（补剂类）：每个主成分一条链路 `缺口 → 作用 → 年龄 → 生活结果`（带 F 编号）；本产品 allowed / blocked 功效方向；多成分时各成分的分工。（见 `references/ingredient-research.md`）
7. **营销话术与成分科普**：A+/品牌故事批次默认附两张 sheet——「营销话术」16 条成分链路式损失厌恶（`references/persuasion-psychology.md`）、「成分科普」约 6–7 个 ELI5 主题（`references/ingredient-eli5.md`）；用户可关闭或改数量，其他心理学原理和站外话术只在用户要求时写。listing 副图批次不生成。
8. **交付格式**（默认Excel）。
9. **AskUserQuestion 选择题**（≤4题，推荐项放第一个）：常见题目——品牌名写法、某张图的叙事角度、listing未覆盖的徽章/认证是否有证据、交付格式。

然后**停止**，等用户确认。

### 第5步：写文案

逐文字位写：新英文文案、备选一句、中文释义、事实编号、合规/设计备注。要点：
- 字数贴近占位原文（同样行数、相近字符数）；超出时给更短的备选或注明可折行。
- 标注约定：`**…**` 加粗，`*…*` 红色/强调斜体，句尾单独 `*` 为功能声明星号；单元格内换行即排版换行。
- 需要新增的文字位（FDA 声明、可选小标签、可选徽章）标【新增】或【可选新增】。
- 同时给每张 A+ 图写 alt 文本（≤100 字符），品牌故事按需；listing 副图没有 alt 字段，不写。
- listing 副图另按 `references/listing-images.md`：每张独立成立、大标题 ≤2 行 ≤45 字符、FDA 声明按图放、对照列按属性限定。
- 品牌调性位按 `references/brand-voice.md` 写：洞察式品牌宣言，两拍、不写数字/规格/认证、不复述前面图的事实；该图的 alt 也只写品牌＋产品＋情绪主张。JSON 里给这些行（含该图 ALT 行）加 `"voice": "brand"`。
- 营销话术写进 JSON 的 `marketing` 数组，成分科普写进 `explainers` 数组，写法按上面两份参考文件；plan 确定的功效方向写进 `meta.claims`（`allowed` / `blocked`）。成品效果以用户认可的 B0XXXXXXXX v5 为准（见 `references/ingredients/urolithin-a.md`）。
- 设计层面的问题（换Logo、换瓶身、他牌素材、标签重做、播放按钮等）写进「设计修改清单」，不混在文案里。

### 第6步：生成交付物

先取本批交付的生成时间戳（12 小时制，如 `20261001_PM1030`），所有产物共用它：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_xlsx.py --stamp-only
```

把全部内容写成 JSON（结构见 `scripts/build_xlsx.py` 顶部注释），命名为 `{ASIN}_{类型}_v{n}_{时间戳}_copy.json`，然后：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_xlsx.py copy.json "/path/{ASIN}_{类型}_v{n}_{时间戳}.xlsx"
```

文件名没带时间戳时脚本会自动补上，以脚本打印的 `saved …` 路径为准。

输出 sheet：说明 / 文案总表（含 LEN 字符数、差值公式）/ 营销话术（有 `marketing` 时）/ 成分科普（有 `explainers` 时）/ 设计修改清单 / 事实依据。文件名格式 `{ASIN}_{类型}_v{n}_{YYYYMMDD}_{AM|PM}{hhmm}.xlsx`，如 `B0XXXXXXXX_A+高级轮播文案_v1_20261001_PM1030.xlsx` / `{ASIN}_副图文案_v1_{时间戳}.xlsx`，放到用户文件夹。用户要 Word/Markdown 时，用同一份 JSON 转换（Word 需先读 docx skill），文件名带同一个时间戳。

### 第7步：验证（必须）

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_copy.py copy.json --forbid "1000mg,softgel,旧品牌名" [--supplement] [--listing]
```
- `--forbid` 填本次冲突表里"不应再出现"的词（错误剂量、错误剂型、占位品牌名、对标品牌名等）。
- 检查：禁用词、alt 超长、带星号功效句是否有 FDA 声明行、比占位原文长太多的字段；`voice: brand` 行若含数字/规格/认证词或与其他行有 4 词以上重复则 FLAG；所有行检查 A+ 政策词（价格/促销、buy now、now/new/limited、reviews/stars、guarantee/refund、best-selling/#1），命中即 FLAG；`marketing` 行另查恐吓措辞（FLAG）、A+ 行未填 `[N]`（FLAG）、站外行未填 `[N]`（WARN）、损失厌恶行缺反读（WARN）；`explainers` 行做同样的禁用词/恐吓/A+ 政策词检查；任何行出现 `meta.claims.blocked` 里的功效方向即 FLAG（没设 `meta.claims` 时 WARN）；`--listing` 另查残留中文占位（FLAG）和过长标题（WARN）。
- Excel 公式重算：先复制到 `/tmp` 再跑 xlsx skill 的 `recalc.py`（挂载目录下 LibreOffice 容易超时），确认 `total_errors: 0` 后复制回去。不要在同一条 bash 命令里 `pkill -f soffice`（会杀掉自身）。

### 第8步：交付

给出文件链接＋简短总结：叙事主线一句话、最关键的必改项（通常是标签/剂量/他牌素材）、仍待用户确认的事项。不长篇复述表格内容。

本次如果调研了新成分（或复核了旧档案），按 `references/ingredients/_template.md` 存档或更新，只存用户在 plan 里确认过的结论，并告诉用户存了哪份档案。

## 参考文件

- `references/baseline-rules.md`：无对标库时的写作基线
- `references/library-digest-guide.md`：如何从任意品牌 md 集提炼规则卡
- `references/conflict-checklist.md`：构图 vs 事实的冲突检查项
- `references/compliance-supplements.md`：补剂合规包（美国站）
- `references/aplus-specs.md`：A+ / 品牌故事模块规格与 alt 文本
- `references/manual-facts-template.md`：手动事实填空模板
- `references/listing-images.md`：listing 主图/副图规格与写法差异
- `references/brand-voice.md`：品牌调性位的洞察式品牌宣言写法、触发条件与禁区
- `references/persuasion-psychology.md`：营销话术 sheet——默认成分链路式损失厌恶；按需原理、A+ 红线与站外诚实要求
- `references/ingredient-eli5.md`：成分科普 sheet 的 ELI5 写法、主题顺序与合规
- `references/ingredient-research.md`：遇到任何新成分的调研方法论（不含具体成分结论）
- `references/ingredients/`：成分档案（每个成分一份，按需读取；`_template.md` 为存档模板）
