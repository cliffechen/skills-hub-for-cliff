"""Turn entry_check metrics into a short point-by-point analysis (text first, few numbers).

Every point = what we see (at most ~2 key numbers) + what it means. Wording tiers are listed in
../references/metrics.md ("叙述规则"); thresholds come from entry_check.TH.
"""
from __future__ import annotations


def approx(n) -> str:
    """'约 80' style; small numbers stay exact and get a leading space so templates read '进来 7 个'."""
    if n is None:
        return " ?"
    n = int(round(n))
    if n < 20:
        return f" {n}"
    step = 5 if n < 100 else 10 if n < 1000 else 100
    return f"约 {int(round(n / step) * step):,}"


def approx_plain(n) -> str:
    return approx(n).strip()


def p0(x) -> str:
    return f"{x * 100:.0f}%"


def mon(m: str, ref: str | None = None) -> str:
    """'8 月'; with the year when it differs from the reference month."""
    if ref and m[:4] != ref[:4]:
        return f"{m[:4]} 年 {int(m[5:])} 月"
    return f"{int(m[5:])} 月"


def months_apart(a: str | None, b: str) -> int:
    """Whole months from a to b ('YYYY-MM'); 0 when a is unknown."""
    if not a:
        return 0
    return (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])


TIER_TEXT = {
    "不建议": "落在不建议档（<8%）：转化太低，推起来会很吃广告。",
    "谨慎": "落在谨慎档（8–10%）：转化偏弱，推广成本高，要谨慎。",
    "观望": "落在观望档（10–12%）：转化中等，单靠这个词推不划算，先观望。",
    "潜力": "落在潜力档（12–15%）：转化不错，有推起来的潜力。",
    "重点关注": "落在重点关注档（≥15%）：转化很好，这一项值得重点关注。",
}


def name_of(r) -> str:
    return " / ".join(r["queries"])


# ----------------------------------------------------------------------------- judgement in words
def human_blockers(r, TH) -> list[str]:
    i1, i2, i4, c = r["I1"], r["I2"], r["I4"], r["I5"]
    out = []
    if r["verdict"] == "数据不足":
        return ["在卖的品牌太少，样本撑不起判断" if r["parents_upto_M"] < TH["min_parents"] else "没有需求数据"]
    if c["value"] is not None and c["value"] < TH["cvr_bad"]:
        out.append(f"核心词转化只有约 {p0(c['value'])}，落在不建议档")
    if i1["value"] is not None and i1["value"] < TH["win_bad"]:
        out.append("后来者大多卖不动")
    if (i2["demand_growth"] or 0) and i2["demand_growth"] < TH["min_demand_growth"]:
        out.append("需求本身在缩")
    if i4["value"] > TH["head_max"]:
        out.append(f"后来者里已有{' 至少' if i4.get('lower_bound') and months_apart(r['oldest_month'], r['M']) < 12 else ''} {i4['value']} 个站稳，好位置在被占")
    if c["value"] is not None and TH["cvr_bad"] <= c["value"] < TH["cvr_ok"]:
        out.append(f"核心词转化约 {p0(c['value'])}，只到{c['tier']}档")
    if c["value"] is None:
        out.append("缺核心词转化率，没法确认好不好推")
    if i2["value"] is not None and not i2.get("lower_bound") and i2["value"] < TH["ds_ok"]:
        out.append("供给涨得比需求快")
    if i1["value"] is None and not i1.get("cut") and i1["new"] < TH["min_cohort"]:
        out.append("最近几乎没人进场，没有可以对照的跟随样本")
    if i1["value"] is not None and TH["win_bad"] <= i1["value"] < TH["win_ok"]:
        out.append("后来者只有一部分能卖起来")
    return out


def strengths(r, TH) -> list[str]:
    i1, i2, i4, c = r["I1"], r["I2"], r["I4"], r["I5"]
    out = []
    dg = i2["demand_growth"]
    if dg and dg >= 1.5:
        out.append(f"需求半年涨了 {dg:.1f} 倍")
    if i1["value"] is not None and i1["value"] >= TH["win_ok"]:
        out.append(f"后来者约 {p0(i1['value'])} 卖得动")
    if c["value"] is not None and c["value"] >= TH["cvr_ok"]:
        out.append(f"核心词转化约 {p0(c['value'])}（{c['tier']}档）")
    if i4["value"] == 0 and i1["new"] >= TH["min_cohort"]:
        out.append("还没有后来者站稳")
    return out


