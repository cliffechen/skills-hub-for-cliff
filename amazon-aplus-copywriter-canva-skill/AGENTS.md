# 文案工作区约定

用户要为 A+ / 主图副图写文案、审 Canva 设计、或把文案写进 Canva 备注时，使用 `amazon-aplus-copywriter-canva` 技能。本地输入一律从 `工作区/` 读取，不要求用户把图片贴进对话；Canva 设计直接用链接或标题读取。

| 文件夹 | 内容 | 处理 |
|---|---|---|
| `工作区/01-A+排版/` | A+ 模块图、品牌故事构图（PNG/JPG） | 按技能第0步判断类型，逐张查看 |
| `工作区/02-主图副图/` | listing 主图/副图构图（PNG/JPG） | 按 `references/listing-images.md` 写 |
| `工作区/03-SupplementFacts-可选/` | 真实产品的 Supplement Facts 标签图 | 有则作为事实来源（出处记为"标签图"），优先级高于构图里的占位数字；同时驱动「辅料与剂型」模块（`references/dosage-form-excipients.md`）。没有标签图但用户在对话里提到剂型时，按所说剂型写，并在 plan 里列出待确认的辅料；都没有就跳过 |
| `工作区/04-对标文案库-可选/` | 对标品牌的 markdown 文案集（可按品牌分子文件夹） | 有则按 `references/library-digest-guide.md` 提炼规则卡，只借结构与方法、不照抄原句；没有则用 `references/baseline-rules.md` |
| `工作区/05-输出/` | 交付的 Excel、copy.json 等 | 所有产出放这里 |
| `工作区/05-输出/canva/` | Canva 读写的中间文件：`pages.json`、`thumbs/`、`onimage/p{N}.txt`、`notes_before.json`、`notes_{时间戳}/`、`notes_backup_{时间戳}.json`、`notes_after.json` | 由技能第 C3、6、C9 步生成，不要手工改 |

- 开始前先列出各文件夹里的文件，把识别到的内容告诉用户；某个文件夹为空就跳过对应类型，不要报错。
- 01 和 02 都空、用户也没给 Canva 设计时，提醒用户先放图或给设计链接。
- 04 里有多个品牌时，在 plan 里列出品牌名，问用户本次对标哪个（或全部）。
- ASIN 或手动产品信息仍在对话里问用户要。
- 写 ZAB 任何模块的文案（A+、品牌故事、副图）前，先读 `references/brand-profiles/zab.md`（品牌语气档案）。
- 一批写完后不要自行删除或移动输入图片，由用户决定是否清空。
- Canva 账号：登录方式由用户选，邮箱和验证码向用户要，不输入密码；写完问用户是否退出登录。
