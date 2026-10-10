# amazon-aplus-copywriter-canva

亚马逊图片文案编写 Skill 的 Canva 版——A+ 模块图、From the brand 品牌故事、Listing 主图/副图。

在原 `amazon-aplus-copywriter` 的基础上（写作文风、8 步流程、剂型与辅料规则、输入输出全部保留），增加一条 Canva 链路：

**连 Canva → 看图（每页文字位 + 缩略图 + 原备注）→ 出 plan → 用户确认 → 写 → 扫描验证 → 交付 Excel → 登录 Canva 网页按页写备注 → 回读核验**

备注按固定四区写：①上图文案 / ②设计指令（不上图）/ ③待确认 / ④审核记录。美工打开哪一页，就能看到这一页该上图的字和该改的地方，不会再把指令当成文案放上图。

## 目录结构

```
amazon-aplus-copywriter-canva/
├── SKILL.md                        # 主文件（铁律 + 原 8 步 + Canva 的 C0/C3/C9 步）
├── README.md                       # 本文件
├── CLAUDE.md / AGENTS.md           # 工作区约定（同一内容，分别给 Claude Code 和 Cursor/ZCode 读）
├── install.sh                      # 安装到 Claude Code / Cursor / ZCode / .agents 的技能目录
├── adapters/                       # 各 agent 的工具对照、MCP 配置、浏览器方式
│   ├── claude-code.md
│   ├── cursor.md                   # 含 Cloud Agent 的 computerUse 子代理用法（任意模型，含 Grok）
│   ├── zcode.md
│   └── generic.md                  # 接入任何其他 computer use agent 的检查表
├── references/
│   ├── canva-access.md             # 新：Canva 三层能力（读/看/写备注）与读取配方
│   ├── canva-notes-format.md       # 新：备注四区格式、copy.json 的 canva 块
│   ├── computer-use-canva.md       # 新：浏览器登录 Canva、逐页写备注、故障处理
│   ├── conflict-checklist.md       # 冲突检查 18 项（新增 15–18：剂型改版残留、内部指令上图、备注已改图未同步、跨页矛盾）
│   ├── compliance-supplements.md   # 补剂合规包（新增：%DV 与糖醇的标签检查提醒）
│   └── …                           # 其余与原技能相同：baseline-rules、listing-images、dosage-form-excipients、brand-profiles/zab.md 等
├── scripts/
│   ├── build_xlsx.py               # 原脚本：JSON → Excel
│   ├── scan_copy.py                # 原脚本：合规与冲突扫描
│   ├── build_notes.py              # 新：JSON → 每页备注 p{N}.txt + all_notes.md + manifest.json，并检查①区
│   ├── verify_notes.py             # 新：写后回读核验；图上文字 vs ①区同步表；内部指令上图检测；写前并发改动检测
│   └── fetch_thumbs.py             # 新：按 get-design-pages 结果批量下载缩略图
└── examples/
    ├── 04-示例产出/                 # 原技能的两份成品 Excel
    └── UA1000GUM_canva_demo_copy.json  # Canva 示例（第 3、8 页），产出与实际写入 Canva 的备注逐字一致
```

## 输入

| 输入 | 形态 |
|---|---|
| 产品事实 | A. 给 ASIN（自动抓 listing）；B. 手动填写；C. 两者混用 |
| 对标品牌库 | 文件夹里任意品牌的 markdown 集，可随时更换；可缺省（缺省时用 baseline-rules） |
| 构图 · Canva | 设计链接、设计标题、或"我最近的设计" |
| 构图 · 本地 | Canva 导出的 PNG/JPG；文件名或 1:1 比例用于判断是 A+、品牌故事还是 Listing 副图 |

## 输出

- Excel（原格式不变）：说明 / 文案总表 / 营销话术 / 成分科普 / 辅料与剂型 / 设计修改清单 / 事实依据
- Canva 每页备注（四区格式），以及本地的 `notes_{时间戳}/`（每页 txt、汇总 md、manifest）和写入前备份

## 安装

在项目根目录运行（`{技能目录}` 是本文件夹的路径，如 `skills-hub-for-cliff/amazon-aplus-copywriter-canva-skill`）。不管源文件夹叫什么，装好后的目录名统一是 `amazon-aplus-copywriter-canva`，与 SKILL.md 的 `name` 一致：

```bash
bash {技能目录}/install.sh all      # .claude/.cursor/.zcode/.agents 四处都装
bash {技能目录}/install.sh cursor   # 只装 Cursor
bash {技能目录}/install.sh claude --user   # 装到 ~/.claude/skills
pip install openpyxl
```

然后按 `adapters/` 里对应的一份接好 Canva MCP（`https://mcp.canva.com/mcp`）和浏览器能力。

## 用法

```bash
S={技能目录}/scripts
python3 $S/build_xlsx.py --stamp-only                                   # 时间戳
python3 $S/build_xlsx.py copy.json "B0XXXXXXXX_副图文案_v1.xlsx"         # Excel
python3 $S/scan_copy.py copy.json --forbid "softgel,700 mg" --supplement --listing
python3 $S/build_notes.py copy.json --out 工作区/05-输出/canva/notes_20261009_PM1030
# 写入 Canva 前：并发改动检测
python3 $S/verify_notes.py --compare notes_before.json notes_now.json
# 写入 Canva 后：回读核验 + 上图同步表
python3 $S/verify_notes.py --expected 工作区/05-输出/canva/notes_20261009_PM1030 \
  --readback notes_after.json --on-image-dir 工作区/05-输出/canva/onimage
```

## 已验证

- Cursor Cloud Agent（2026-10-09）：Canva MCP 读取 → computerUse 子代理用邮箱验证码登录 → UA1000GUM 第 1–8 页备注写入 → 回读逐字一致。`examples/UA1000GUM_canva_demo_copy.json` 用 `build_notes.py` 生成的第 3、8 页与实际写入内容逐字一致；`verify_notes.py` 能检出第 3 页图上的 "KEEP Muscle & Immune"。
- Claude 桌面端 Code 标签页（Windows，2026-10-10）：在 UA1000GUM 的两页副本上，Canva 连接器 `edit-design` 的 `replace_speaker_notes` 直接写备注、Claude in Chrome 用 `form_input` 写备注，两条通道回读均逐字一致；脚本在 Windows 下跑通。细节见 `adapters/claude-code.md`。
- ZCode：安装路径、MCP 配置和变量替换按官方文档整理，浏览器写入步骤待实机确认。

## 合规边界

本 skill 用于图片文案编写与风险初筛，不构成法律意见。补剂的功效声明、认证徽章、原产地措辞，仍需按 Amazon 类目政策与 FDA/FTC 规定，结合检测报告和实物标签最终确认。
