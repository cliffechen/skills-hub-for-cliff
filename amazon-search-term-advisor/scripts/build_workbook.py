#!/usr/bin/env python3
"""
Build a 3-tab Sponsored Products search-term analysis workbook from a raw
Amazon Advertising "Sponsored Products Search term report" (.xlsx/.csv).

Supports both English and Chinese (simplified) column headers. The input's
language is auto-detected from its column names, and the output workbook
(sheet names, header labels, TOTAL row, and default output filename) is
produced in the SAME language as the input.

Usage:
    python build_workbook.py <input_report> [output.xlsx]

Tabs produced (in this exact order):
    1. Customer Search Terms / 客户搜索词      - every unique search term, aggregated
    2. Targeting / 投放                         - every unique target, aggregated
    3. Untargeted Search Terms / 未投放搜索词   - search terms with no matching target

Each tab has 13 columns:
    <label> | Impressions | Clicks | Spend | Spend % | Sales | Sales % |
    Orders | Orders % | CTR | CVR | CPC | ACOS
(or the Chinese equivalents — see HEADERS_ZH below)

Percentages and ratios are written as live Excel FORMULAS referencing the
tab's own TOTAL row, so the workbook stays dynamic. Run the xlsx skill's
recalc.py afterward to populate values and confirm zero formula errors.
"""
import sys, re, os, math
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------- load & map
def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()

def find_col(cols, *, equals=None, contains=None):
    """Resolve a column name robustly (trailing spaces, case, day-window vary)."""
    n = {c: norm(c) for c in cols}
    if equals:
        for c, v in n.items():
            if v == norm(equals):
                return c
    if contains:
        needle = norm(contains)
        for c, v in n.items():
            if needle in v:
                return c
    return None

# Each field is tried in English first, then Chinese (order doesn't affect
# detection — whichever set actually matches determines the report language).
# NOTE: the Chinese "contains" patterns are deliberately specific
# ("总销售额" / "总订单数") so they don't accidentally match adjacent columns
# like "7天内广告SKU销售额" or "7天总销售量(#)" that also appear in the
# standard Amazon CN search-term export.
FIELD_ALIASES = {
    "cst": {"en": dict(equals="Customer Search Term"), "zh": dict(equals="客户搜索词")},
    "tgt": {"en": dict(equals="Targeting"),             "zh": dict(equals="投放")},
    "imp": {"en": dict(equals="Impressions"),           "zh": dict(equals="展示量")},
    "clk": {"en": dict(equals="Clicks"),                "zh": dict(equals="点击量")},
    "sp":  {"en": dict(equals="Spend"),                 "zh": dict(equals="花费")},
    "sal": {"en": dict(contains="Total Sales"),         "zh": dict(contains="总销售额")},
    "ord": {"en": dict(contains="Total Orders"),        "zh": dict(contains="总订单数")},
}

def load(path):
    if path.lower().endswith((".csv", ".tsv")):
        sep = "\t" if path.lower().endswith(".tsv") else ","
        df = pd.read_csv(path, sep=sep)
    else:
        df = pd.read_excel(path)
    cols = list(df.columns)

    m = {}
    votes = {"en": 0, "zh": 0}
    for key, by_lang in FIELD_ALIASES.items():
        hit, hit_lang = None, None
        for lang in ("en", "zh"):
            c = find_col(cols, **by_lang[lang])
            if c:
                hit, hit_lang = c, lang
                break
        m[key] = hit
        if hit_lang:
            votes[hit_lang] += 1

    missing = [k for k, v in m.items() if v is None]
    if missing:
        raise SystemExit(
            f"Could not locate required column(s) {missing}. "
            f"Columns present: {cols}"
        )

    # Report language = whichever alias set matched more fields (in practice
    # a report is consistently all-English or all-Chinese, so this is decisive).
    lang = "zh" if votes["zh"] >= votes["en"] else "en"
    return df, m, lang


