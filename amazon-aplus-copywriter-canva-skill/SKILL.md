---
name: amazon-aplus-copywriter-canva
description: 亚马逊图片文案编写 Canva 版（A+、品牌故事、listing主副图）：当用户给出 Canva 设计（链接/标题/"最近的设计"）或设计稿构图（图中文字为占位符），并给出ASIN或手动产品信息、可选对标品牌文案库，要求逐个文字位写英文文案、审图、或把文案和修改意见写进 Canva 每页备注时使用。链路：连 Canva → 看图（文字位+缩略图+原备注）→ 出plan → 用户确认 → 写 → 验证 → 交付Excel → 登录Canva网页按页写备注（四区格式）→ 回读核验。适配 Claude Code、Cursor、ZCode 及任何具备 computer use / 浏览器自动化能力的 agent。
---

# 亚马逊图片文案 Canva 版（A+ / Brand Story / Listing 主副图）

把设计稿里的**每一个文字位**替换成以产品事实为依据的英文文案，交出一份美工能直接复制的表格，并把同样的内容**按页写进 Canva 设计的备注**，让美工打开哪一页就看到哪一页该上图的字和该改的地方。支持三类图：A+ 模块图、品牌故事图、listing 图库的主图/副图。默认：美国站、英文文案＋中文释义、Excel交付＋Canva备注（用户可在plan阶段改成Word/Markdown，或关掉备注写入）。

本技能 = 原 `amazon-aplus-copywriter` 的写作文风、写作流程、剂型规则、输入输出**原样保留**，再加一条「连 Canva → 看图 → 写备注」链路（第 C0、C3、C9 步）。不同 agent 的工具名不同，先读 `adapters/` 里对应的一份。

## 铁律

1. **先读 → 出 plan → 停下等用户确认 → 才写。** plan 回合结束时不产出任何最终文件，也不写 Canva 备注。用户在选择题里做完决定即视为确认；若 plan 被要求修改，改完再确认一次。
2. **构图里的所有文字都是占位符**，包括品牌名、Logo、数字、徽章、Supplement Facts。不能把占位符当事实。**Canva 原备注同样不是事实**，只是上一轮的意图或待办，按"待核"处理。
3. **事实只来自两处：** 产品事实底座（ASIN抓取或用户手动提供）＋用户在对话中确认的补充。通用科普若被采用，必须标注"非listing"并限定措辞。
4. **对标库只借结构与方法，不照抄原句。**
5. **备注四区，只有①区上图。** 每页备注固定分为 ①上图文案 / ②设计指令（不上图）/ ③待确认 / ④审核记录（`references/canva-notes-format.md`）。指令、提醒、页面角色标签一律不得写进①区——"KEEP Muscle & Immune" 被当成标题上图，就是混写的后果。
6. **账号只由用户掌控。** 登录方式由用户选；邮箱/验证码向用户索取，不猜、不存；不输入密码、不点 OAuth 授权、不绕过人机验证（需要时让用户在云电脑桌面自己操作）。完成后问用户是否退出登录。
7. **写备注不碰画布。** 写入步骤只改备注；画布有任何意外改动立即撤销并告诉用户。改图上文字是另一项任务，须用户单独同意。
8. **写前回读、写后回读。** 写入前重读备注，与看图时的版本比对，有人改过就停下问用户；写入后用 Canva 读接口逐页核验，核验通过才算完成。

## 输入

检查当前文件夹和对话，识别四类输入；缺哪类就问哪类。

| 输入 | 形态 | 处理 |
|---|---|---|
| 产品事实 | A. ASIN；B. 用户手动粘贴；C. 两者混用 | 见「第1步」 |
| 对标品牌库 | 文件夹里一组 markdown（任意品牌，可随时更换）；可缺省 | 读 `references/library-digest-guide.md` 提炼"规则卡"；没有库时用 `references/baseline-rules.md` |
| 构图 · Canva | 设计链接（`canva.com/d/…`、`canva.com/design/D…/edit`）、设计标题、或"我最近的设计" | 见「第C0步」「第C3步」 |
| 构图 · 本地 | PNG/JPG（Canva导出等） | 先按第0步判断图片类型，再逐张查看，列出每个文字位 |

两种构图来源可以同时存在（例如 Canva 设计＋本地标签图）；用户只给本地图时，跳过 C 系列步骤，流程与原技能一致。

## 流程

### 第C0步：连接 Canva（有 Canva 构图时）

能力分三层，按 `references/canva-access.md` 检查本 agent 有哪几层：

