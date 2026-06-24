#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build report-ready web signal sections from web_signal_analysis.json.

This helper does not call xCrawl directly. It normalizes already collected
xCrawl/search/scrape summaries into:
- chapters.ch07_web_signal_intelligence
- Web情报_* Excel sheets
- artifacts/web_signal_analysis.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("web signal input must be a JSON object")
    return data


def build_chapter(web: dict[str, Any]) -> dict[str, Any]:
    return {
        "coverage": web.get("coverage", {}),
        "platform_summary": web.get("platform_summary", []),
        "demand_signals": web.get("demand_signals", []),
        "ingredient_feedback": web.get("ingredient_feedback", []),
        "safety_signals": web.get("safety_signals", []),
        "brand_narratives": web.get("brand_narratives", []),
        "trend_signals": web.get("trend_signals", []),
        "insight": web.get("insight", ""),
    }


def build_sheets(web: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    search_rows = []
    for item in web.get("search_results", []):
        search_rows.append({
            "查询词": item.get("query", ""),
            "排名": item.get("position", ""),
            "标题": item.get("title", ""),
            "URL": item.get("url", ""),
            "平台": item.get("platform", ""),
            "来源类型": item.get("source_type", "search_result"),
        })

    scrape_rows = []
    for item in web.get("scraped_pages", []):
        scrape_rows.append({
            "URL": item.get("url", ""),
            "平台": item.get("platform", ""),
            "标题": item.get("title", ""),
            "摘要": item.get("summary", ""),
            "情绪": item.get("sentiment", ""),
            "关键话题": ", ".join(item.get("key_topics", [])),
            "来源查询词": item.get("source_query", ""),
            "内容类型": item.get("content_type", ""),
        })

    insight_rows = []
    for item in web.get("platform_summary", []):
        sentiment = item.get("sentiment_distribution", {})
        insight_rows.append({
            "类型": "平台汇总",
            "对象": item.get("platform", ""),
            "内容": f"样本 {item.get('mention_count', 0)}；正/中/负={sentiment.get('positive', 0)}/{sentiment.get('neutral', 0)}/{sentiment.get('negative', 0)}",
            "主题": ", ".join(item.get("top_topics", [])),
            "来源": item.get("platform", ""),
        })
    for item in web.get("demand_signals", []):
        insight_rows.append({
            "类型": "需求信号",
            "对象": item.get("signal", ""),
            "内容": item.get("relevance", ""),
            "主题": "",
            "来源": item.get("source_url", item.get("source", "")),
        })
    for item in web.get("safety_signals", []):
        insight_rows.append({
            "类型": "风险信号",
            "对象": item.get("concern", ""),
            "内容": item.get("relevance", ""),
            "主题": item.get("frequency", ""),
            "来源": ", ".join(item.get("source_platforms", [])),
        })
    for item in web.get("brand_narratives", []):
        insight_rows.append({
            "类型": "竞品叙事",
            "对象": item.get("brand", ""),
            "内容": item.get("positioning", ""),
            "主题": item.get("implication", ""),
            "来源": item.get("source", ""),
        })

    return {
        "Web情报_搜索结果": search_rows,
        "Web情报_抓取明细": scrape_rows,
        "Web情报_综合洞察": insight_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build web signal chapter and Excel sheets")
    parser.add_argument("--input", "-i", required=True, help="web_signal_analysis.json path")
    parser.add_argument("--output", "-o", required=True, help="output JSON path")
    args = parser.parse_args()

    web = load_json(Path(args.input))
    result = {
        "chapter": build_chapter(web),
        "excel_sheets": build_sheets(web),
        "artifacts": {
            "web_signal_analysis.json": web,
        },
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
