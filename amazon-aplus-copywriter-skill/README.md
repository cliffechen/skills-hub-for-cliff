# amazon-aplus-copywriter-skill

亚马逊图片文案编写 Skill — A+ 模块图、From the brand 品牌故事、Listing 主图/副图。

输入设计稿构图（PNG，图中的文字视为占位符）＋产品事实（ASIN 抓取或手动填写）＋可选的对标品牌 markdown 文案库，输出一份美工可直接复制的 Excel：英文新文案 + 备选句 + 中文释义 + 事实编号 + 字符数/差值公式 + 设计修改清单。

核心是固定的工作顺序：**先读 → 出 plan → 用户确认 → 才写 → 扫描验证 → 交付 Excel**。

## 目录结构

```
amazon-aplus-copywriter-skill/
├── SKILL.md                        # skill 主文件（铁律 + 8 步流程 + 判断标准）
├── README.md                       # 本文件
├── references/                     # 规则与合规包（skill 运行时会引用）
│   ├── baseline-rules.md           # 无对标库时的写作基线 10 条
│   ├── library-digest-guide.md     # 从任意品牌 md 集提炼“规则卡”
│   ├── conflict-checklist.md       # 构图 vs 事实的 14 项冲突检查
│   ├── compliance-supplements.md   # 补剂合规包（结构/功能声明、禁用说法）
│   ├── aplus-specs.md              # A+ / 品牌故事模块尺寸与 alt 文本
│   ├── brand-voice.md              # 品牌调性位：洞察式品牌宣言写法与禁区
│   ├── persuasion-psychology.md    # 营销话术：默认成分链路式损失厌恶（正读/反读）；按需原理与站外话术
│   ├── ingredient-eli5.md          # 成分科普：ELI5 写法（本质→类比→展开→So what）
│   ├── ingredient-research.md      # 新成分调研方法论（剂量口径/缺口/作用/年龄/功效方向/原料风险）
│   ├── listing-images.md           # Listing 主图/副图规格与写法差异
│   ├── manual-facts-template.md    # 手动产品事实填空模板
│   └── ingredients/                # 成分档案：每跑一个新成分沉淀一份（_template.md、urolithin-a.md …）
├── scripts/
│   ├── build_xlsx.py               # JSON → Excel（说明/文案总表/营销话术/成分科普/设计修改清单/事实依据）；文件名自动加生成时间戳
│   └── scan_copy.py                # 合规与冲突扫描（禁用词、星号声明、alt 长度、副图标题、品牌调性位、A+ 政策词、营销话术、成分科普）
└── examples/                       # 示例：UA700 项目的真实构图、对标库与成品表
    ├── 01-示例构图-A+与品牌故事/    # 6 张 4:3 构图（Canva 导出，图上文字为占位符）
    ├── 02-示例构图-副图/            # 8 张 1600×1600 副图
    ├── 03-对标品牌文案库-OLENPHOGY/ # 对标库样例：markdown 方法库 + assets（229 个文件）
    └── 04-示例产出/                 # 两份成品 Excel（A+ 与副图）
```

## 输入

| 输入 | 形态 |
|---|---|
| 产品事实 | A. 给 ASIN（自动抓 listing）；B. 手动填写；C. 两者混用 |
| 对标品牌库 | 文件夹里任意品牌的 markdown 集，可随时更换；可缺省（缺省时用 baseline-rules） |
| 构图 | Canva 导出的 PNG/JPG；文件名或 1:1 比例用于判断是 A+、品牌故事还是 Listing 副图 |

## 用法

```bash
# 1. 无对标库时直接读 references/baseline-rules.md
# 2. 写文案（plan 经用户确认后），产出 copy.json，然后：
python3 scripts/build_xlsx.py --stamp-only          # 取时间戳，如 20261001_PM1030
python3 scripts/build_xlsx.py copy.json "B0XXXXXXXX_副图文案_v1.xlsx"
# → 实际保存为 B0XXXXXXXX_副图文案_v1_20261001_PM1030.xlsx（已带时间戳则不重复追加）

# 3. 扫描
python3 scripts/scan_copy.py copy.json \
  --forbid "1000mg,softgel,旧品牌名" --supplement --listing
```

`--supplement` 检查补剂高风险说法、以及带星号的功能句是否配了 FDA 声明；`--listing` 拦截残留的中文占位、并提醒副图标题过长。JSON 里标了 `"voice": "brand"` 的品牌调性行总会额外检查：含数字/规格/认证词或与其他行有 4 词以上重复即 FLAG（写法见 `references/brand-voice.md`）。所有行都会检查 A+ 政策词（价格/促销、buy now、now/new/limited、reviews、guarantee、#1 等）；JSON 里的 `marketing` 数组生成「营销话术」sheet，并额外检查恐吓措辞和未填的 `[N]` 占位（写法见 `references/persuasion-psychology.md`）。`explainers` 数组生成「成分科普」sheet（写法见 `references/ingredient-eli5.md`）；任何行出现本产品 `meta.claims.blocked` 里的功效方向会被拦（功效方向在 plan 阶段按成分调研确定）。

Excel 里的字符数用 LEN 公式计算；需要写入真实数值时先用 LibreOffice 重算：

```bash
soffice --headless --convert-to xlsx --outdir /tmp 待重算的文件.xlsx
```

## 示例

`examples/` 是 UA700 项目（B0XXXXXXXX，ZAB Urolithin A 700mg）的完整一组输入与产出：6 张 A+/品牌故事构图、8 张副图、一份 OLENPHOGY 对标库，以及用它们写出的两份成品 Excel（`04-示例产出/`，各 4 个 sheet）。细节见 [examples/README.md](./examples/README.md)。

## 依赖

- Python 3 + `openpyxl`
- 可选：LibreOffice（重算公式）；ASIN 模式的产品事实走 agent 自带的 web fetch，不使用 curl 绕过

## 安装

- **Claude 桌面版**：把整个文件夹打包成 `.skill`（zip）导入。桌面版只接受单文件 `SKILL.md`，可用合并版（附录 A–I：references 与 scripts 全部并入 SKILL.md，运行时写到 `/tmp/aplus/`）通过「保存 skill」安装。
- **Claude Code / QoderWork**：把 `SKILL.md` + `references/` + `scripts/` 一起拷到项目的 skills 目录即可。

## 合规边界

本 skill 用于图片文案编写与风险初筛，不构成法律意见。补剂的功效声明、认证徽章、原产地措辞，仍需按 Amazon 类目政策与 FDA/FTC 规定，结合检测报告和实物标签最终确认。