# ------------------------------------------------------------------- reshape
def prepare(df, m):
    for k in ("imp", "clk", "sp", "sal", "ord"):
        df[m[k]] = pd.to_numeric(df[m[k]], errors="coerce").fillna(0)
    df["_cst"] = df[m["cst"]].astype(str).str.strip()
    df["_tgt"] = df[m["tgt"]].astype(str).str.strip()
    df = df[df["_cst"] != ""].copy()          # drop blank search-term rows
    df["_cstk"] = df["_cst"].str.lower()       # case-insensitive match keys
    df["_tgtk"] = df["_tgt"].str.lower()
    return df

def agg(frame, keycol, labelcol, m):
    """Sum metrics per (case-insensitive) key; keep first-seen original label."""
    g = frame.groupby(keycol).agg(
        _label=(labelcol, "first"),
        Impressions=(m["imp"], "sum"),
        Clicks=(m["clk"], "sum"),
        Spend=(m["sp"], "sum"),
        Sales=(m["sal"], "sum"),
        Orders=(m["ord"], "sum"),
        _key=(keycol, "first"),
    ).reset_index(drop=True)
    return g

def srt(g):
    # Sales desc is the requirement; Spend/Impressions desc break ties so the
    # biggest wasted-spend (zero-sales) terms surface at the top of that block.
    return g.sort_values(
        by=["Sales", "Spend", "Impressions", "Clicks"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)


# ------------------------------------------------------------ recommendations
# Statistically-driven action rules (no hardcoded target ACOS / min-order count —
# every threshold is derived from the report's own data so the sheet stays valid
# across accounts/categories):
#
#   ACOS "high"/"low"  -> quartiles (Q1/Q3) of ACOS among that tab's own
#                          sales-generating rows. A row above Q3 is under-
#                          performing relative to its own peer group; below Q1
#                          is out-performing. No fixed target ACOS required.
#   "enough orders?"    -> 95% Wilson score confidence interval on CVR
#                          (Orders/Clicks). A term only gets a directional
#                          call (negate / scale up) when the interval is both
#                          narrow enough to trust AND clearly separated from
#                          the account's blended CVR. Otherwise it's flagged
#                          "observe" instead of guessed at.
WILSON_Z = 1.96
WIDE_CI = 0.20          # interval wider than this = sample too small to trust
OBVIOUS_P = 0.12        # Poisson P(zero orders | expected count) below this = "obvious", not just noise
RATIO_MULT = 3          # actual CVR >= this many x account average = "obviously promising"

def wilson_ci(orders, clicks, z=WILSON_Z):
    if clicks <= 0:
        return None, None
    p = orders / clicks
    denom = 1 + z * z / clicks
    center = (p + z * z / (2 * clicks)) / denom
    margin = z * math.sqrt((p * (1 - p) / clicks) + (z * z) / (4 * clicks * clicks)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)

ACT = {
    "harvest":       {"en": "Harvest to Exact",            "zh": "收割为精准词"},
    "negate":        {"en": "Negative Keyword Candidate",  "zh": "否定词候选"},
    "likely_negate": {"en": "Probable Negative - Review",  "zh": "疑似否定-建议复核"},
    "scale_up":      {"en": "Increase Bid / Budget",       "zh": "加大力度/提高出价"},
    "likely_scale_up":{"en": "Promising - Worth Watching", "zh": "疑似优质-建议关注"},
    "scale_down":    {"en": "Decrease Bid / Pause",        "zh": "降低出价/减少投入"},
    "watch_small":   {"en": "Observe - Sample Too Small",  "zh": "观察-样本不足"},
    "watch_nodata":  {"en": "Observe - No Clicks",          "zh": "观察-无点击数据"},
    "maintain":      {"en": "Maintain",                     "zh": "维持现状"},
}

def build_recommendations(t1, target_keys, lang):
    """One row per customer search term with a statistically-grounded action."""
    df = t1.copy()
    df["ACOS"] = df.apply(lambda r: (r["Spend"] / r["Sales"]) if r["Sales"] > 0 else None, axis=1)

    total_clicks = df["Clicks"].sum()
    total_orders = df["Orders"].sum()
    baseline_cvr = (total_orders / total_clicks) if total_clicks else 0.0

    sales_rows = df[df["Sales"] > 0]
    have_quartiles = len(sales_rows) >= 4
    q1 = sales_rows["ACOS"].quantile(0.25) if have_quartiles else None
    q3 = sales_rows["ACOS"].quantile(0.75) if have_quartiles else None

    def r_en(v, d=1):
        return f"{v*100:.{d}f}%"

    rows = []
    for _, r in df.iterrows():
        clicks, orders = int(r["Clicks"]), int(r["Orders"])
        untargeted = r["_key"] not in target_keys
        acos = r["ACOS"]

        if untargeted and orders >= 1:
            act = "harvest"
            reason_en = (f"Not currently targeted, but has driven {orders} order(s) — "
                         f"add as an exact-match keyword to take control of this converting query.")
            reason_zh = f"当前未被精准投放，但已产生{orders}笔订单——建议加为精准匹配词，主动掌握该词流量。"
        elif clicks == 0:
            act = "watch_nodata"
            reason_en = "No clicks yet — insufficient data to evaluate."
            reason_zh = "尚无点击数据，无法评估，继续观察。"
        else:
            lo, hi = wilson_ci(orders, clicks)
            width = hi - lo
            exp_orders = clicks * baseline_cvr
            poisson_p0 = math.exp(-exp_orders) if exp_orders > 0 else 1.0
            actual_cvr = orders / clicks
            ratio = (actual_cvr / baseline_cvr) if baseline_cvr > 0 else None

            if orders == 0 and hi < baseline_cvr * 0.5:
                # High-confidence call: even the optimistic end of the CI sits
                # well below account average — safe to call this with 95% confidence.
                act = "negate"
                reason_en = (f"{clicks} clicks, 0 orders — CI upper bound {r_en(hi)} is confidently "
                              f"below the account average CVR ({r_en(baseline_cvr)}).")
                reason_zh = f"点击{clicks}次零转化，置信区间上界{r_en(hi)}显著低于账户平均转化率{r_en(baseline_cvr)}，统计上可判定确实低效。"
            elif have_quartiles and acos is not None and acos <= q1 and lo >= baseline_cvr:
                act = "scale_up"
                reason_en = (f"ACOS {r_en(acos)} is in the best quartile for this report (\u2264{r_en(q1)}), "
                              f"and CVR CI lower bound {r_en(lo)} is at/above account average.")
                reason_zh = f"ACOS {r_en(acos)}处于本表最优四分位（\u2264{r_en(q1)}），且转化率置信区间下界{r_en(lo)}不低于账户平均水平，建议加大投入。"
            elif have_quartiles and acos is not None and acos >= q3:
                act = "scale_down"
                reason_en = f"ACOS {r_en(acos)} is in the worst quartile for this report (\u2265{r_en(q3)})."
                reason_zh = f"ACOS {r_en(acos)}处于本表最差四分位（\u2265{r_en(q3)}），建议降低出价或减少投入。"
            elif orders == 0 and poisson_p0 < OBVIOUS_P:
                # The strict CI test missed this because clicks aren't huge, but
                # the expected-value read is still hard to ignore: at the account's
                # own average CVR this term "should" have produced ~exp_orders
                # order(s) by now. Seeing exactly zero has <10% probability by
                # chance alone — an obvious pattern worth a human's eyes even
                # though it doesn't clear the stricter 95%-CI bar for "negate".
                act = "likely_negate"
                reason_en = (f"At the account's average CVR ({r_en(baseline_cvr)}), {clicks} clicks "
                              f"would be expected to yield ~{exp_orders:.1f} order(s); seeing 0 has only "
                              f"a {poisson_p0*100:.0f}% chance if this term performed at average — "
                              f"obvious enough to flag, though the sample is too small for full 95% confidence.")
                reason_zh = (f"按账户平均转化率{r_en(baseline_cvr)}测算，{clicks}次点击理应产生约{exp_orders:.1f}单，"
                              f"实际0单——若该词表现与账户平均持平，出现0单的概率仅{poisson_p0*100:.0f}%，特征已经比较明显，"
                              f"建议人工复核是否否定（样本量尚未达到95%置信区间的严格标准）。")
            elif orders >= 2 and ratio is not None and ratio >= RATIO_MULT:
                # Small sample, so the CI is wide and won't clear the strict
                # scale_up bar — but a 3x-or-better actual CVR vs. account
                # average, with at least 2 real orders behind it, is too
                # obvious a signal to file under "just keep watching".
                act = "likely_scale_up"
                reason_en = (f"Actual CVR ({r_en(actual_cvr)}) is {ratio:.1f}\u00d7 the account average "
                              f"on {orders} order(s) — promising even though the sample is still small; "
                              f"worth prioritizing for more data/budget.")
                reason_zh = (f"实际转化率{r_en(actual_cvr)}是账户平均的{ratio:.1f}倍（{orders}笔订单支撑），"
                              f"虽然样本量还小、置信区间较宽，但比值已相当明显，建议优先关注/适当加大投入以积累更多数据。")
            elif width > WIDE_CI:
                act = "watch_small"
                reason_en = (f"{clicks} click(s), 95% CI for CVR is [{r_en(lo)}, {r_en(hi)}] — "
                              f"too wide to draw a conclusion yet.")
                reason_zh = f"点击{clicks}次，转化率95%置信区间为[{r_en(lo)}, {r_en(hi)}]，区间过宽，样本不足以下结论。"
            else:
                act = "maintain"
                reason_en = "No statistically clear signal in either direction — leave as-is."
                reason_zh = "当前数据未显示明确的统计信号，建议维持现状。"

        rows.append({
            "_label": r["_label"], "Impressions": r["Impressions"], "Clicks": r["Clicks"],
            "Spend": r["Spend"], "Sales": r["Sales"], "Orders": r["Orders"],
            "ACOS": acos, "_action_key": act,
            "_action": ACT[act][lang], "_reason": reason_zh if lang == "zh" else reason_en,
        })

    out = pd.DataFrame(rows)
    # Surface the terms that need a human decision first; passive rows sink.
    order_map = {"harvest": 0, "negate": 1, "likely_negate": 2, "scale_up": 3,
                 "likely_scale_up": 4, "scale_down": 5, "watch_small": 6,
                 "watch_nodata": 7, "maintain": 8}
    out["_ord"] = out["_action_key"].map(order_map)
    out = out.sort_values(by=["_ord", "Spend"], ascending=[True, False]).reset_index(drop=True)
    return out, baseline_cvr, q1, q3


# -------------------------------------------------------------------- styling
HDR_FILL = PatternFill("solid", fgColor="1F3864")   # navy house style
TOT_FILL = PatternFill("solid", fgColor="D9E1F2")   # light blue
HDR_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=10)
TOT_FONT = Font(name="Arial", bold=True, color="000000", size=10)
BODY_FONT = Font(name="Arial", size=10)
_thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)