| 层 | 用途 | 通道 |
|---|---|---|
| 读 | 找设计、读每页文字、缩略图、原备注、导出 | Canva MCP（`https://mcp.canva.com/mcp`） |
| 看 | 看图（版式、人物、徽章、小字） | agent 自带的图片查看；没有则用视觉 MCP |
| 写备注 | 把备注写进每一页 | Canva MCP 的 `edit-design` 有 `replace_speaker_notes` 操作时直接用它（Claude Code 实测可用，见 `adapters/claude-code.md`）；没有则走浏览器自动化 / computer use |

1. 用一次轻量调用验证 MCP 已授权（如 `search-designs` 取 1 条）。未连接 → 按 `adapters/` 指引让用户授权，不要改用网页抓取绕过。
2. 定位设计：用户给链接就用链接；给标题用 `search-designs`；说"最近的"用 `sort_by=modified_descending`。把设计名、页数、修改时间告诉用户确认是这一个。
3. 写备注那一层不可用时，在 plan 里说明，默认改为「交付备注文本，用户自己粘贴」。

### 第0步：判断图片类型

用文件名和像素比例判断（Canva 用 `get-design-pages` 返回的 `dimensions`），在 plan 里写明：

| 类型 | 线索 | 规则来源 |
|---|---|---|
| A+ 模块图 | 4:3、1464×600 等横图；文件名含 A+/连图 | 基线规则＋`references/aplus-specs.md` |
| 品牌故事 | 1464×625 背景、362×453 卡片；文件名含品牌故事/轮播 | 同上 |
| Listing 副图 | 1:1 正方形（1600×1600、2000×2000）；文件名含副图/主图/listing | `references/listing-images.md`（写法与 A+ 不同：每张独立、字更少、数字前置、标签放最后） |
| 主图 | 用户提到主图但没有文件；或 Canva 第 1 页为纯白底产品图 | 不写文案；plan 里确认"主图为纯白底产品图" |

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

每条事实编号 F01、F02…，记录出处（listing标题/要点N/详情/标签图/用户确认+日期/通用科普）。Canva 里的 Supplement Facts 页、瓶身渲染也是占位符，不能记为"标签图"；只有用户确认"这页就是实物标签"时才可以。

**剂型与辅料事实**：有标签图（或用户贴了 Other Ingredients）时，单独记一条：剂型、Serving size、外壳/基质、全部 Other Ingredients 原文、Vegetarian/Vegan 等标签字样。剂型按 `references/dosage-form-excipients.md` 识别；用户在对话里明确说的剂型优先。标签与 listing 的辅料或剂型不一致时进冲突表，以标签为准。设计稿是从另一剂型改过来的（软胶囊 → 软糖等）时，逐页查残留的剂型字样和视觉（见冲突清单第 3、15 项）。

**成分机理事实**（补剂类）：识别主成分和有功效作用的辅助成分，先查 `references/ingredients/{成分}.md` 有没有档案；有且未过期就沿用，没有就按 `references/ingredient-research.md` 的调研清单查（剂量口径、来源与缺口、作用、年龄、允许/拦截的功效方向、原料风险、顾客疑虑）。这类事实接着编号，来源标"通用科普（非 listing）"或"研究（非本品）"并附出处方向，只保留定性结论。

### 第2步：读对标库 → 规则卡

按 `references/library-digest-guide.md` 读库，产出 ≤12 条的规则卡（每条注明来自哪个文件）。规则卡在 plan 里展示给用户。

品牌有档案（`references/brand-profiles/{品牌}.md`，如 ZAB → `zab.md`）时先读：语气、签名句式和已确认的品牌承诺以档案为准；合规仍以 `compliance-supplements.md` 为准，事实仍以事实底座为准。规则卡和档案冲突时，在 plan 里说明取舍。

### 第3步：读构图 → 文字位清单

**本地图**：逐张查看图片，记录：图号、文件名、每个文字位（位置、行数、字重/颜色/斜体等样式、原占位文字）、画面元素（人物、产品、食物、图标、徽章、他牌素材）。识别连图（跨图延续的标题或产品）。

**Canva 设计（第C3步）**：按 `references/canva-access.md` 的读取配方，对本次范围内每一页取三样东西并存进 `工作区/05-输出/canva/`：
1. **图上文字**：`get-design-content` **逐页单独调用**（多页一次调用会把文字连成一片，分不清页），存 `onimage/p{N}.txt`。
2. **画面**：`get-design-pages` 拿缩略图（447px，签名链接约 2 小时过期），用 `scripts/fetch_thumbs.py` 下载后逐张查看；小字、徽章、标签看不清时，用 `export-design` 导出该页 PNG 再看，并在 plan 里注明哪些判断来自缩略图。
3. **原备注**：`get-presenter-notes` 一次取全部页，原样存 `notes_before.json`。原备注里的指令、文案草稿按铁律 2 处理：可以作为线索，不能当事实；它和图上文字不一致的地方进冲突表（"备注已改、图未同步"）。

