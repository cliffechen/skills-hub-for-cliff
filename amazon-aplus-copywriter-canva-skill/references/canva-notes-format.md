# Canva 备注四区格式

每页备注写给两类人：美工（照着改图）和下一轮的 agent（照着审图）。两者都要一眼分清"哪些字上图、哪些字是指令"。所以格式固定，区块标题一字不改。

## 格式

```
[P{N} · {页面角色}]
【备注规则】只有①区内容可以上图；②③④区一律不得出现在图上。

【① 上图文案 ON-IMAGE】{可选限定，如（必须与实物标签逐字一致）}
{可选前置说明，如（主图为纯白底产品图，图上不加任何文字；以下仅为瓶身标签核对用）}
{文字位}：{英文文案}
{文字位}：{英文文案}
页脚：*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.

【② 设计指令 DESIGNER ONLY · 不上图】
- {具体操作}

【③ 待确认 TO CONFIRM】
- {需要证据或拍板的事}

【④ 审核记录 REVIEW LOG】
- {YYYY-MM-DD}：{本次发现的问题}
```

规则：

1. **①区只放上图的字。** 文字位名用中文（H1、副标、正文 1、图标 1、页脚、瓶标……），冒号后是英文原文，逐字照抄即可上图。①区的值里不能有中文、不能有指令（KEEP / Remove / Replace / Optional: / DO NOT / → / [Page …]）。可选文案放进①区时，文字位写成"可选："，不要写成英文 `Optional:`。
2. **FDA 页脚在①区写全文**，不写"标准 FDA 页脚"这类简称——美工只看这一页也能直接复制。②区提到时写"FDA 页脚（原文见①区）"。
3. **②区写动作，不写判断。** "删除图上 'KEEP Muscle & Immune'（内部指令误上图）"，而不是"这页有问题"。图上现有文字与①区不同的，写"由 '旧文案' 替换为上面的新标题"。
4. **③区写需要谁做什么。** 证书、实物标签、功效取舍、页序调整。没有就写"- 无。"。
5. **④区只增不删。** 每次审核追加一行带日期的记录；下一轮先读④区，知道上次发现了什么、改了没有。
6. **单页 ≤5000 字符**（Canva 备注上限）。超了先压缩②区措辞，不删①区。
7. **语言**：①区英文文案；页面角色、区块标题、②③④区用用户的工作语言（默认中文）。
8. **①区的 `*` 只表示功能声明星号。** 不用 `**…**`、`*…*` 标粗体和斜体，否则分不清哪个星号要上图；样式写在文字位名称里：`H1（第 2 行粗体）`、`H1 第 2 行（衬线斜体）`、`剂量行（1,000 mg 粗体）`。`build_notes.py` 遇到样式标记会 FLAG。
9. **表格类文字位**一行写成 `左列 | 右列`，并在文字位名称里写明（`列头 左｜右`、`第 1 行`）。

## 多版文案（A / B / C）

用户要求每个文字位给多版时（用户 2026-10-10：三版都进 Excel 和备注，自己就是设计，不需要先选），不改 JSON 结构，用文字位名称区分：

```
【① 上图文案 ON-IMAGE】
（A / B / C 三版任选其一，【共用】各项三版相同）
【A】H1（第 2 行粗体）：What Your Cells Get
Every Morning*
【B】H1（第 2 行粗体）：Two Softgels a Day.
Here's What They Support.*
【C】H1（第 2 行粗体）：Start Where Energy Starts:
Inside the Cell.*
共用·图标 1：Mitochondrial Health*
共用·页脚：*These statements have not been evaluated by the Food and Drug Administration. …
```