# Zero renders as "-" to keep large tables readable (financial-model convention)
CUR = '$#,##0.00;($#,##0.00);"-"'
INT = '#,##0;(#,##0);"-"'
PCT = '0.00%;(0.00%);"-"'

COLFMT = {1: INT, 2: INT, 3: CUR, 4: PCT, 5: CUR, 6: PCT, 7: INT,
          8: PCT, 9: PCT, 10: PCT, 11: CUR, 12: PCT}
WIDTHS = {0: 52, 1: 13, 2: 9, 3: 11, 4: 10, 5: 12, 6: 10,
          7: 9, 8: 10, 9: 9, 10: 9, 11: 9, 12: 9}

# Recommendation-sheet row tint by action, so priority is visible at a glance
ACT_FILL = {
    "harvest":         PatternFill("solid", fgColor="C6E0B4"),  # green  - opportunity
    "scale_up":        PatternFill("solid", fgColor="C6E0B4"),  # green
    "likely_scale_up": PatternFill("solid", fgColor="E2EFDA"),  # pale green - promising, still thin data
    "negate":          PatternFill("solid", fgColor="F8CBAD"),  # red    - stop the bleed
    "scale_down":      PatternFill("solid", fgColor="F8CBAD"),  # red
    "likely_negate":   PatternFill("solid", fgColor="FBE5D6"),  # pale red - obvious but not 95%-confirmed
    "watch_small":     PatternFill("solid", fgColor="FFE699"),  # amber  - not enough data
    "watch_nodata":    PatternFill("solid", fgColor="FFE699"),  # amber
    "maintain":        PatternFill("solid", fgColor="F2F2F2"),  # grey   - no action needed
}
REC_COLFMT = {1: INT, 2: INT, 3: CUR, 4: CUR, 5: INT, 6: PCT}
REC_WIDTHS = {0: 44, 1: 13, 2: 9, 3: 11, 4: 12, 5: 9, 6: 10, 7: 26, 8: 70}