# ----------------------------------------------------------------------------- single item
def narrate(r, mode, TH) -> str:
    M, i1, i2, i3, i4, c = r["M"], r["I1"], r["I2"], r["I3"], r["I4"], r["I5"]
    # Truncation only matters when the sample does not reach a year before M; older losses barely move the story.
    capped = r["capped"] and months_apart(r["oldest_month"], M) < 12
    at_least = "至少" if capped else ""
    nm = name_of(r)
    L = []

    # 0. verdict
    if r["verdict"] == "可跟进":
        why = "需求在涨、后来者卖得动、转化也够，现在跟还来得及"
    else:
        b = human_blockers(r, TH)
        if len(b) >= 2:
            why = f"主要卡在两点：一是{b[0]}；二是{b[1]}"
        elif b:
            why = f"主要卡在{b[0]}"
        else:
            why = "几项指标都不算差，但也没有特别亮的"
    if c["tier"] == TH["cvr_top"]:
        why += f"。值得一提的是核心词转化约 {p0(c['value'])}，属于重点关注档"
    L.append(f"**{nm} 现在跟进：{r['verdict']}。** {why}。")
    L.append("")

    # 1. entry curve
    total, n_rec = r["parents_upto_M"], i1["new"]
    post = sum(p["new"] for p in r["post_M"])
    s = f"截至 {mon(M)}，{at_least}{approx_plain(total)} 个品牌在卖，其中最近 3 个月就进来{approx(n_rec)} 个"
    if total and not capped:
        s += f"（约占 {p0(n_rec / total)}）"
    if post:
        s += f"，{mon(r['post_M'][0]['month'])}以后又进来{approx(post)} 个"
    s += "。"
    lab = i3["label"]
    if lab.startswith("加速"):
        s += "入场潮还在加速、没到顶——今天进场按现有人数算排在后面，但最终进场的人会比现在多得多。"
    elif lab == "平稳":
        s += "进场节奏平稳，没有明显的新一波。"
    elif lab == "放缓":
        s += "进场在降温，后面跟的人会越来越少。"
    elif lab == "样本少":
        s += "最近几乎没有新卖家进来，这个成分没有在被追。"
    else:
        s += "因为样本截断，进场是在加速还是降温这次判断不了。"
    L.append(f"- **入场曲线**：{s}")

    # 2. supply vs demand
    dg, sg = i2["demand_growth"], i2["supply_growth"]
    if dg is None:
        s = "需求数据不全，这次没法比供需。"
    else:
        s = f"近 3 个月的搜索量是半年前的 {dg:.1f} 倍，"
        s += f"同期在卖的品牌数是 {sg:.1f} 倍。" if sg else "同期品牌数因样本截断算不出来。"
        v = i2["value"]
        if dg < TH["min_demand_growth"]:
            s += "需求本身在缩，供给再少也不算机会。"
        elif v is None:
            s += "只能看出需求在涨。"
        elif v >= 1:
            s += "需求跑得比供给快，窗口还开着。"
        elif v >= TH["ds_ok"]:
            s += "供给追得比需求快，窗口在收窄，但还没关。"
        else:
            s += "供给远比需求涨得快，窗口基本关了。"
        if i2.get("lower_bound") and capped:
            s += "（样本截断，真实情况只会比这更好。）"
    L.append(f"- **供需对比**：{s}")

    # 3. do newcomers sell
    if i1.get("cut"):
        s = "最近 3 个月的新品没有取全，卖不卖得动这次判断不了。"
    elif i1["value"] is None:
        s = f"最近 3 个月只进来 {n_rec} 个新品，样本太少，看不出后来者能不能卖。"
    else:
        s = f"最近 3 个月进场的{approx(n_rec)} 个新品里，约 {p0(i1['value'])} 月销已经过 {r['min_units']}。"
        if i1["value"] >= TH["win_ok"]:
            s += "后来者还卖得动，需求在往新人那里分。"
        elif i1["value"] >= TH["win_bad"]:
            s += "只有一部分能卖起来，产品和打法得有差异。"
        else:
            s += "大多数新品卖不动，需求没往新人那里流。"
    L.append(f"- **后来者卖得动吗**：{s}")

    # 4. new heads
    k, heads = i4["value"], i4["heads"]
    pre = " 至少" if i4.get("lower_bound") and capped else ""
    if k == 0:
        s = "近一年进场的新品里还没有谁站稳（评分数过 300 的一个都没有）——位置是空的，但也要想想是不是这个成分本身难做大。"
    elif k == 1:
        h = heads[0]
        s = (f"近一年进场的新品里有 1 个已经站稳（{h['brand']}，评分数{approx(h['ratings'])}）——"
             "说明后来者能做起来，坑位还多。")
    else:
        names = "、".join(h["brand"] for h in heads[:2])
        s = (f"近一年进场的新品里已经有{pre} {k} 个站稳了（评分数过 300，比如 {names}）——"
             "后来者做得起来，但好位置在被一个个占掉。")
    L.append(f"- **新头部**：{s}")

    # 5. conversion
    kw = r["demand_kw"]
    if c["value"] is None:
        s = f"「{kw}」的点击转化率 SIF 没有收录，这一项缺失，判定里没算进去。"
        if c.get("ss_purchase_rate"):
            s += f"按卖家精灵的口径，每 100 次搜索大约出 {c['ss_purchase_rate'] * 100:.0f} 单，仅供参考。"
    else:
        cost = c.get("cost_per_order") or (c["cpc"] / c["value"] if c.get("cpc") and c["value"] else None)
        s = f"「{kw}」点进来每 100 个点击大约出 {c['value'] * 100:.0f} 单"
        s += f"，按参考出价算每出一单要花约 ${cost:.0f} 点击费。" if cost else "。"
        s += TIER_TEXT[c["tier"]]
        better = [t for t in c.get("longtails") or []
                  if t.get("cvr") and t["cvr"] >= c["value"] + 0.03 and (t.get("search_week") or 0) >= 200
                  and generic_tail(t["keyword"], kw)]
        if better:
            t = max(better, key=lambda t: t["cvr"])
            s += f"长尾词「{t['keyword']}」转化更高（约 {p0(t['cvr'])}），可以作切入词。"
    L.append(f"- **好不好推**：{s}")

    # plus extras (only what carries information)
    if mode == "plus" and "plus" in r:
        L += plus_points(r)

    # 6. watch-outs (max 2)
    watch = []
    if capped:
        watch.append(f"样本被截断了（只取到 {mon(r['oldest_month'], M)}以后上架的商品），上面带\"至少\"的数是下限；"
                     "想看完整结果，调大页数或收窄类目再跑。")
    elif r["capped"]:
        watch.append(f"商品太多没取完，但样本已经回溯到 {mon(r['oldest_month'], M)}，漏掉的只是更老的商品，不影响上面的判断。")
    jump = demand_jump(r)
    if jump:
        watch.append(f"需求在 {mon(jump[0])}突然跳了约 {jump[1]:.0f} 倍，可能是爆款带动或数据口径变化，增速要打个折看。")
    if r["risk_terms"]:
        watch.append(f"相关商品标题里出现了 {', '.join(r['risk_terms'][:3])} 这类词，上架前注意合规。")
    if r["parents_upto_M"] < TH["min_parents"]:
        watch.append("在卖的品牌太少，以上结论都只能参考。")
    if mode == "plus" and (r.get("plus", {}).get("top3_click_share") or 0) >= 0.75:
        watch.append("核心词的点击大部分集中在前 3 个商品，更像是冲着具体品牌来的搜索。")
    if watch:
        L.append("- **需要留意**：" + "".join(watch[:2]))

    L += ["", "<sub>数据：卖家精灵 + SIF 估算值</sub>"]
    return "\n".join(L)