同时识别**品牌调性位**：用户要求写品牌调性/腔调，或文件名含品牌调性、品牌标语、slogan、tagline、品牌宣言等语义，或占位文字本身要求写调性。触发条件详见 `references/brand-voice.md`。

### 第4步：输出 plan（对话中，然后停下）

plan 包含：
1. **事实底座**：F编号清单＋来源说明（含中文回译提示）。
2. **规则卡摘要**（来自对标库或基线规则）。
3. **买家与主线**（按 `references/conversion-copy.md`）：2–4 类买家各自"已经相信 / 还在怀疑"什么；整组的品类张力（一句话主线）；有价格优势时怎么在不写钱的前提下讲出来。
4. **逐图任务卡**：每张图回答哪类买家的哪个怀疑 → 主标题方向 → 关键数字（对象/单位/份量）→ 与上一张/下一张如何衔接；品牌调性位单独标出。副图、A+、轮播按 `conversion-copy.md` §7 分工，A+ 不重复副图的句子；带 \* 的功效集中在 2–3 张。
5. **冲突表**：按 `references/conflict-checklist.md` 逐项检查构图 vs 事实，列出问题与默认处理。Canva 设计另查：图上文字 vs 原备注、内部指令上图、跨页自相矛盾。
6. **合规方式**：识别品类；补剂/保健品启用 `references/compliance-supplements.md`；其他品类按基线规则＋品类常识，必要时提醒用户核对类目政策。
7. **成分链路与功效方向**（补剂类）：每个主成分一条链路 `缺口 → 作用 → 年龄 → 生活结果`（带 F 编号）；本产品 allowed / blocked 功效方向；多成分时各成分的分工。（见 `references/ingredient-research.md`）
8. **营销话术与成分科普**：A+/品牌故事批次默认附两张 sheet——「营销话术」16 条成分链路式损失厌恶（`references/persuasion-psychology.md`）、「成分科普」约 6–7 个 ELI5 主题（`references/ingredient-eli5.md`）；用户可关闭或改数量，其他心理学原理和站外话术只在用户要求时写。listing 副图批次不生成。另外，有标签图或用户提到剂型时，A+ 与副图批次都默认附「辅料与剂型」sheet：按剂型从外壳/基质、辅料清单、各司其职三个角度各写一版 headline + subheadline + 支撑卖点（`references/dosage-form-excipients.md`）；plan 里写明识别出的剂型和依据，用户可关闭。
9. **交付格式**（默认Excel）。
10. **Canva 备注写入方案**（有 Canva 构图时）：写入页码范围；写入方式（默认「覆盖，原备注先备份到本地」，可选「原备注附在④区之后」「只交付文本不写入」）；写入通道（本 agent 用哪种浏览器能力）；登录方式（由用户选，按铁律 6）。
11. **AskUserQuestion 选择题**（≤4题，推荐项放第一个；没有选择题工具的 agent 用编号选项列在对话里）：常见题目——品牌名写法、某张图的叙事角度、listing未覆盖的徽章/认证是否有证据、交付格式、备注写入方式。

然后**停止**，等用户确认。

### 第5步：写文案

逐文字位写：新英文文案、备选一句、中文释义、事实编号、合规/设计备注。要点：
- 先过 `references/conversion-copy.md` 的四个测试（换成分 / 主语 / 张力 / 场景）：合规只限制功效，不限制情绪；删掉功效词的地方要用处境、生活时刻、反差或数字换算补回说服力。不写钱字（pay、afford、price…），不贬低竞品，也不拿自家其他剂型做反例。
- 字数贴近占位原文（同样行数、相近字符数）；超出时给更短的备选或注明可折行。
- 标注约定：`**…**` 加粗，`*…*` 红色/强调斜体，句尾单独 `*` 为功能声明星号；单元格内换行即排版换行。
- 需要新增的文字位（FDA 声明、可选小标签、可选徽章）标【新增】或【可选新增】。
- 同时给每张 A+ 图写 alt 文本（≤100 字符），品牌故事按需；listing 副图没有 alt 字段，不写。
- listing 副图另按 `references/listing-images.md`：每张独立成立、大标题 ≤2 行 ≤45 字符、FDA 声明按图放、对照列按属性限定。
- 品牌调性位按 `references/brand-voice.md` 写：洞察式品牌宣言，两拍、不写数字/规格/认证、不复述前面图的事实；该图的 alt 也只写品牌＋产品＋情绪主张。JSON 里给这些行（含该图 ALT 行）加 `"voice": "brand"`。
- 营销话术写进 JSON 的 `marketing` 数组，成分科普写进 `explainers` 数组，写法按上面两份参考文件；plan 确定的功效方向写进 `meta.claims`（`allowed` / `blocked`）。辅料与剂型写进 `excipients`（`form` / `source` / `items`），只写标签上真实出现的辅料，不写 no fillers、吸收提升；vegan、free-from 类需标签或供应商依据。成品效果以用户认可的 B0XXXXXXXX v5 为准（见 `references/ingredients/urolithin-a.md`）。
- 设计层面的问题（换Logo、换瓶身、他牌素材、标签重做、播放按钮等）写进「设计修改清单」，不混在文案里。
- **Canva 页码**：每行加 `"page": N`；每条设计修改清单加 `"page": N`；每页的页面标签、③待确认、④审核记录写进 JSON 的 `canva` 块（结构见 `references/canva-notes-format.md`）。`copy` 字段只放上图的字，任何"删除/保留/替换/KEEP/Optional"类指令都放 `issues` 或 `canva.pages[].designer`。