# ----------------------------------------------------------- language packs
# Everything user-visible (sheet names, headers, TOTAL label, output suffix)
# switches together based on the detected input language.
LANG = {
    "en": {
        "headers": ["{LABEL}", "Impressions", "Clicks", "Spend", "Spend %",
                    "Sales", "Sales %", "Orders", "Orders %", "CTR", "CVR",
                    "CPC", "ACOS"],
        "label_cst": "Customer Search Term",
        "label_tgt": "Targeting",
        "sheet_cst": "Customer Search Terms",
        "sheet_tgt": "Targeting",
        "sheet_untargeted": "Untargeted Search Terms",
        "total": "TOTAL",
        "out_suffix": "_Analysis.xlsx",
        "sheet_rec": "Action Recommendations",
        "rec_headers": ["Customer Search Term", "Impressions", "Clicks", "Spend",
                         "Sales", "Orders", "ACOS", "Recommended Action", "Why"],
        "rec_note": ("Thresholds are derived from this report's own data, not fixed "
                      "targets: ACOS high/low = this report's own quartiles (Q1/Q3) "
                      "among sales-generating terms; the primary \"enough orders?\" "
                      "test is a 95% Wilson confidence interval on conversion rate vs. "
                      "the account average. Terms whose sample is too small to clear "
                      "that 95% bar, but whose numbers are still an obvious outlier "
                      "(expected-order-count/Poisson check for zero-order terms, "
                      "3x-average-CVR check for small positive samples), are flagged "
                      "separately as \"Probable\" / \"Promising\" for manual review "
                      "rather than silently defaulting to \"Maintain.\""),
    },
    "zh": {
        "headers": ["{LABEL}", "展示量", "点击量", "花费", "花费占比",
                    "销售额", "销售额占比", "订单量", "订单占比",
                    "点击率(CTR)", "转化率(CVR)", "单次点击成本(CPC)",
                    "广告成本占比(ACOS)"],
        "label_cst": "客户搜索词",
        "label_tgt": "投放",
        "sheet_cst": "客户搜索词",
        "sheet_tgt": "投放",
        "sheet_untargeted": "未投放搜索词",
        "total": "总计",
        "out_suffix": "_分析.xlsx",
        "sheet_rec": "实操建议",
        "rec_headers": ["客户搜索词", "展示量", "点击量", "花费",
                         "销售额", "订单量", "ACOS", "建议动作", "判断依据"],
        "rec_note": ("阈值均来自本报告数据本身，非固定目标值：ACOS高低="
                      "本表内有销售词的四分位数(Q1/Q3)；主要的\"订单量是否足够\"检验="
                      "转化率95% Wilson置信区间与账户平均转化率的比较。"
                      "对于样本量没达到95%置信标准、但数据本身已是明显异常值的词"
                      "（零转化词用期望订单数/Poisson概率检验，小样本正转化词用"
                      "\"实际转化率≥账户平均3倍\"检验），会单独标为\"疑似\"类别"
                      "提醒人工复核，而不是被严格阈值一刀切归入\"维持现状\"。"),
    },
}