def plus_points(r) -> list[str]:
    p, out = r["plus"], []
    forms = [f for f in p["forms"] if f["new"] >= 10 and f["form"] != "其他"]
    if len(forms) >= 2:
        best = max(forms, key=lambda f: f["rate"])
        worst = min(forms, key=lambda f: f["rate"])
        if best["rate"] - worst["rate"] >= 0.10:
            out.append(f"- **剂型**：近半年新进场的里，{best['form']}约 {p0(best['rate'])} 能卖起来，"
                       f"明显好于{worst['form']}（约 {p0(worst['rate'])}）——跟的话优先做{best['form']}。")
        else:
            out.append(f"- **剂型**：几种剂型的出单率差不多，剂型不是关键。")
    elif len(forms) == 1 and p["recent_n"]:
        out.append(f"- **剂型**：近半年新进场的基本都是{forms[0]['form']}，没得比。")
    a, b = p["price_recent"]["median"], p["price_older"]["median"]
    if a and b and abs(a / b - 1) >= 0.10:
        d = a / b - 1
        out.append(f"- **价格**：新进场的定价中位约 ${a:.0f}，比老品（约 ${b:.0f}）{'低' if d < 0 else '高'} {abs(d) * 100:.0f}%——"
                   + ("后来者在用价格抢。" if d < 0 else "后来者在往高价走，靠卖点溢价。"))
    if (p.get("cn_hk_share") or 0) >= 0.7:
        out.append(f"- **谁在跟**：新进场的约 {p0(p['cn_hk_share'])} 是中国/香港卖家——主要是国内卖家在冲，打法会很快趋同。")
    if p.get("weekly_shape") == "pulse":
        out.append("- **近期热度**：最近几周的搜索是脉冲式的，近期热度可能有水分。")
    return out[:3]