### 第6步：生成交付物

先取本批交付的生成时间戳（12 小时制，如 `20261001_PM1030`），所有产物共用它：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_xlsx.py --stamp-only
```

（`${CLAUDE_SKILL_DIR}` 在 Claude Code、ZCode 会自动替换；其他 agent 换成本 SKILL.md 所在目录的绝对路径。）

把全部内容写成 JSON（结构见 `scripts/build_xlsx.py` 顶部注释，Canva 扩展见 `references/canva-notes-format.md`），命名为 `{ASIN}_{类型}_v{n}_{时间戳}_copy.json`，然后：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_xlsx.py copy.json "/path/{ASIN}_{类型}_v{n}_{时间戳}.xlsx"
python3 ${CLAUDE_SKILL_DIR}/scripts/build_notes.py copy.json --out "工作区/05-输出/canva/notes_{时间戳}"
```

文件名没带时间戳时脚本会自动补上，以脚本打印的 `saved …` 路径为准。

输出 sheet：说明 / 文案总表（含 LEN 字符数、差值公式）/ 营销话术（有 `marketing` 时）/ 成分科普（有 `explainers` 时）/ 辅料与剂型（有 `excipients` 时）/ 设计修改清单 / 事实依据。文件名格式 `{ASIN}_{类型}_v{n}_{YYYYMMDD}_{AM|PM}{hhmm}.xlsx`，如 `B0XXXXXXXX_A+高级轮播文案_v1_20261001_PM1030.xlsx` / `{ASIN}_副图文案_v1_{时间戳}.xlsx`，放到用户文件夹。用户要 Word/Markdown 时，用同一份 JSON 转换（Word 需先读 docx skill），文件名带同一个时间戳。

`build_notes.py` 产出每页一份 `p{N}.txt`（即将写进 Canva 的备注全文）、`all_notes.md`（汇总预览）和 `manifest.json`（页码、page_id、字符数）。

