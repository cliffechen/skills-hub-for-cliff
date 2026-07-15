#!/usr/bin/env python3
"""Render the research data contract as a self-contained, dependency-free HTML report."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def evidence(section: dict, key: str) -> dict:
    value = section.get(key, {})
    return value if isinstance(value, dict) else {"value": value}


def evidence_value(section: dict, key: str, default: Any = None) -> Any:
    item = evidence(section, key)
    return item.get("value", default)


def number(value: Any, digits: int = 0) -> str:
    if value is None or value == "":
        return "未获取"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if digits:
        return f"{numeric:,.{digits}f}"
    return f"{numeric:,.0f}"


def percent(value: Any) -> str:
    if value is None or value == "":
        return "未获取"
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return str(value)


def gate_card(label: str, gate: dict) -> str:
    status = str(gate.get("value") or "VERIFY")
    tone = {"GO": "good", "NO-GO": "bad"}.get(status, "warn")
    notes = gate.get("notes") or gate.get("definition") or "证据不足，需继续验证。"
    return (
        f'<article class="gate"><div class="gate-head"><span>{esc(label)}</span>'
        f'<b class="tag {tone}">{esc(status)}</b></div><p>{esc(notes)}</p></article>'
    )


def line_chart(points: list[dict], x_key: str, y_key: str, title: str) -> str:
    clean: list[tuple[str, float]] = []
    for item in points:
        try:
            clean.append((str(item.get(x_key, "")), float(item.get(y_key))))
        except (TypeError, ValueError):
            continue
    if len(clean) < 2:
        return '<div class="empty">趋势数据不足</div>'
    width, height, pad = 760, 260, 36
    values = [item[1] for item in clean]
    low, high = min(values), max(values)
    span = high - low or 1
    coords = []
    for index, (_, value) in enumerate(clean):
        x = pad + index * (width - pad * 2) / (len(clean) - 1)
        y = height - pad - (value - low) * (height - pad * 2) / span
        coords.append(f"{x:.1f},{y:.1f}")
    first_label, last_label = clean[0][0], clean[-1][0]
    return f"""
    <figure class="chart">
      <figcaption>{esc(title)}</figcaption>
      <svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
        <line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" class="axis"/>
        <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" class="axis"/>
        <polyline points="{' '.join(coords)}" class="trend-line"/>
        <text x="{pad}" y="{height-10}" class="axis-label">{esc(first_label)}</text>
        <text x="{width-pad}" y="{height-10}" text-anchor="end" class="axis-label">{esc(last_label)}</text>
        <text x="{pad}" y="{pad-8}" class="axis-label">{number(high)}</text>
        <text x="{pad}" y="{height-pad-8}" class="axis-label">{number(low)}</text>
      </svg>
    </figure>"""


def bar_rows(items: Iterable[tuple[str, float, str]]) -> str:
    rows = list(items)
    maximum = max((value for _, value, _ in rows), default=1) or 1
    output = []
    for label, value, note in rows:
        width = max(2, value / maximum * 100)
        output.append(
            '<div class="bar-row">'
            f'<div class="bar-label">{esc(label)}</div>'
            f'<div class="bar-track"><span style="width:{width:.2f}%"></span></div>'
            f'<div class="bar-value">{number(value)}{esc(note)}</div>'
            "</div>"
        )
    return "".join(output) or '<div class="empty">数据不足</div>'


def product_table(products: list[dict]) -> str:
    rows = []
    for item in products[:20]:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('asin'))}</td>"
            f"<td>{esc(item.get('brand') or item.get('品牌'))}</td>"
            f"<td class=\"num\">{number(item.get('price') or item.get('价格'), 2)}</td>"
            f"<td class=\"num\">{number(item.get('monthly_units') or item.get('月销量'))}</td>"
            f"<td class=\"num\">{number(item.get('reviews') or item.get('评论数'))}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="5">未获取严格相关竞品明细</td></tr>')
    return "".join(rows)


def source_table(sources: list[dict]) -> str:
    rows = []
    for item in sources:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('name') or item.get('source'))}</td>"
            f"<td>{esc(item.get('status'))}</td>"
            f"<td>{esc(item.get('retrieved_at'))}</td>"
            f"<td>{esc(item.get('notes') or item.get('scope'))}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="4">未记录数据源状态</td></tr>'


def source_usage_call_table(items: list[dict]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('source'))}</td>"
            f"<td>{esc(item.get('tool'))}</td>"
            f"<td class=\"num\">{number(item.get('call_count'))}</td>"
            f"<td>{esc(item.get('status') or '未记录')}</td>"
            f"<td>{esc(item.get('notes') or '')}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="5">未记录工具调用统计</td></tr>'


def source_usage_output_table(items: list[dict]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('source'))}</td>"
            f"<td>{esc(item.get('metric'))}</td>"
            f"<td class=\"num\">{number(item.get('count'))}</td>"
            f"<td>{esc(item.get('unit'))}</td>"
            f"<td>{esc(item.get('notes') or '')}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="5">未记录返回数据规模</td></tr>'


def source_usage_kpis(usage: dict) -> str:
    cards = [
        ("数据源调用总数", usage.get("total_calls"), "次"),
        ("数据源数量", usage.get("source_count"), "个"),
    ]
    for item in (usage.get("headline_metrics") or [])[:2]:
        if isinstance(item, dict):
            cards.append((item.get("label"), item.get("value"), item.get("unit") or ""))
    return "".join(
        '<article class="kpi"><span>'
        f'{esc(label)}</span><b>{number(value)}</b><small>{esc(unit)}</small></article>'
        for label, value, unit in cards
    )


def keyword_drift_table(terms: list[dict]) -> str:
    labels = {
        "generic_core": "泛词核心",
        "generic_synonym_source": "同义/来源词",
        "benefit_formulation": "功效/配方词",
        "brand_root": "品牌根词",
        "brand_product": "品牌产品词",
        "brand_variant": "品牌拼写变体",
        "noise": "噪声",
    }
    rows = []
    for item in terms:
        overlap = item.get("seed_result_overlap_coefficient_pct")
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('keyword'))}</td>"
            f"<td>{esc(labels.get(item.get('classification'), item.get('classification')))}</td>"
            f"<td class=\"num\">{number(item.get('current_monthly_search_volume'))}</td>"
            f"<td class=\"num\">{percent(item.get('year_over_year_change_pct'))}</td>"
            f"<td class=\"num\">{percent(item.get('latest_6m_vs_prior_6m_pct'))}</td>"
            f"<td class=\"num\">{percent(overlap) if overlap is not None else '—'}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="6">本次运行未获得关键词漂移证据</td></tr>'


def keyword_selection_table(terms: list[dict]) -> str:
    rows = []
    for item in terms:
        scoring = item.get("scoring") or {}
        coverage = scoring.get("market_coverage") or {}
        failures = scoring.get("eligibility_failures") or []
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('keyword'))}</td>"
            f"<td>{esc(item.get('classification'))}</td>"
            f"<td class=\"num\">{number(item.get('current_monthly_search_volume'))}</td>"
            f"<td class=\"num\">{number(scoring.get('strict_relevance_rate'), 4)}</td>"
            f"<td class=\"num\">{number(scoring.get('purchase_intent_weight'), 2)}</td>"
            f"<td class=\"num\">{number(coverage.get('final'), 4)}</td>"
            f"<td class=\"num\">{number(scoring.get('sales_multiplier'), 4)}</td>"
            f"<td class=\"num\">{number(scoring.get('primary_keyword_score'), 2)}</td>"
            f"<td>{'入围' if scoring.get('eligible') else esc('；'.join(failures) or '证据不足')}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="9">未获得完整候选词评分证据</td></tr>'


def audit_text(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    parts = []
    for key in ("field", "evidence", "impact", "resolution", "reason", "notes"):
        value = item.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}: {value}")
    return "；".join(parts) if parts else json.dumps(item, ensure_ascii=False)


def render(data: dict, title: str | None = None) -> str:
    run = data.get("run", {})
    market = data.get("market_capacity", {})
    competition = data.get("competition", {})
    differentiation = data.get("differentiation", {})
    decision = data.get("decision", {})
    keyword = run.get("keyword") or "Amazon Product Opportunity"
    primary_selection = evidence_value(market, "primary_keyword_selection", {}) or {}
    primary_keyword = (
        run.get("primary_research_keyword")
        or primary_selection.get("primary_research_keyword")
        or keyword
    )
    handoff = bool(run.get("keyword_handoff") or primary_selection.get("keyword_handoff"))
    report_title = title or (
        f"{keyword} → {primary_keyword} 选品验证报告" if handoff else f"{primary_keyword} 选品验证报告"
    )

    keyword_detail = evidence_value(market, "amazon_keyword_detail", {}) or {}
    keyword_trend = evidence_value(market, "amazon_keyword_trend_12m", {}) or {}
    category_trend = evidence_value(market, "category_trend", {}) or {}
    web_trends = evidence_value(market, "google_trends_web_5y", {}) or {}
    keyword_drift = evidence_value(market, "keyword_drift_analysis", {}) or {}
    drift_terms = keyword_drift.get("terms", []) if isinstance(keyword_drift, dict) else []
    top10_units = evidence_value(market, "top10_monthly_units", []) or []
    review_sample = evidence_value(differentiation, "negative_review_sample_size", {}) or {}
    products = evidence_value(competition, "strict_algae_subset", None)
    if not isinstance(products, list):
        products = evidence_value(competition, "top20_products", []) or []
    complaints = evidence_value(differentiation, "complaint_clusters", []) or []
    improvements = evidence_value(differentiation, "product_improvements", []) or []
    offsite_raw = data.get("offsite_validation", []) or []
    offsite = offsite_raw.get("findings", []) if isinstance(offsite_raw, dict) else offsite_raw
    source_usage = data.get("source_usage", {}) or {}
    source_usage_notes = "".join(
        f"<li>{esc(item)}</li>" for item in (source_usage.get("notes") or [])
    ) or "<li>未记录额外统计口径说明。</li>"

    complaint_bars = []
    for item in complaints:
        complaint_bars.append(
            (
                str(item.get("cluster") or item.get("pain_point") or "未命名痛点"),
                float(item.get("explicit_review_occurrences") or item.get("frequency") or 0),
                " 次",
            )
        )

    improvement_cards = []
    for item in improvements:
        improvement_cards.append(
            '<article class="action"><h3>'
            f"{esc(item.get('pain_point') or item.get('title'))}</h3>"
            f"<p>{esc(item.get('hypothesis') or item.get('solution'))}</p></article>"
        )
    if not improvement_cards:
        improvement_cards.append('<div class="empty">尚未形成可执行改进方案</div>')

    offsite_rows = []
    for item in offsite:
        if not isinstance(item, dict):
            continue
        offsite_rows.append(
            "<tr>"
            f"<td>{esc(item.get('source') or item.get('title') or item.get('source_title'))}</td>"
            f"<td>{esc(item.get('finding') or item.get('assessment') or item.get('claim'))}</td>"
            f"<td>{esc(item.get('confidence') or item.get('authority') or '需结合来源判断')}</td>"
            "</tr>"
        )
    if not offsite_rows:
        offsite_rows.append('<tr><td colspan="3">暂无站外交叉验证记录</td></tr>')

    missing = data.get("missing_fields", []) or []
    conflicts = data.get("conflicts", []) or []
    audit_items = "".join(f"<li>{esc(audit_text(item))}</li>" for item in missing + conflicts)
    if not audit_items:
        audit_items = "<li>未记录会改变结论的缺失或冲突。</li>"

    result = str(decision.get("result") or "VERIFY")
    confidence = str(decision.get("confidence") or "low")
    summary = decision.get("summary") or "现有证据不足以形成稳定结论。"
    generated = datetime.now().astimezone().isoformat(timespec="seconds")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(report_title)}</title>
<style>
:root{{--navy:#0f172a;--ink:#172033;--muted:#667085;--blue:#6378e5;--slate:#26384a;--purple:#7446a5;--cyan:#16bde5;--lav:#eef0ff;--green:#e4f5e6;--yellow:#fff7e7;--red:#feecec;--line:#e6e9f0}}
*{{box-sizing:border-box}}html,body{{margin:0;max-width:100%;overflow-x:hidden}}body{{background:var(--navy);color:var(--ink);font:14px/1.55 "Segoe UI","Microsoft YaHei",sans-serif}}main{{width:min(1080px,100%);margin:0 auto;padding:18px}}.card{{background:#fff;border-radius:18px;padding:24px;margin-bottom:16px;box-shadow:0 8px 24px rgba(0,0,0,.12)}}h1{{margin:0 0 8px;font-size:30px}}h2{{margin:0 0 18px;padding-bottom:10px;border-bottom:1px solid #b8c1df;font-size:21px}}h3{{margin:0 0 8px;font-size:16px}}.kpis+h3,.table-wrap+h3{{margin-top:22px}}.table-wrap+.callout{{margin-top:18px}}p{{margin:7px 0}}.muted{{color:var(--muted)}}.hero{{background:linear-gradient(145deg,#fff 0%,#eef0ff 100%)}}.hero-top,.gate-head{{display:flex;align-items:center;justify-content:space-between;gap:12px}}.decision{{font-size:28px;font-weight:800;color:var(--blue)}}.kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}.kpi{{background:var(--navy);color:white;border-radius:14px;padding:18px;min-width:0}}.kpi b{{display:block;font-size:25px;overflow-wrap:anywhere}}.kpi span{{color:#cbd5e1}}.gates,.actions{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.gate{{border:1px solid var(--line);border-radius:14px;padding:16px}}.tag{{border-radius:999px;padding:3px 9px;font-size:12px}}.tag.good{{background:var(--green);color:#146c2e}}.tag.warn{{background:var(--yellow);color:#8a5b00}}.tag.bad{{background:var(--red);color:#a32424}}.callout{{border-left:4px solid var(--purple);background:var(--lav);padding:15px 17px;border-radius:10px}}.audit{{border-left-color:#d69a14;background:var(--yellow)}}.action{{background:var(--green);border-radius:14px;padding:16px}}.chart{{margin:0;max-width:100%;overflow:hidden}}.chart figcaption{{font-weight:700;margin-bottom:8px}}svg{{display:block;width:100%;height:auto;max-width:100%}}.axis{{stroke:#d8deea;stroke-width:1}}.trend-line{{fill:none;stroke:var(--blue);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}}.axis-label{{fill:var(--muted);font-size:11px}}.bar-row{{display:grid;grid-template-columns:minmax(120px,2fr) minmax(120px,5fr) 72px;gap:10px;align-items:center;margin:10px 0}}.bar-label{{overflow-wrap:anywhere}}.bar-track{{height:14px;background:#edf0f6;border-radius:99px;overflow:hidden}}.bar-track span{{display:block;height:100%;background:var(--purple);border-radius:99px}}.bar-value{{text-align:right;font-variant-numeric:tabular-nums}}.table-wrap{{max-width:100%;overflow-x:auto}}table{{width:100%;border-collapse:collapse;table-layout:fixed}}th{{background:var(--slate);color:#fff;text-align:left;padding:10px;overflow-wrap:anywhere}}td{{border-bottom:1px solid var(--line);padding:10px;vertical-align:top;overflow-wrap:anywhere}}td.num{{text-align:right;font-variant-numeric:tabular-nums}}.empty{{padding:16px;color:var(--muted);background:#f6f7fa;border-radius:10px}}ul{{padding-left:20px}}footer{{color:#cbd5e1;text-align:center;padding:5px 0 24px}}
@media(max-width:760px){{main{{padding:10px}}.card{{padding:17px;border-radius:14px}}h1{{font-size:23px}}.kpis{{grid-template-columns:repeat(2,minmax(0,1fr))}}.gates,.actions{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr}}.bar-value{{text-align:left}}table{{min-width:660px}}}}
</style>
</head>
<body><main>
<section class="card hero"><div class="hero-top"><div><h1>{esc(report_title)}</h1><p class="muted">Amazon {esc(run.get('marketplace') or 'US')} · 输入词 {esc(keyword)} · 主调研词 {esc(primary_keyword)} · {esc(run.get('completed_at') or generated)}</p></div><div class="decision">{esc(result)}</div></div><div class="callout"><b>执行结论 · 置信度 {esc(confidence)}</b><p>{esc(summary)}</p></div></section>

<section class="card"><h2>核心指标</h2><div class="kpis">
<article class="kpi"><span>主调研词月搜索量</span><b>{number(keyword_detail.get('monthly_search_volume'))}</b><small>{percent(keyword_trend.get('year_over_year_change_pct'))} YoY</small></article>
<article class="kpi"><span>类目近 12 月平均月销量</span><b>{number(category_trend.get('recent_12m_average_units'))}</b><small>{percent(category_trend.get('year_over_year_change_pct'))} YoY</small></article>
<article class="kpi"><span>Google Web 近 52 周</span><b>{percent(web_trends.get('year_over_year_change_pct'))}</b><small>相对热度变化</small></article>
<article class="kpi"><span>负评样本</span><b>{number(review_sample.get('returned_reviews'))}/{number(review_sample.get('target'))}</b><small>已获取 / 目标</small></article>
</div></section>

<section class="card"><h2>三道门判断</h2><div class="gates">{gate_card('市场容量', evidence(market,'gate'))}{gate_card('竞争格局', evidence(competition,'gate'))}{gate_card('差异化机会', evidence(differentiation,'gate'))}</div></section>

<section class="card"><h2>数据源统计</h2><div class="kpis">{source_usage_kpis(source_usage)}</div><h3>工具 / API 调用明细</h3><div class="table-wrap"><table><thead><tr><th>数据源</th><th>Tool / API</th><th>调用次数</th><th>状态</th><th>说明</th></tr></thead><tbody>{source_usage_call_table(source_usage.get('tool_calls',[]) or [])}</tbody></table></div><h3>返回数据规模</h3><div class="table-wrap"><table><thead><tr><th>数据源</th><th>统计项</th><th>数量</th><th>单位</th><th>说明</th></tr></thead><tbody>{source_usage_output_table(source_usage.get('outputs',[]) or [])}</tbody></table></div><div class="callout audit"><b>统计口径</b><ul>{source_usage_notes}</ul></div></section>

<section class="card"><h2>市场趋势</h2>{line_chart(keyword_trend.get('months',[]),'month','search_volume','Amazon 精确关键词近 12 个月搜索趋势')}<h3>Top10 月销量分布</h3>{bar_rows((f'第 {i+1} 名',float(v),'') for i,v in enumerate(top10_units))}</section>

<section class="card"><h2>主调研词自动选择</h2><div class="kpis">
<article class="kpi"><span>用户输入词</span><b>{esc(keyword)}</b><small>研究起点</small></article>
<article class="kpi"><span>主调研词</span><b>{esc(primary_selection.get('primary_research_keyword') or '证据不足')}</b><small>固定脚本选择</small></article>
<article class="kpi"><span>自动接管</span><b>{'是' if handoff else '否'}</b><small>keyword_handoff</small></article>
<article class="kpi"><span>选择状态</span><b>{esc(primary_selection.get('selection_status') or '未完成')}</b><small>selected / insufficient</small></article>
</div><div class="callout"><b>固定公式</b><p>{esc(primary_selection.get('selection_formula') or 'V × R × I × C × (0.85 + 0.15 × S)')}</p><p>{esc(evidence(market,'primary_keyword_selection').get('notes') or 'LLM 只生成和分类候选词；最终主词由 Sorftime 证据和固定系数脚本选择。')}</p></div><div class="table-wrap"><table><thead><tr><th>关键词</th><th>类型</th><th>搜索量</th><th>R</th><th>I</th><th>C</th><th>销量乘数</th><th>最终得分</th><th>状态/淘汰原因</th></tr></thead><tbody>{keyword_selection_table(primary_selection.get('terms',[]) or [])}</tbody></table></div></section>

<section class="card"><h2>关键词漂移</h2><div class="kpis">
<article class="kpi"><span>品牌根词 / 精确泛词</span><b>{number(keyword_drift.get('brand_root_to_seed_volume_ratio'),2)}×</b><small>当前搜索量比值</small></article>
<article class="kpi"><span>种子与品牌根词重合</span><b>{percent(keyword_drift.get('seed_vs_brand_root_overlap_coefficient_pct'))}</b><small>Top20 overlap coefficient</small></article>
<article class="kpi"><span>品牌产品词同比</span><b>{percent(next((item.get('year_over_year_change_pct') for item in drift_terms if item.get('classification') == 'brand_product'), None))}</b><small>查询迁移信号</small></article>
<article class="kpi"><span>品牌拼写变体同比</span><b>{percent(next((item.get('year_over_year_change_pct') for item in drift_terms if item.get('classification') == 'brand_variant'), None))}</b><small>查询迁移信号</small></article>
</div><div class="table-wrap"><table><thead><tr><th>关键词</th><th>类型</th><th>当前月搜索量</th><th>近12月同比</th><th>最近半年变化</th><th>与种子Top20重合</th></tr></thead><tbody>{keyword_drift_table(drift_terms)}</tbody></table></div><div class="callout"><b>解释边界</b><p>{esc(evidence(market,'keyword_drift_analysis').get('notes') or '品牌词与非品牌词必须分开分析；品牌搜索量不能直接计入泛词可寻址需求。')}</p></div></section>

<section class="card"><h2>严格相关竞品</h2><div class="table-wrap"><table><thead><tr><th>ASIN</th><th>品牌</th><th>价格</th><th>月销量</th><th>评论数</th></tr></thead><tbody>{product_table(products)}</tbody></table></div></section>

<section class="card"><h2>用户痛点与差异化</h2>{bar_rows(complaint_bars)}<div class="actions">{''.join(improvement_cards)}</div></section>

<section class="card"><h2>站外交叉验证</h2><div class="table-wrap"><table><thead><tr><th>来源</th><th>支持的发现</th><th>证据等级</th></tr></thead><tbody>{''.join(offsite_rows)}</tbody></table></div></section>

<section class="card"><h2>数据源与审计</h2><div class="callout audit"><b>缺失、冲突与限制</b><ul>{audit_items}</ul></div><div class="table-wrap"><table><thead><tr><th>来源</th><th>状态</th><th>获取时间</th><th>范围/说明</th></tr></thead><tbody>{source_table(data.get('sources',[]) or [])}</tbody></table></div></section>

<section class="card"><h2>下一步</h2><div class="callout"><p>优先补齐会改变三道门结论的数据，再验证最具可执行性的产品改进。不要把宽泛类目数据直接当作严格细分市场需求。</p></div></section>
<footer>Generated {esc(generated)} · Self-contained report · No external scripts</footer>
</main></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title")
    args = parser.parse_args()
    data = json.loads(args.data_file.read_text(encoding="utf-8"))
    output = render(data, args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"WROTE {args.output.resolve()}")


if __name__ == "__main__":
    main()