- **rows**：每个版本一行，`slot` 以 `【A】`、`【B】`、`【C】` 开头；三版相同的项（功效图标、FDA 页脚、徽章、剂量行）只写一行，`slot` 以 `共用·` 开头。同一页的行按 A 全部 → B 全部 → C 全部 → 共用 的顺序排，方便整版对照。这时不再用 `alt`（备选）字段。
- **`canva.pages[].on_image_preface`**：写一行 `（A / B / C 三版任选其一，【共用】各项三版相同）`。
- **③区**：加一条“从 A / B / C 里选定一版再上图，可以按文字位混搭”，再逐条写各版要注意的事（哪版标题超过 45 字符、哪两页用了同一句、哪版的说法需要额外证据）。
- **②区**：指令不能绑定某一版的文字，写成“文字用①区选定的那一版”。
- **只有一版的页**（如 Supplement Facts 标签页）：`on_image_preface` 写明“标签正文只有一版”，能选的部分（如小标题）单独列 `【B】小标题`、`【C】小标题`，“A 版不加”写进③区。
- **长度**：三版加起来仍要 ≤5000 字符；实测 4 行表格的三版约 1,950 字符。
- **`verify_notes.py --on-image-dir`**：多版时没被选中的版本都会显示“未上图”，属于正常。
- 各版要真的不同（换角度、换买家怀疑点、换长短），不是同一句换词；每版都过合规和品牌禁用词。
- 用户选定后，把①区收成一版：重新生成备注并覆盖写入，④区追加一行“选定 14A / 15B …”。

## JSON 里的 `canva` 块

在原 `copy.json` 结构（见 `scripts/build_xlsx.py` 顶部注释）上增加，`build_xlsx.py` 会忽略这些字段，`build_notes.py` 读取它们：

```json
{
  "rows": [
    {"id": "P3-01", "page": 3, "group": "副图3", "slot": "H1",
     "placeholder": "Made Simple. Daily Urolithin A",
     "copy": "You've Read About Urolithin A. Here's 1,000 mg of It.*", "alt": "…", "zh": "…",
     "facts": "F01", "note": "…"}
  ],
  "issues": [
    {"page": 3, "priority": "必改", "location": "P3 标题区",
     "problem": "内部指令误上图", "fix": "删除图上 \"KEEP Muscle & Immune\""}
  ],
  "canva": {
    "design_id": "DAHR284bBN8",
    "design_title": "UA1000GUM",
    "edit_url": "https://www.canva.com/d/F0zXoW2J2HkOVqB",
    "write_mode": "replace",
    "review_date": "2026-10-09",
    "pages": [
      {"page": 3, "page_id": "PBPkKTdQ4vzP9tQY", "label": "钩子 Hook",
       "on_image_hint": "", "on_image_preface": "",
       "designer": ["H1 改为无衬线字体，与其他页统一"],
       "confirm": ["\"Immune Function\" 合规风险最高，确认是否保留"],
       "log": ["内部指令误上图（严重）；缺 FDA 页脚"]}
    ]
  }
}
```

拼装规则（`build_notes.py`）：

| 区 | 来源 |
|---|---|
| ① | `rows` 里 `page == N` 的行，按出现顺序输出 `{slot}：{copy}`；`slot` 为空时只输出 `copy`（Supplement Facts 这类逐行照抄的标签）；`id` 以 `ALT` 开头的行不输出 |
| ② | `canva.pages[].designer` → 再接 `issues` 里 `page == N` 且 priority 为 必改/建议 的条目（输出 `{fix}（{problem}）`） |
| ③ | `canva.pages[].confirm` → 再接 `issues` 里 priority 为 确认 的条目 |
| ④ | `canva.pages[].log`，每条前加 `review_date`；`write_mode` 为 `archive` 时，在④区后追加【⑤ 原备注 ARCHIVE】放写入前的原文（需传 `--before notes_before.json`） |

`write_mode`：`replace`（默认，覆盖；写入前必须备份）/ `archive`（覆盖，并把原备注附在末尾）。

## 示例

`examples/UA1000GUM_canva_demo_copy.json` 是 UA1000GUM 第 3、8 页的最小示例，`build_notes.py` 产出的文本与 2026-10-09 实际写进 Canva 的备注逐字一致。