### 第7步：验证（必须）

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_copy.py copy.json --forbid "1000mg,softgel,旧品牌名" [--supplement] [--listing]
```
- `--forbid` 填本次冲突表里"不应再出现"的词（错误剂量、错误剂型、占位品牌名、对标品牌名等）。
- 检查：禁用词、alt 超长、带星号功效句是否有 FDA 声明行、比占位原文长太多的字段；`voice: brand` 行若含数字/规格/认证词或与其他行有 4 词以上重复则 FLAG；所有行检查 A+ 政策词（价格/促销、buy now、now/new/limited、reviews/stars、guarantee/refund、best-selling/#1），命中即 FLAG；`marketing` 行另查恐吓措辞（FLAG）、A+ 行未填 `[N]`（FLAG）、站外行未填 `[N]`（WARN）、损失厌恶行缺反读（WARN）；`explainers` 行做同样的禁用词/恐吓/A+ 政策词检查；任何行出现 `meta.claims.blocked` 里的功效方向即 FLAG（没设 `meta.claims` 时 WARN）；`--listing` 另查残留中文占位（FLAG）和过长标题（WARN）。
- Excel 公式重算：先复制到 `/tmp` 再跑 xlsx skill 的 `recalc.py`（挂载目录下 LibreOffice 容易超时），确认 `total_errors: 0` 后复制回去。不要在同一条 bash 命令里 `pkill -f soffice`（会杀掉自身）。
- **备注检查**：`build_notes.py` 运行时自带检查——①区出现中文或指令词（KEEP / Remove / Replace / Optional: / DO NOT / [Page …]）即 FLAG；单页超过 5000 字符 FLAG；①区有带 `*` 的句子却没有 FDA 页脚行 WARN。有 FLAG 不得进入第 C9 步。

### 第8步：交付

给出文件链接＋简短总结：叙事主线一句话、最关键的必改项（通常是标签/剂量/他牌素材）、仍待用户确认的事项。不长篇复述表格内容。有 Canva 构图时，同时贴一页备注样例（通常选问题最多的那页），问用户是否按 plan 写入 Canva；用户说写，才进第 C9 步。

本次如果调研了新成分（或复核了旧档案），按 `references/ingredients/_template.md` 存档或更新，只存用户在 plan 里确认过的结论，并告诉用户存了哪份档案。

### 第C9步：写入 Canva 备注 → 回读核验

Canva MCP 能直接写备注时（`edit-design` 的 `replace_speaker_notes`），第 3–4 步换成 `adapters/claude-code.md`「通道 A」的事务写入，第 1、2、5、6 步不变。否则按 `references/computer-use-canva.md` 执行，要点：

1. **写前回读**：`get-presenter-notes` 再取一次，与 `notes_before.json` 比对。有页面被别人改过 → 停下，把差异告诉用户，问"以新的为准重写 / 合并 / 跳过该页"。
2. **备份**：把当前备注存为 `notes_backup_{时间戳}.json`（写入方式为覆盖时必须做）。
3. **打开设计**：浏览器打开设计的编辑链接；遇到登录页按铁律 6 处理。
4. **逐页写入**：确认备注面板标题是第 N 页 → 焦点在备注输入框 → 全选 → 粘贴 `p{N}.txt` 全文（中文不要逐字键入，用剪贴板或 DOM 填值）→ 点面板标题让输入框失焦 → 看字数计数与 `manifest.json` 一致。
5. **等自动保存**，然后**写后回读**：`get-presenter-notes` 取回 → 存 `notes_after.json` →
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/verify_notes.py --expected "工作区/05-输出/canva/notes_{时间戳}" --readback notes_after.json [--on-image-dir 工作区/05-输出/canva/onimage]
   ```
   全部 MATCH 才算完成；DIFF 的页重写一次，仍失败就告诉用户哪页、差在哪。`--on-image-dir` 同时给出①区每条文案"已上图 / 未上图"的同步表，以及疑似内部指令上图的 FLAG。
6. **收尾**：抽查一页画布文字确认没被改动；问用户是否退出 Canva 登录；汇报写了哪几页、备份在哪、仍有哪些①区文案未上图。

## 参考文件

- `references/baseline-rules.md`：无对标库时的写作基线
- `references/library-digest-guide.md`：如何从任意品牌 md 集提炼规则卡
- `references/conflict-checklist.md`：构图 vs 事实的冲突检查项（含 Canva 设计特有的 15–18 项）
- `references/compliance-supplements.md`：补剂合规包（美国站）
- `references/aplus-specs.md`：A+ / 品牌故事模块规格与 alt 文本
- `references/manual-facts-template.md`：手动事实填空模板
- `references/listing-images.md`：listing 主图/副图规格与写法差异
- `references/conversion-copy.md`：让文案有购买冲动——买家阶段地图、品类张力、价格优势的写法、对比的边界、副图/A+/轮播分工
- `references/brand-voice.md`：品牌调性位的洞察式品牌宣言写法、触发条件与禁区
- `references/brand-profiles/`：品牌语气档案（每个品牌一份，如 `zab.md`）；写该品牌任何模块前先读
- `references/persuasion-psychology.md`：营销话术 sheet——默认成分链路式损失厌恶；按需原理、A+ 红线与站外诚实要求
- `references/ingredient-eli5.md`：成分科普 sheet 的 ELI5 写法、主题顺序与合规
- `references/dosage-form-excipients.md`：辅料与剂型 sheet——剂型识别、各剂型辅料角色、三个角度与证据红线
- `references/ingredient-research.md`：遇到任何新成分的调研方法论（不含具体成分结论）
- `references/ingredients/`：成分档案（每个成分一份，按需读取；`_template.md` 为存档模板）
- `references/canva-access.md`：Canva 三层能力（读/看/写备注）的检查方法与读取配方
- `references/canva-notes-format.md`：备注四区格式、JSON 里的 `canva` 块、示例
- `references/computer-use-canva.md`：浏览器 / computer use 登录 Canva 并逐页写备注的操作手册与故障处理
- `adapters/`：Claude Code、Cursor、ZCode 及通用 agent 的工具对照与安装方式
