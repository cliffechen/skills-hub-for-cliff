#!/usr/bin/env python3
"""Build the A+ / Brand Story copy workbook from a JSON file.

Usage: python3 build_xlsx.py copy.json output.xlsx

JSON structure (all text may contain real newlines; they become in-cell line breaks):
{
  "meta": {
    "title": "B0XXXX｜A+ 与 Brand Story 文案 v1",
    "subtitle": "ASIN：...｜品牌 产品 规格｜编写日期：YYYY-MM-DD",
    "decisions": ["品牌名只用 ZAB", "..."],          # 用户在 plan 阶段拍板的事项
    "rules": ["每个数字都写清对象、单位和每份基准", "..."],  # 规则卡摘要
    "notes": ["尺寸提示……", "..."]                   # 其他说明（可选）
  },
  "rows": [                                          # 每个文字位一行
    {"id": "A1-01", "group": "A+图1", "file": "A+纯图1.png", "slot": "左侧引语",
     "placeholder": "占位原文（新增位写“（无）”，不适用写“—”）",
     "copy": "新英文文案", "alt": "备选英文", "zh": "中文释义",
     "facts": "F01, F02", "note": "合规/设计备注"}
  ],
  "issues": [                                        # 设计修改清单
    {"priority": "必改|建议|确认", "location": "...", "problem": "...", "fix": "..."}
  ],
  "facts": [                                         # 事实依据
    {"id": "F01", "fact": "...", "source": "...", "note": "..."}
  ]
}
Markup convention in copy: **bold**, *accent/italic*, trailing lone * = structure/function claim asterisk.
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT = "Arial"
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F1F1F")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY = Font(name=FONT, size=10)
WRAP = Alignment(wrap_text=True, vertical="top")
PALETTE = ["FDF2F2", "F2F6FC", "F4F9F1", "FBF7EE", "F5F0FA", "EEF8F8", "F3F3F3", "FFF8E6"]
PRI_FILL = {"必改": "F8D7DA", "建议": "FFF3CD", "确认": "D9E7F7"}


def style_table(ws, widths):
    for row in ws.iter_rows():
        for c in row:
            c.font = BODY
            c.alignment = WRAP
            c.border = BORDER
    for c in ws[1]:
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    meta = data.get("meta", {})
    wb = Workbook()

    # --- 说明 ---
    ws = wb.active
    ws.title = "说明"
    lines = [(meta.get("title", "A+ 文案"), "title"), (meta.get("subtitle", ""), None), ("", None),
             ("怎么用这份表", "h")]
    lines += [(t, None) for t in [
        "1. 「文案总表」每行对应构图里的一个文字位。设计直接复制E列（新英文文案），F列是备选句。",
        "2. 标注约定：**…** 表示加粗，*…* 表示强调色/斜体，句尾单独的 * 是功能声明星号（要和FDA免责声明对应）。单元格里怎么换行，排版就怎么换行。",
        "3. H列/I列用 LEN 公式统计新文案和占位原文的字符数，J列是差值（正数=比原稿长）。差值超过 +10 的位置，需要设计检查是否放得下。",
        "4. 「设计修改清单」列出图片或素材层面要改的地方（不是文案），上线前需要逐项关掉。",
        "5. 「事实依据」列出每条文案引用的事实编号（F01…）及出处。",
    ]]
    if meta.get("decisions"):
        lines += [("", None), ("本次已确认的决定", "h")] + [("· " + d, None) for d in meta["decisions"]]
    if meta.get("rules"):
        lines += [("", None), ("写作规则（规则卡摘要）", "h")] + [("· " + r, None) for r in meta["rules"]]
    if meta.get("notes"):
        lines += [("", None), ("其他说明", "h")] + [("· " + n, None) for n in meta["notes"]]
    for i, (t, kind) in enumerate(lines, 1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(name=FONT, bold=kind is not None, size=14 if kind == "title" else (11 if kind else 10))
        c.alignment = WRAP
    ws.column_dimensions["A"].width = 120

    # --- 文案总表 ---
    ws = wb.create_sheet("文案总表")
    headers = ["编号", "图片", "构图文件", "文字位置", "新英文文案", "备选英文", "中文释义",
               "新文案字符数", "占位原文字符数", "差值", "占位原文（设计稿）", "事实依据", "合规 / 设计备注"]
    ws.append(headers)
    groups = []
    for r in data["rows"]:
        g = r.get("group", "")
        if g not in groups:
            groups.append(g)
        ws.append([r.get("id", ""), g, r.get("file", ""), r.get("slot", ""), r.get("copy", ""),
                   r.get("alt", ""), r.get("zh", ""), None, None, None, r.get("placeholder", ""),
                   r.get("facts", ""), r.get("note", "")])
        n = ws.max_row
        ws.cell(n, 8).value = f"=LEN(E{n})"
        ws.cell(n, 9).value = f'=IF(OR(K{n}="—",K{n}="",LEFT(K{n},1)="（"),"",LEN(K{n}))'
        ws.cell(n, 10).value = f'=IF(I{n}="","",H{n}-I{n})'
    style_table(ws, [8, 10, 16, 24, 44, 34, 28, 9, 9, 7, 34, 12, 52])
    for n in range(2, ws.max_row + 1):
        fill = PatternFill("solid", fgColor=PALETTE[groups.index(ws.cell(n, 2).value) % len(PALETTE)])
        for col in range(1, len(headers) + 1):
            ws.cell(n, col).fill = fill
        ws.cell(n, 5).font = Font(name=FONT, bold=True, size=10, color="C00000")
        ws.cell(n, 11).font = Font(name=FONT, size=9, color="808080")
    ws.freeze_panes = "E2"
    ws.auto_filter.ref = f"A1:M{ws.max_row}"
    ws.row_dimensions[1].height = 30

    # --- 设计修改清单 ---
    ws = wb.create_sheet("设计修改清单")
    ws.append(["#", "优先级", "位置", "问题", "建议处理", "状态"])
    for i, it in enumerate(data.get("issues", []), 1):
        ws.append([i, it.get("priority", "建议"), it.get("location", ""), it.get("problem", ""),
                   it.get("fix", ""), it.get("status", "待处理")])
    style_table(ws, [5, 8, 24, 50, 50, 10])
    for n in range(2, ws.max_row + 1):
        p = ws.cell(n, 2).value
        if p in PRI_FILL:
            ws.cell(n, 2).fill = PatternFill("solid", fgColor=PRI_FILL[p])

    # --- 事实依据 ---
    ws = wb.create_sheet("事实依据")
    ws.append(["编号", "事实", "出处", "备注"])
    for f in data.get("facts", []):
        ws.append([f.get("id", ""), f.get("fact", ""), f.get("source", ""), f.get("note", "")])
    style_table(ws, [6, 56, 50, 48])

    wb.save(out)
    print(f"saved {out}  rows={len(data['rows'])} issues={len(data.get('issues', []))} facts={len(data.get('facts', []))}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build_xlsx.py copy.json output.xlsx")
    main(sys.argv[1], sys.argv[2])