def build_sheet(ws, dframe, label_header, pack):
    n = len(dframe)
    last = n + 1          # last data row (data starts at row 2)
    tot = n + 2           # TOTAL row directly below the data
    hdrs = pack["headers"].copy(); hdrs[0] = label_header

    for j, h in enumerate(hdrs):
        c = ws.cell(1, j + 1, h)
        c.fill = HDR_FILL; c.font = HDR_FONT; c.border = BORDER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i in range(n):
        r = i + 2
        row = dframe.iloc[i]
        ws.cell(r, 1, row["_label"])
        ws.cell(r, 2, float(row["Impressions"]))
        ws.cell(r, 3, float(row["Clicks"]))
        ws.cell(r, 4, float(row["Spend"]))
        ws.cell(r, 5, f"=IF($D${tot}=0,0,D{r}/$D${tot})")   # Spend %
        ws.cell(r, 6, float(row["Sales"]))
        ws.cell(r, 7, f"=IF($F${tot}=0,0,F{r}/$F${tot})")   # Sales %
        ws.cell(r, 8, float(row["Orders"]))
        ws.cell(r, 9, f"=IF($H${tot}=0,0,H{r}/$H${tot})")   # Orders %
        ws.cell(r, 10, f"=IF(B{r}=0,0,C{r}/B{r})")          # CTR = Clk/Imp
        ws.cell(r, 11, f"=IF(C{r}=0,0,H{r}/C{r})")          # CVR = Ord/Clk
        ws.cell(r, 12, f"=IF(C{r}=0,0,D{r}/C{r})")          # CPC = Spend/Clk
        ws.cell(r, 13, f"=IF(F{r}=0,0,D{r}/F{r})")          # ACOS = Spend/Sales

    ws.cell(tot, 1, pack["total"])
    for col, L in [(2, "B"), (3, "C"), (4, "D"), (6, "F"), (8, "H")]:
        ws.cell(tot, col, f"=SUM({L}2:{L}{last})" if n else 0)
    ws.cell(tot, 5, f"=IF($D${tot}=0,0,D{tot}/$D${tot})")
    ws.cell(tot, 7, f"=IF($F${tot}=0,0,F{tot}/$F${tot})")
    ws.cell(tot, 9, f"=IF($H${tot}=0,0,H{tot}/$H${tot})")
    ws.cell(tot, 10, f"=IF(B{tot}=0,0,C{tot}/B{tot})")
    ws.cell(tot, 11, f"=IF(C{tot}=0,0,H{tot}/C{tot})")
    ws.cell(tot, 12, f"=IF(C{tot}=0,0,D{tot}/C{tot})")
    ws.cell(tot, 13, f"=IF(F{tot}=0,0,D{tot}/F{tot})")

    for r in range(2, tot + 1):
        is_tot = (r == tot)
        for j in range(13):
            c = ws.cell(r, j + 1)
            c.font = TOT_FONT if is_tot else BODY_FONT
            c.border = BORDER
            if is_tot:
                c.fill = TOT_FILL
            if j == 0:
                c.alignment = Alignment(horizontal="left", vertical="center")
            else:
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = COLFMT[j]

    for j, w in WIDTHS.items():
        ws.column_dimensions[get_column_letter(j + 1)].width = w
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"                       # keep header visible
    # Autofilter covers data only (NOT the TOTAL row) so filtering never hides it
    ws.auto_filter.ref = f"A1:M{last}"


