"""Strict validation for Agent-produced exchange JSON."""
from __future__ import annotations

import json
import os


def load_validated_analysis(path: str, tier1_keywords: list[str]) -> dict:
    """Validate Agent analysis before rendering or publishing the report."""
    if not tier1_keywords and not os.path.exists(path):
        return {"keyword_analysis": {}, "tracks": [], "core_findings": []}
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"未找到分析结果: {path}。请先根据 analysis_input.json 生成 analysis_output.json。"
        )
    with open(path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    if not isinstance(analysis, dict):
        raise ValueError("analysis_output.json 顶层必须是 JSON 对象")

    keyword_analysis = analysis.get("keyword_analysis")
    tracks = analysis.get("tracks")
    core_findings = analysis.get("core_findings")
    if not isinstance(keyword_analysis, dict):
        raise ValueError("keyword_analysis 必须是对象")
    if not isinstance(tracks, list):
        raise ValueError("tracks 必须是数组")
    if not isinstance(core_findings, list):
        raise ValueError("core_findings 必须是数组")

    expected = set(tier1_keywords)
    actual = set(keyword_analysis)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise ValueError(f"keyword_analysis 关键词不匹配；缺少={missing}；多余={extra}")
    invalid_summaries = [
        keyword
        for keyword, summary in keyword_analysis.items()
        if not isinstance(summary, str) or not summary.strip()
    ]
    if invalid_summaries:
        raise ValueError(f"以下关键词的分析摘要为空或格式错误: {invalid_summaries}")
    if any(not isinstance(item, str) or not item.strip() for item in core_findings):
        raise ValueError("core_findings 的每一项都必须是非空字符串")

    clustered: list[str] = []
    for index, track in enumerate(tracks):
        if not isinstance(track, dict):
            raise ValueError(f"tracks[{index}] 必须是对象")
        for field in ("name", "icon", "summary"):
            if not isinstance(track.get(field), str) or not track[field].strip():
                raise ValueError(f"tracks[{index}].{field} 必须是非空字符串")
        keywords = track.get("keywords")
        if not isinstance(keywords, list) or any(not isinstance(k, str) for k in keywords):
            raise ValueError(f"tracks[{index}].keywords 必须是字符串数组")
        clustered.extend(keywords)

    clustered_set = set(clustered)
    unknown_clustered = sorted(clustered_set - expected)
    missing_clustered = sorted(expected - clustered_set)
    duplicated = sorted({keyword for keyword in clustered if clustered.count(keyword) > 1})
    if unknown_clustered or missing_clustered or duplicated:
        raise ValueError(
            "tracks 关键词覆盖错误；"
            f"未知={unknown_clustered}；未归类={missing_clustered}；重复={duplicated}"
        )
    return analysis
