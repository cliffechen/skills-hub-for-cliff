"""Supplement ingredient entry check (lite / plus / compare).

  python entry_check.py lite    --query "urolithin" --demand "urolithin a"
  python entry_check.py plus    --query "goldenseal,golden seal" --demand "goldenseal"
  python entry_check.py compare --items "urolithin|urolithin a; goldenseal,golden seal|goldenseal"

Data: SellerSprite (supply, demand, purchase rate) + SIF (keyword click->purchase CVR), both over MCP HTTP.
Definitions: ../references/metrics.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ss_client import SellerSprite, Sif  # noqa: E402
from trend_filter import classify  # noqa: E402
from render_html import render  # noqa: E402
from narrate import narrate, narrate_compare  # noqa: E402

NODE_HPC = "3760901"
TH = {  # starting thresholds, see metrics.md
    "min_parents": 15, "win_ok": 0.25, "win_bad": 0.15, "ds_ok": 0.5, "ds_bad": 0.3,
    "head_ratings": 300, "head_max": 1, "accel_up": 1.2, "accel_down": 0.8,
    "min_cohort": 5, "min_demand_growth": 1.0,
    "cvr_ok": 0.12, "cvr_bad": 0.08,   # SIF click->purchase CVR of the core keyword
    # CVR tiers (user-defined): <8 不建议, 8-10 谨慎, 10-12 观望, 12-15 潜力, >=15 重点关注
    "cvr_tiers": [(0.08, "不建议"), (0.10, "谨慎"), (0.12, "观望"), (0.15, "潜力")], "cvr_top": "重点关注",
}


def cvr_tier(v):
    if v is None:
        return None
    for upper, label in TH["cvr_tiers"]:
        if v < upper:
            return label
    return TH["cvr_top"]
VERDICT_ORDER = {"可跟进": 0, "谨慎": 1, "不建议": 2, "数据不足": 3}
RISK = re.compile(r"diabet|blood sugar|glp|insulin|prostate|cancer|tumor|cure|letrozole|clomid|"
                  r"metformin|ozempic|semaglutide|tinnitus|hearing|vision loss|weight loss|fat burn", re.I)
FORMS = [("软糖", r"gumm"), ("软胶囊", r"softgel"), ("胶囊", r"capsul|\bcaps\b|veggie cap"),
         ("粉", r"powder"), ("片剂", r"tablet"), ("滴剂", r"drop|tincture"),
         ("液体", r"liquid|shot|drink|syrup"), ("贴片", r"patch")]


# ----------------------------------------------------------------------------- month helpers
def ym(d: dt.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def shift(m: str, k: int) -> str:
    y, mo = int(m[:4]), int(m[5:])
    idx = y * 12 + (mo - 1) + k
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def months_between(a: str, b: str) -> list[str]:
    out, m = [], a
    while m <= b:
        out.append(m)
        m = shift(m, 1)
    return out


def ms_date(ms) -> dt.date | None:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date() if ms else None


def pct(x):
    return "—" if x is None else f"{x:.0%}"


def pct1(x):
    return "—" if x is None else f"{x:.1%}"


def num(x, nd=2):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else f"{x:,}")


# ----------------------------------------------------------------------------- data
def fetch_supply(ss, queries, node, max_pages):
    asins, capped = {}, False
    for q in queries:
        for page in range(1, max_pages + 1):
            d = ss.call("product_research", {"request": {
                "marketplace": "US", "keyword": q, "matchType": 1, "nodeIdPath": node,
                "order": {"field": "available_date", "desc": True}, "size": 40, "page": page,
                "returnFields": "asin,parent,brand,title,availableDate,units,ratings,price,sellerNation"}})["data"]
            batch = d.get("items") or []
            for it in batch:
                asins.setdefault(it["asin"], it)
            if len(batch) < 40:
                break
            if page == max_pages:
                capped = True
    return list(asins.values()), capped


def to_parents(items):
    parents = {}
    for it in items:
        d = ms_date(it.get("availableDate"))
        if not d:
            continue
        p = it.get("parent") or it["asin"]
        cur = parents.get(p)
        if cur is None:
            parents[p] = {"parent": p, "first": d, "units": it.get("units") or 0,
                          "ratings": it.get("ratings") or 0, "brand": it.get("brand") or "",
                          "title": it.get("title") or "", "price": it.get("price"),
                          "seller": it.get("sellerNation") or "", "asins": 1}
            continue
        cur["asins"] += 1
        cur["units"] = max(cur["units"], it.get("units") or 0)
        cur["ratings"] = max(cur["ratings"], it.get("ratings") or 0)
        if d < cur["first"]:
            cur.update(first=d, brand=it.get("brand") or cur["brand"], title=it.get("title") or cur["title"],
                       price=it.get("price") or cur["price"], seller=it.get("sellerNation") or cur["seller"])
    return list(parents.values())


def fetch_demand(ss, kw):
    data = ss.call("aba_research_trend", {"marketplace": "US", "keyword": kw, "timeGranularity": "M",
                                          "returnFields": "label,searches"})["data"] or []
    return {f"{p['label'][:4]}-{p['label'][4:6]}": p.get("searches") or 0 for p in data}


def fetch_conversion(ss, sif, kw):
    """Core-keyword conversion: SIF click->purchase CVR (primary) + SellerSprite search->purchase rate (reference)."""
    out = {"cvr": None, "ctr_week": None, "ctr_90d": None, "conv_share_top3": None, "click_share_top3": None,
           "cpc": None, "cost_per_order": None, "period": None, "entry_signal": None, "longtails": [],
           "ss_purchase_rate": None,
           "ss_month": None, "error": None}
    try:
        d = sif.call("market_screen_keyword_opportunities", {"keyword_root": kw, "topN": 10})
        rows = d.get("keywords") or []
        own = next((x for x in rows if x["keyword"].lower() == kw.lower()), None)
        if own:
            out.update(cvr=own.get("cvr"), ctr_week=own.get("search_ctr_week"), ctr_90d=own.get("search_ctr_90d"),
                       conv_share_top3=own.get("conversion_share_top3"), click_share_top3=own.get("click_share_top3"),
                       cpc=own.get("cpc"), cost_per_order=own.get("traffic_cost_per_unit") or None,
                       period=own.get("data_period"), entry_signal=own.get("entry_signal"))
        out["longtails"] = [{"keyword": x["keyword"], "search_week": x.get("search_volume"), "cvr": x.get("cvr"),
                             "cpc": x.get("cpc"), "click_share_top3": x.get("click_share_top3")}
                            for x in rows if x["keyword"].lower() != kw.lower()][:5]
    except Exception as e:  # SIF down / quota -> keep running, I5 shows as missing
        out["error"] = str(e)[:120]
    items = ss.call("keyword_miner", {"request": {"marketplace": "US", "keywordList": [kw],
                                                  "returnFields": "keyword,purchaseRate,month"}})["data"].get("items") or []
    if items:
        out["ss_purchase_rate"], out["ss_month"] = items[0].get("purchaseRate"), items[0].get("month")
    return out


# ----------------------------------------------------------------------------- metrics
def analyse(ss, sif, queries, demand_kw, node, min_units, max_pages, today):
    items, capped = fetch_supply(ss, queries, node, max_pages)
    parents = to_parents(items)
    demand = fetch_demand(ss, demand_kw)
    nonzero = [m for m, v in sorted(demand.items()) if v > 0]
    M = nonzero[-1] if nonzero else shift(ym(today), -1)

    by_month = {}
    for p in parents:
        e = by_month.setdefault(ym(p["first"]), {"new": 0, "win": 0})
        e["new"] += 1
        e["win"] += p["units"] >= min_units
    upto_M = [p for p in parents if ym(p["first"]) <= M]
    after_M = [p for p in parents if ym(p["first"]) > M]

    def cum(m):
        return sum(1 for p in parents if ym(p["first"]) <= m)

    def window(a, b):
        ms = months_between(a, b)
        return sum(by_month.get(m, {}).get("new", 0) for m in ms), sum(by_month.get(m, {}).get("win", 0) for m in ms)

    total_M = len(upto_M)
    first_tab = shift(M, -11)
    table = []
    earlier_new = sum(1 for p in upto_M if ym(p["first"]) < first_tab)
    earlier_win = sum(1 for p in upto_M if ym(p["first"]) < first_tab and p["units"] >= min_units)
    table.append({"month": f"< {first_tab}", "new": earlier_new, "win": earlier_win,
                  "cum_pct": earlier_new / total_M if total_M else None, "demand": None})
    for m in months_between(first_tab, M):
        e = by_month.get(m, {"new": 0, "win": 0})
        table.append({"month": m, "new": e["new"], "win": e["win"],
                      "cum_pct": cum(m) / total_M if total_M else None, "demand": demand.get(m)})
    post = [{"month": m, "new": by_month[m]["new"], "win": by_month[m]["win"]}
            for m in sorted(by_month) if m > M]

    # I1 recent cohort win rate (M-2..M)
    oldest = ym(min(p["first"] for p in parents)) if parents else None
    n_rec, w_rec = window(shift(M, -2), M)
    i1 = w_rec / n_rec if n_rec >= TH["min_cohort"] else None   # too few entrants -> not a rate
    i1_cut = bool(capped and (oldest is None or oldest > shift(M, -2)))  # cohort not fully covered
    if i1_cut:
        i1 = None
    # I2 demand growth / supply growth over the same 6 months
    d_now = [demand.get(m) for m in months_between(shift(M, -2), M)]
    d_then = [demand.get(m) for m in months_between(shift(M, -8), shift(M, -6))]
    d_growth = (statistics.mean(d_now) / statistics.mean(d_then)
                if all(v is not None for v in d_now + d_then) and statistics.mean(d_then) > 0 else None)
    # Truncation drops the OLDEST listings, so both cumulative counts miss the same k parents:
    # observed supply growth >= true growth, i.e. observed I2 is a LOWER bound - but only if the
    # sample reaches back before M-6; otherwise the "6 months ago" stock is unknown.
    i2_note = None
    s_growth = cum(M) / cum(shift(M, -6)) if cum(shift(M, -6)) else None
    if capped and (oldest is None or oldest >= shift(M, -6)):
        s_growth, i2_note = None, "样本截断，覆盖不到 6 个月前，无法计算"
    elif capped:
        i2_note = "样本截断，此值为下限"
    i2 = d_growth / s_growth if d_growth and s_growth else None
    # I3 entry acceleration
    n_prev, _ = window(shift(M, -5), shift(M, -3))
    i3 = n_rec / n_prev if n_prev else None
    if capped and (oldest is None or oldest >= shift(M, -5)):
        i3, i3_label = None, "截断无法计算"
    elif n_rec + n_prev < 2 * TH["min_cohort"] - 4:      # fewer than 6 entrants across both windows
        i3_label = "样本少"
    elif i3 is None:
        i3_label = "加速（再前 3 月为 0）"
    else:
        i3_label = "加速" if i3 > TH["accel_up"] else "放缓" if i3 < TH["accel_down"] else "平稳"
    # I4 new heads: entered within 12 months of today, ratings >= 300
    heads = sorted([p for p in parents if (today - p["first"]).days <= 365 and p["ratings"] >= TH["head_ratings"]],
                   key=lambda p: -p["ratings"])
    i4 = len(heads)
    i4_lower = bool(capped and (oldest is None or oldest > ym(today - dt.timedelta(days=365))))

    conv = fetch_conversion(ss, sif, demand_kw)
    cvr = conv["cvr"]

    # verdict
    reasons = []
    if total_M < TH["min_parents"] or not nonzero:
        verdict = "数据不足"
        reasons.append(f"截至 {M} 只有 {total_M} 个父体" if nonzero else "没有需求数据")
    elif ((i1 is not None and i1 < TH["win_bad"]) or (i2 is not None and not capped and i2 < TH["ds_bad"])
          or (cvr is not None and cvr < TH["cvr_bad"])):
        verdict = "不建议"
        if cvr is not None and cvr < TH["cvr_bad"]:
            reasons.append(f"核心词 CVR {pct1(cvr)}（{cvr_tier(cvr)}档）")
        if i1 is not None and i1 < TH["win_bad"]:
            reasons.append(f"近期出单率 {pct(i1)} < {pct(TH['win_bad'])}")
        if i2 is not None and not capped and i2 < TH["ds_bad"]:
            reasons.append(f"供需增速比 {num(i2)} < {TH['ds_bad']}")
    elif ((i1 is not None and i1 >= TH["win_ok"]) and (i2 is not None and i2 >= TH["ds_ok"])
          and i4 <= TH["head_max"] and (d_growth or 0) >= TH["min_demand_growth"]
          and cvr is not None and cvr >= TH["cvr_ok"]):
        verdict = "可跟进"
        reasons.append(f"需求 ×{num(d_growth)}、近期出单率 {pct(i1)}、供需增速比 {num(i2)}、新头部 {i4} 个、"
                       f"核心词 CVR {pct1(cvr)}（{cvr_tier(cvr)}档）都在线内")
    else:
        verdict = "谨慎"
        if i1_cut:
            reasons.append("近 3 月批次未完整覆盖，出单率无法计算")
        elif n_rec < TH["min_cohort"]:
            reasons.append(f"近 3 月只进场 {n_rec} 个父体，没有可参考的跟进样本")
        elif i1 < TH["win_ok"]:
            reasons.append(f"近期出单率 {pct(i1)} 未到 {pct(TH['win_ok'])}")
        if d_growth is not None and d_growth < TH["min_demand_growth"]:
            reasons.append(f"需求在缩（×{num(d_growth)}）")
        if cvr is None:
            reasons.append("核心词 CVR 无数据")
        elif cvr < TH["cvr_ok"]:
            reasons.append(f"核心词 CVR {pct1(cvr)}，只到{cvr_tier(cvr)}档")
        if (i2 is None and not capped) or (i2 is not None and i2 < TH["ds_ok"]):
            reasons.append(f"供需增速比 {num(i2)} 未到 {TH['ds_ok']}")
        if i4 > TH["head_max"]:
            reasons.append(f"已有 {i4} 个新头部（评分数 ≥{TH['head_ratings']}）")

    if capped:
        reasons.append("样本已截断（调大 --max-pages 或收窄 --node 再跑）")

    risk_hits = sorted({m.group(0).lower() for t in [demand_kw, *queries, *(p["title"] for p in parents)]
                        for m in RISK.finditer(t)})
    return {
        "queries": queries, "demand_kw": demand_kw, "node": node, "today": str(today), "M": M,
        "asins": len(items), "parents": len(parents), "parents_upto_M": total_M, "capped": capped,
        "oldest_month": oldest,
        "min_units": min_units, "table": table, "post_M": post,
        "demand_series": [{"month": m, "searches": demand[m]} for m in sorted(demand)],
        "I1": {"value": i1, "cut": i1_cut, "new": n_rec, "win": w_rec,
               "by_month": [{"month": m, **by_month.get(m, {"new": 0, "win": 0})}
                            for m in months_between(shift(M, -2), M)]},
        "I2": {"value": i2, "note": i2_note, "lower_bound": bool(capped and i2 is not None),
               "demand_growth": d_growth, "supply_growth": s_growth,
               "demand_now": d_now, "demand_then": d_then,
               "cum_now": cum(M), "cum_then": cum(shift(M, -6))},
        "I3": {"value": i3, "label": i3_label, "recent3": n_rec, "prev3": n_prev},
        "I4": {"value": i4, "lower_bound": i4_lower, "heads": [{"brand": h["brand"], "ratings": h["ratings"], "first": str(h["first"]),
                                       "units": h["units"]} for h in heads[:5]]},
        "I5": {"value": cvr, "tier": cvr_tier(cvr), **conv},
        "verdict": verdict, "reasons": reasons, "risk_terms": risk_hits[:8],
        "_parents": parents,
    }


def plus_extras(ss, r):
    M, parents = r["M"], r["_parents"]
    lo = shift(M, -5)
    recent = [p for p in parents if lo <= ym(p["first"]) <= M]
    older = [p for p in parents if ym(p["first"]) < lo]

    forms = {}
    for p in recent:
        t = p["title"].lower()
        f = next((name for name, rx in FORMS if re.search(rx, t)), "其他")
        e = forms.setdefault(f, {"new": 0, "win": 0})
        e["new"] += 1
        e["win"] += p["units"] >= r["min_units"]
    forms = [{"form": k, **v, "rate": v["win"] / v["new"]} for k, v in sorted(forms.items(), key=lambda kv: -kv[1]["new"])]

    def band(ps):
        xs = sorted(p["price"] for p in ps if p.get("price"))
        if len(xs) < 4:
            return {"n": len(xs), "median": statistics.median(xs) if xs else None, "p25": None, "p75": None}
        q = statistics.quantiles(xs, n=4)
        return {"n": len(xs), "median": statistics.median(xs), "p25": q[0], "p75": q[2]}

    cn = sum(1 for p in recent if p["seller"] in ("CN", "HK"))
    weekly = ss.call("aba_research_trend", {"marketplace": "US", "keyword": r["demand_kw"], "timeGranularity": "W",
                                            "returnFields": "label,searches"})["data"] or []
    series = [p.get("searches") or 0 for p in weekly]
    while series and series[0] == 0:
        series.pop(0)
    shape = classify(series[-16:]) if series else {"label": "—"}
    aba = ss.call("aba_research_weekly", {"request": {"marketplace": "US", "includeKeywords": r["demand_kw"],
                                                      "size": 10, "page": 1,
                                                      "returnFields": "keyword,top3Brands,clickShareRate,searchRank,searches"}})["data"].get("items") or []
    own = next((it for it in aba if it["keyword"].lower() == r["demand_kw"].lower()), None)
    r["plus"] = {
        "window": f"{lo}..{M}", "recent_n": len(recent), "forms": forms,
        "price_recent": band(recent), "price_older": band(older),
        "cn_hk_share": cn / len(recent) if recent else None,
        "weekly_shape": shape.get("label"), "weekly_last": series[-4:],
        "top3_brands": [b for b in (own or {}).get("top3Brands") or [] if b], "top3_click_share": (own or {}).get("clickShareRate"),
        "weekly_rank": (own or {}).get("searchRank"), "weekly_searches": (own or {}).get("searches"),
    }


# ----------------------------------------------------------------------------- data tables (appendix / --tables)
def tables(r, mode):
    q = " / ".join(r["queries"])
    L = [f"### 入场速判 · {q}",
         f"需求词 `{r['demand_kw']}` · 截止月 **{r['M']}** · 样本 {r['asins']} 个 ASIN / {r['parents']} 个父体"
         f"{'（⚠️ 样本已截断，最早只到 ' + str(r['oldest_month']) + '；累计占比* 偏高）' if r['capped'] else ''}"
         f" · 出单线 月销 ≥{r['min_units']}",
         "", f"**判定：{r['verdict']}** —— " + "；".join(r["reasons"]), "",
         "| 月份 | 新父体 | 其中出单 | 累计占比 | 月搜索 |", "|---|---|---|---|---|"]
    for t in r["table"]:
        L.append(f"| {t['month']} | {t['new']} | {t['win']} | {pct(t['cum_pct']) + ('*' if r['capped'] else '')} | {num(t['demand']) if t['demand'] is not None else ''} |")
    if r["post_M"]:
        L += ["", "截止月之后（需求数据还没出，不进指标）：" + "，".join(
            f"{p['month']} 新父体 {p['new']}、出单 {p['win']}" for p in r["post_M"])]
    i1, i2, i3, i4 = r["I1"], r["I2"], r["I3"], r["I4"]
    L += ["", "| 指标 | 值 | 怎么来的 |", "|---|---|---|",
          f"| I1 近期批次出单率 | **{pct(i1['value']) if i1['value'] is not None else ('截断无法计算' if i1.get('cut') else '样本少')}** | {r['M']} 及前 2 个月进场 {i1['new']} 个父体，{i1['win']} 个月销 ≥{r['min_units']}"
          f"（逐月 " + "、".join(f"{b['month'][5:]}月 {b['win']}/{b['new']}" for b in i1["by_month"]) + "） |",
          f"| I2 需求增速 ÷ 供给增速 | **{i2_str(i2)}** | {(i2['note'] + '；') if i2['note'] else ''}需求 ×{num(i2['demand_growth'])}（近 3 月均值 vs 6 个月前 3 月均值）÷ "
          f"供给 ×{num(i2['supply_growth'])}（累计父体 {i2['cum_then']}→{i2['cum_now']}） |",
          f"| I3 入场加速度 | **{i3['label']}**（×{num(i3['value'])}） | 近 3 月新父体 {i3['recent3']} vs 再前 3 月 {i3['prev3']} |",
          f"| I4 新头部 | **{'≥' if i4.get('lower_bound') else ''}{i4['value']}** 个 | 近 12 个月进场、评分数 ≥{TH['head_ratings']}"
          + ("：" + "、".join(f"{h['brand']}({h['ratings']})" for h in i4["heads"][:3]) if i4["heads"] else "") + " |",
          i5_row(r)]
    if r["I5"]["longtails"]:
        L += ["", f"核心词下的长尾词（SIF，{r['I5']['period']} 周）：" + "；".join(
            f"`{t['keyword']}` CVR {pct1(t['cvr'])} · 周搜索 {num(t['search_week'])} · CPC ${t['cpc']}"
            for t in r["I5"]["longtails"])]
    if mode in ("plus",) and "plus" in r:
        p = r["plus"]
        L += ["", f"**plus · 近 6 个月进场者（{p['window']}，{p['recent_n']} 个父体）**", "",
              "| 剂型 | 进场 | 出单 | 出单率 |", "|---|---|---|---|"]
        L += [f"| {f['form']} | {f['new']} | {f['win']} | {pct(f['rate'])} |" for f in p["forms"]]
        pr, po = p["price_recent"], p["price_older"]
        L += ["", f"- 价格带：近期进场 中位 {num(pr['median'])}（P25–P75 {num(pr['p25'])}–{num(pr['p75'])}，n={pr['n']}）"
              f" vs 老品 中位 {num(po['median'])}（{num(po['p25'])}–{num(po['p75'])}，n={po['n']}）",
              f"- 近期进场者中国/香港卖家占比：{pct(p['cn_hk_share'])}",
              f"- 需求词周度形态：**{p['weekly_shape']}**（最近 4 周搜索 {', '.join(f'{x:,}' for x in p['weekly_last'])}）",
              f"- 需求词前三品牌：{', '.join(p['top3_brands']) or '—'}；前三点击集中度 {pct(p['top3_click_share'])}"
              + ("（≥75%，偏品牌/导航型需求）" if (p['top3_click_share'] or 0) >= 0.75 else "")]
    if r["risk_terms"]:
        L += ["", f"⚠️ 合规提示词（只提示、不进判定）：{', '.join(r['risk_terms'])}"]
    L += ["", "<sub>数据源：卖家精灵 product_research（上架时间、月销、评分数）+ aba_research_trend（月搜索）+ keyword_miner（搜索→购买率）；"
          "SIF market_screen_keyword_opportunities（核心词 CVR、点击率、CPC）。均为估算值。"
          "样本只含标题匹配查询词、且在所选类目节点下的商品；月销是当前值，不是进场当月的值。</sub>"]
    return "\n".join(L)


def i2_str(i2):
    if i2["value"] is None:
        return "—"
    return ("≥" if i2.get("lower_bound") else "") + num(i2["value"])


def i5_row(r):
    c = r["I5"]
    if c["value"] is None:
        why = f"SIF 无数据（{c['error']}）" if c["error"] else "SIF 未收录该词"
        return f"| I5 核心词 CVR | **—** | {why}；卖家精灵 搜索→购买率 {pct1(c['ss_purchase_rate'])}（{c['ss_month']}） |"
    return (f"| I5 核心词 CVR | **{pct1(c['value'])}（{c['tier']}）** | SIF 点击→购买转化（{c['period']} 周）；点击率 {pct(c['ctr_week'])}"
            f"（90 天 {pct(c['ctr_90d'])}）、Top3 转化集中度 {pct(c['conv_share_top3'])}、参考 CPC ${c['cpc']}；"
            f"对照：卖家精灵 搜索→购买率 {pct1(c['ss_purchase_rate'])}（{c['ss_month']}） |")


def compare_tables(rows):
    rows = sorted(rows, key=lambda r: (VERDICT_ORDER[r["verdict"]],
                                       -((r["I2"]["demand_growth"] or 0) >= TH["min_demand_growth"]),
                                       -(r["I5"]["value"] or 0),
                                       -(r["I1"]["value"] if r["I1"]["value"] is not None else -1),
                                       -(r["I2"]["value"] or 0)))
    L = ["### 入场速判 · 对比", "", "| | " + " | ".join(" / ".join(r["queries"]) for r in rows) + " |",
         "|---|" + "---|" * len(rows)]

    def row(name, f):
        L.append(f"| {name} | " + " | ".join(f(r) for r in rows) + " |")
    row("判定", lambda r: f"**{r['verdict']}**")
    row("截止月", lambda r: r["M"])
    row("父体（截至 M）", lambda r: f"{r['parents_upto_M']}{' ⚠️截断' if r['capped'] else ''}")
    row("I1 近期出单率", lambda r: f"{pct(r['I1']['value'])}（{r['I1']['win']}/{r['I1']['new']}）")
    row("I2 供需增速比", lambda r: i2_str(r["I2"]))
    row("　需求 ×", lambda r: num(r["I2"]["demand_growth"]))
    row("　供给 ×", lambda r: num(r["I2"]["supply_growth"]))
    row("I3 入场", lambda r: f"{r['I3']['label']}（{r['I3']['recent3']} vs {r['I3']['prev3']}）")
    row("I4 新头部", lambda r: ("≥" if r["I4"].get("lower_bound") else "") + str(r["I4"]["value"]))
    row("I5 核心词 CVR", lambda r: pct1(r["I5"]["value"]) + (f"（{r['I5']['tier']}）" if r["I5"]["tier"] else ""))
    row("　参考 CPC", lambda r: f"${r['I5']['cpc']}" if r["I5"]["cpc"] is not None else "—")
    row("合规提示", lambda r: ", ".join(r["risk_terms"][:3]) or "—")
    L += ["", "理由：", *[f"- **{' / '.join(r['queries'])}**：{'；'.join(r['reasons'])}" for r in rows],
          "", "<sub>数据源：卖家精灵 + SIF（估算值）。排序：判定档位 → 需求是否增长 → I5 → I1 → I2。</sub>"]
    return "\n".join(L), rows


# ----------------------------------------------------------------------------- main
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["lite", "plus", "compare"])
    ap.add_argument("--query", help="title match terms, comma separated (union)")
    ap.add_argument("--demand", help="ABA demand keyword")
    ap.add_argument("--items", help="compare: 'q1,q2|demand[|node]; q3|demand; ...' (2-5 items)")
    ap.add_argument("--node", default=NODE_HPC)
    ap.add_argument("--min-units", type=int, default=100)
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--today", default=str(dt.date.today()))
    ap.add_argument("--out", default="entry-check")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--tables", action="store_true", help="also print the raw data tables")
    ap.add_argument("--html", action="store_true", help="also write report.html (charts + data appendix); off by default")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today)
    ss = SellerSprite(use_cache=not a.no_cache)
    sif = Sif(min_interval=1.0, use_cache=not a.no_cache)

    if a.mode == "compare":
        specs = [s.strip() for s in (a.items or "").split(";") if s.strip()]
        if not 2 <= len(specs) <= 5:
            ap.error("--items needs 2-5 entries")
        results = []
        for s in specs:
            parts = [x.strip() for x in s.split("|")]
            qs = [x.strip() for x in parts[0].split(",") if x.strip()]
            d = parts[1] if len(parts) > 1 and parts[1] else qs[0]
            node = parts[2] if len(parts) > 2 and parts[2] else a.node
            print(f"  ... {qs} | {d} | {node}", flush=True)
            results.append(analyse(ss, sif, qs, d, node, a.min_units, a.max_pages, today))
        tab, ordered = compare_tables(results)
        text = narrate_compare(ordered, TH)
        name = "compare_" + "_".join(slug(r["queries"][0]) for r in ordered)[:60]
        payload = {"mode": "compare", "items": ordered}
    else:
        if not a.query:
            ap.error("--query is required")
        qs = [x.strip() for x in a.query.split(",") if x.strip()]
        r = analyse(ss, sif, qs, a.demand or qs[0], a.node, a.min_units, a.max_pages, today)
        if a.mode == "plus":
            plus_extras(ss, r)
        tab = tables(r, a.mode)
        text = narrate(r, a.mode, TH)
        name = f"{a.mode}_{slug(qs[0])}"
        payload = {"mode": a.mode, "items": [r]}

    out_dir = Path(a.out) / f"{name}_{a.today}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in payload["items"]:
        r.pop("_parents", None)
    (out_dir / "card.md").write_text(text, encoding="utf-8")
    (out_dir / "data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (out_dir / "tables.md").write_text(tab, encoding="utf-8")
    if a.html:
        (out_dir / "report.html").write_text(render(payload, text, tab), encoding="utf-8")
    print(text)
    if a.tables:
        print("\n---\n" + tab)
    extras = "已生成 report.html" if a.html else "需要带图的报告可加 --html；需要明细表可加 --tables"
    print(f"\n<sub>文件：{out_dir.resolve()} · {extras} · API 调用 卖家精灵 {ss.calls} 次 + SIF {sif.calls} 次，"
          f"缓存命中 {ss.cache_hits + sif.cache_hits} 次</sub>")


if __name__ == "__main__":
    main()