def build_recommendation_sheet(ws, rec_df, pack, baseline_cvr, q1, q3, lang):
    hdrs = pack["rec_headers"]
    for j, h in enumerate(hdrs):
        c = ws.cell(1, j + 1, h)
        c.fill = HDR_FILL; c.font = HDR_FONT; c.border = BORDER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    n = len(rec_df)
    for i in range(n):
        r = i + 2
        row = rec_df.iloc[i]
        vals = [row["_label"], float(row["Impressions"]), float(row["Clicks"]),
                float(row["Spend"]), float(row["Sales"]), float(row["Orders"]),
                (float(row["ACOS"]) if row["ACOS"] is not None else 0.0),
                row["_action"], row["_reason"]]
        fill = ACT_FILL[row["_action_key"]]
        for j, v in enumerate(vals):
            c = ws.cell(r, j + 1, v)
            c.font = BODY_FONT
            c.border = BORDER
            c.fill = fill
            if j == 0:
                c.alignment = Alignment(horizontal="left", vertical="center")
            elif j == 7:
                c.alignment = Alignment(horizontal="left", vertical="center")
            elif j == 8:
                c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            else:
                c.alignment = Alignment(horizontal="right", vertical="center")
                if j in REC_COLFMT:
                    c.number_format = REC_COLFMT[j]

    # Methodology note below the table
    note_row = n + 3
    baseline_txt = (f"{'账户平均转化率' if lang=='zh' else 'Account avg CVR'}: "
                     f"{baseline_cvr*100:.1f}%")
    quart_txt = (f"{'ACOS四分位' if lang=='zh' else 'ACOS quartiles'}: "
                 f"Q1={q1*100:.1f}%, Q3={q3*100:.1f}%") if q1 is not None else \
                ("样本不足，未启用ACOS四分位分档" if lang == "zh"
                 else "Not enough sales rows to compute ACOS quartiles this run")
    ws.cell(note_row, 1, pack["rec_note"]).font = Font(name="Arial", size=9, italic=True, color="666666")
    ws.cell(note_row + 1, 1, f"{baseline_txt}   |   {quart_txt}").font = \
        Font(name="Arial", size=9, italic=True, color="666666")

    for j, w in REC_WIDTHS.items():
        ws.column_dimensions[get_column_letter(j + 1)].width = w
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:I{n + 1}"