GENERIC_TAIL = set("""gummies gummy capsules capsule caps softgels softgel liquid drops powder tablets tablet
supplement supplements pills for women men kids adults children organic natural vegan sugar free extra strength
max plus with and high potency pure liposomal chewable spray tea vitamin daily""".split())


def generic_tail(keyword: str, core: str) -> bool:
    """True if the words added to the core keyword are only form/audience/dose words (not a brand)."""
    extra = keyword.lower().replace(core.lower(), " ").split()
    import re as _re
    return bool(extra) and all(w in GENERIC_TAIL or _re.fullmatch(r"\d+(mg|mcg|g|iu|ct|count)?", w) for w in extra)


def demand_jump(r):
    s = [d for d in r["demand_series"] if d["month"] <= r["M"]][-12:]
    for a, b in zip(s, s[1:]):
        if a["searches"] and b["searches"] / a["searches"] >= 3:
            return b["month"], b["searches"] / a["searches"]
    return None


# ----------------------------------------------------------------------------- compare
def narrate_compare(rows, TH) -> str:
    groups = {}
    for r in rows:
        groups.setdefault(r["verdict"], []).append(name_of(r))
    parts = []
    if groups.get("可跟进"):
        parts.append("、".join(groups["可跟进"]) + " 可以跟")
    if groups.get("谨慎"):
        parts.append("、".join(groups["谨慎"]) + " 要谨慎")
    if groups.get("不建议"):
        parts.append("、".join(groups["不建议"]) + " 不建议")
    if groups.get("数据不足"):
        parts.append("、".join(groups["数据不足"]) + " 数据不够")
    L = [f"**按现在的条件：{'；'.join(parts)}。最值得先看的是 {name_of(rows[0])}。**", ""]
    for r in rows:
        good, bad = strengths(r, TH), human_blockers(r, TH)
        s = f"- **{name_of(r)}（{r['verdict']}）**："
        if good:
            s += "亮点是" + "、".join(good[:2]) + "；"
        s += ("卡点是" + "；".join(bad[:2]) + "。") if bad else "没有明显卡点。"
        if r["capped"] and months_apart(r["oldest_month"], r["M"]) < 12:
            s += "（样本截断，部分结论是下限。）"
        L.append(s)
    L += ["", "<sub>数据：卖家精灵 + SIF 估算值 · 排序：判定档位 → 需求是否增长 → 转化 → 后来者出单率 → 供需比</sub>"]
    return "\n".join(L)
