"""HTML 报告生成器 — 卡片式布局 + AI 分析摘要"""
import os
import logging
from datetime import datetime
from dataclasses import asdict

from jinja2 import Environment, FileSystemLoader

import config
from analyzer import TrendData

logger = logging.getLogger(__name__)


def generate_report(
    results: list[TrendData],
    total_scraped: int,
    total_supplement: int,
    new_dict_words: dict[str, list[str]],
    analysis: dict = None,
    excluded_keywords: dict = None,
    sorftime_stats: dict = None,
) -> str:
    os.makedirs(config.REPORT_DIR, exist_ok=True)
    analysis = analysis or {}
    excluded_keywords = excluded_keywords or {}
    sorftime_stats = sorftime_stats or {}
    tier1 = [r for r in results if r.tier == 1]
    tier2 = [r for r in results if r.tier == 2]
    tier3 = [r for r in results if r.tier == 3]
    now = datetime.now()

    keyword_analysis = analysis.get("keyword_analysis", {})
    tracks = analysis.get("tracks", [])
    core_findings = analysis.get("core_findings", [])

    context = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "week_label": f"{now.year} 第 {now.isocalendar()[1]} 周",
        "week_code": f"W{now.isocalendar()[1]:02d}",
        "total_scraped": total_scraped,
        "total_supplement": total_supplement,
        "tier1_count": len(tier1),
        "tier2_count": len(tier2),
        "tier3_count": len(tier3),
        "tier1": [_enrich(r, keyword_analysis) for r in tier1],
        "tier2": [_enrich(r, keyword_analysis) for r in tier2],
        "tier3": [_enrich(r, keyword_analysis) for r in tier3],
        "tracks": tracks,
        "core_findings": core_findings,
        "new_words": new_dict_words,
        "total_new_words": sum(len(v) for v in new_dict_words.values()),
        "excluded_keywords": excluded_keywords,
        "excluded_count": len(excluded_keywords),
        "sorftime_stats": sorftime_stats,
    }
    env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR), autoescape=True)
    template = env.get_template("report.html")
    html = template.render(**context)

    week_str = f"{now.year}-W{now.isocalendar()[1]:02d}"
    filename = f"supplement_monitor_{week_str}.html"
    filepath = os.path.join(config.REPORT_DIR, filename)
    # 同周覆盖：如果同周报告已存在，直接覆盖而非新建
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"报告已生成: {filepath}")
    return filepath


def _enrich(td: TrendData, keyword_analysis: dict = None) -> dict:
    d = asdict(td)
    keyword_analysis = keyword_analysis or {}
    burst_map = {
        "first_burst": ("🆕 首次爆发", "burst-first"),
        "rebound": ("🔄 回弹", "burst-rebound"),
        "steady_rise": ("📈 持续爆发", "burst-steady"),
        "declining": ("📉 下跌中", "burst-decline"),
        "long_tail_expansion": ("🌱 长尾扩展", "burst-longtail"),
        "unknown": ("❓ 未知", ""),
    }
    label, css = burst_map.get(td.burst_type, ("❓ 未知", ""))
    d["burst_type_label"] = label
    d["burst_type_css"] = css
    cat_map = {
        "ingredient": ("🧪 成分", "cat-ingredient"),
        "benefit": ("💪 功效/症状", "cat-benefit"),
        "brand": ("🏷️ 品牌", "cat-brand"),
        "condition": ("🩺 功效/症状", "cat-condition"),
        "form": ("💊 剂型", "cat-form"),
    }
    cat_label, cat_css = cat_map.get(td.category, (td.category, ""))
    d["category_label"] = cat_label
    d["category_css"] = cat_css
    d["zh_name"] = td.zh_name or ""
    d["analysis_text"] = keyword_analysis.get(td.keyword, "")

    # 排名变化方向：previous_rank - current_rank（正=上升，负=下跌）
    if td.previous_rank and td.previous_rank > 0:
        real_change = td.previous_rank - td.current_rank
        d["rank_direction"] = "up" if real_change > 0 else "down"
        d["rank_change_display"] = f"+{real_change:,}" if real_change > 0 else f"{real_change:,}"
        d["rank_change_abs"] = abs(real_change)
    else:
        d["rank_direction"] = "new"
        d["rank_change_display"] = "NEW"
        d["rank_change_abs"] = 0

    # 月搜索量（最新有效值）
    vols = [(m.get("searchVolume") or m.get("volume", 0)) for m in (td.monthly_volumes or [])
            if (m.get("searchVolume") or m.get("volume", 0)) > 0]
    d["latest_volume"] = vols[-1] if vols else 0
    d["peak_volume"] = max(vols) if vols else 0

    # CPC（从 monthly_volumes 的 cpc 字段或 cpc_history 提取）
    cpc_val = None
    # 先从 monthly_volumes 最新月份的 cpc 提取
    for m in reversed(td.monthly_volumes or []):
        if isinstance(m, dict) and m.get("cpc") and float(m["cpc"]) > 0:
            cpc_val = float(m["cpc"])
            break
    # fallback: 从 cpc_history 提取
    if not cpc_val and td.cpc_history:
        for c in reversed(td.cpc_history):
            if isinstance(c, dict):
                v = c.get("cpc") or c.get("推荐竞价") or c.get("bid")
                if v and float(v) > 0:
                    cpc_val = float(v)
                    break
    d["cpc"] = f"${cpc_val:.2f}" if cpc_val else "N/A"

    if td.volume_mom_change is not None:
        d["mom_pct"] = f"{td.volume_mom_change * 100:+.0f}%"
    else:
        d["mom_pct"] = "N/A"

    # Sparkline 数据（最近 12 个月搜索量）
    d["sparkline_data"] = [
        m.get("searchVolume") or m.get("volume", 0)
        for m in (td.monthly_volumes or [])[-12:]
    ]
    return d