# ---------------------------------------------------------------------- main
def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]

    df, m, lang = load(src)
    pack = LANG[lang]

    out = sys.argv[2] if len(sys.argv) > 2 else \
        os.path.splitext(os.path.basename(src))[0] + pack["out_suffix"]

    df = prepare(df, m)

    t1 = srt(agg(df, "_cstk", "_cst", m))
    t2 = srt(agg(df, "_tgtk", "_tgt", m))

    # Untargeted = search term whose exact text is NOT an entry in Targeting.
    # ASIN targets (asin="b0..") and auto match-types (close-match, loose-match,
    # substitutes, complements) never equal a real shopper query, so this test
    # naturally isolates genuine keyword-harvest candidates. Keep impressions>=1.
    target_keys = set(df["_tgtk"].unique())
    t3 = t1[(~t1["_key"].isin(target_keys)) & (t1["Impressions"] >= 1)].copy()
    t3 = srt(t3)

    rec, baseline_cvr, q1, q3 = build_recommendations(t1, target_keys, lang)

    wb = Workbook()
    ws1 = wb.active; ws1.title = pack["sheet_cst"]
    build_sheet(ws1, t1, pack["label_cst"], pack)
    build_sheet(wb.create_sheet(pack["sheet_tgt"]), t2, pack["label_tgt"], pack)
    build_sheet(wb.create_sheet(pack["sheet_untargeted"]), t3, pack["label_cst"], pack)
    build_recommendation_sheet(wb.create_sheet(pack["sheet_rec"]), rec, pack,
                                baseline_cvr, q1, q3, lang)
    wb.save(out)

    print(f"Wrote {out} (language: {lang})")
    print(f"  Tab 1 {pack['sheet_cst']:<22}: {len(t1)} rows")
    print(f"  Tab 2 {pack['sheet_tgt']:<22}: {len(t2)} rows")
    print(f"  Tab 3 {pack['sheet_untargeted']:<22}: {len(t3)} rows")
    print(f"  Tab 4 {pack['sheet_rec']:<22}: {len(rec)} rows")
    action_counts = rec["_action_key"].value_counts().to_dict()
    print(f"  Actions: {action_counts}")
    print(f"  Source totals -> Spend {df[m['sp']].sum():,.2f} | "
          f"Sales {df[m['sal']].sum():,.2f} | Orders {int(df[m['ord']].sum())}")


if __name__ == "__main__":
    main()
