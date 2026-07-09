"""Tier 分层 + Sorftime 异步并发查询 + 爆发/回弹判断。

Sorftime 查询由 Python httpx 异步并发完成，Key 从环境变量或工作区 .env 读取。
Tier 1: keyword_trend + keyword_detail + keyword_extends（3 接口）
Tier 2: keyword_trend（1 接口）
"""
import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

import httpx

import config

logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    keyword: str
    tier: int
    current_rank: int
    previous_rank: Optional[int]
    rank_change: int
    category: str
    combo_label: str
    zh_name: str = ""
    monthly_volumes: list[dict] = field(default_factory=list)
    cpc_history: list[dict] = field(default_factory=list)
    burst_type: str = "unknown"
    historical_peak_rank: Optional[int] = None
    volume_mom_change: Optional[float] = None
    extended_keywords: list = field(default_factory=list)


def assign_tier(current_rank: int, rank_change: int, previous_rank: Optional[int]) -> int:
    """分配 Tier。rank_change 为有符号值：正数 = ABA 排名上升（数字变小/变好），负数 = 下跌。

    本系统只追踪"上升中的爆品"，ABA 排名下跌的关键词不属于任何 Tier（返回 0，后续被过滤）。
    返回 0 表示"非爆品/排名下跌"，调用方需据此剔除。
    """
    # 排名下跌或持平的词不是爆品，直接排除
    if rank_change <= 0:
        return 0

    prev = previous_rank or (current_rank + rank_change)
    if current_rank <= config.TIER1_RANK_THRESHOLD:
        if rank_change >= config.TIER1_SURGE_ABS or (prev > 0 and rank_change / prev >= config.TIER1_SURGE_RATIO):
            return 1
    if current_rank <= config.TIER2_RANK_THRESHOLD:
        if prev >= config.TIER2_CROSS_FROM and current_rank <= config.TIER2_CROSS_TO:
            return 2
        if rank_change >= 1000:
            return 2
    if current_rank > config.TIER2_RANK_THRESHOLD:
        if prev >= config.TIER3_CROSS_FROM and current_rank <= config.TIER3_CROSS_TO:
            return 3
        if rank_change >= 5000:
            return 3
    # 上升但未达到上面更高 Tier 的阈值：按当前排名归入对应 Tier
    if current_rank <= config.TIER1_RANK_THRESHOLD:
        return 1
    elif current_rank <= config.TIER2_RANK_THRESHOLD:
        return 2
    else:
        return 3


def determine_burst_type(monthly_volumes: list[dict], volume_mom: float = None) -> tuple[str, Optional[int]]:
    """判断爆发类型，基于 ABA 搜索排名趋势（排名数字越小=越热门=上升）。

    数据口径说明（重要）：
    - 本系统以 ABA Search Frequency Rank（搜索频率排名）为核心指标
    - ABA 排名是相对排名：#1 = 最热门，数字越小越好
    - "上升" = 排名数字变小（如 5000→200），"下降" = 排名数字变大（如 200→5000）
    - Sorftime 月搜索量作为辅助参考，不作为趋势判断的主要依据
    - 当 ABA 排名上升但搜索量环比下降时（高位正常回调），以 ABA 排名为准

    爆发类型：
    - first_burst: 24个月内从未进入 TOP 1000（真正的首次爆发）
    - rebound: 历史峰值曾进入 TOP 100，当前又冲回
    - steady_rise: 最近 3 个月 ABA 排名持续变好（数字持续变小）
    - declining: ABA 排名中期趋势下跌（最近排名比3个月前差，且月环比也在跌）
    - long_tail_expansion: 词根已是热词，长尾词首次出现
    - unknown: 数据不足
    """
    if not monthly_volumes:
        return "unknown", None
    ranks = [m.get("rank") or m.get("searchRank") for m in monthly_volumes if m.get("rank") or m.get("searchRank")]
    ranks = [r for r in ranks if r and r > 0]
    if not ranks:
        return "unknown", None

    historical_peak = min(ranks)  # 历史最佳排名（数字最小）

    # declining 判断：需要 ABA 排名中期趋势也在变差（数字变大）
    # 仅月搜索量环比下跌不足以判定 declining，必须排名也在恶化
    if volume_mom is not None and volume_mom < -0.3 and len(ranks) >= 4:
        recent_rank = ranks[-1]       # 最近月排名
        earlier_rank = ranks[-4]      # 3个月前排名
        # 只有当最近排名比3个月前差（数字更大）时才是真正下跌
        if recent_rank > earlier_rank:
            return "declining", historical_peak
        # 否则：搜索量环比下跌但排名仍在改善 → 高位正常回调，不是 declining

    # 历史曾进入 TOP 100 → rebound
    if historical_peak <= config.REBOUND_PEAK_THRESHOLD and len(ranks) > 3:
        peak_idx = ranks.index(historical_peak)
        if peak_idx < len(ranks) - 2:
            return "rebound", historical_peak

    # 历史曾进入 TOP 1000 → 不是首次爆发
    if historical_peak <= 1000:
        if len(ranks) >= 3 and ranks[-1] < ranks[-2] < ranks[-3]:
            return "steady_rise", historical_peak
        return "rebound", historical_peak

    # 历史从未进入 TOP 1000 → 首次爆发
    if len(ranks) >= 3 and ranks[-1] < ranks[-2] < ranks[-3]:
        return "steady_rise", historical_peak
    return "first_burst", historical_peak


def determine_burst_type_with_root(keyword: str, monthly_volumes: list[dict],
                                    volume_mom: float, all_tier1_keywords: list[str]) -> tuple[str, Optional[int]]:
    """增强版爆发类型判断：如果是某个 Tier 1 词的长尾词，标记为 long_tail_expansion"""
    burst_type, peak = determine_burst_type(monthly_volumes, volume_mom)

    # 检查是否是某个已知热词的长尾扩展
    kw_lower = keyword.lower()
    for root_kw in all_tier1_keywords:
        root_lower = root_kw.lower()
        if root_lower != kw_lower and root_lower in kw_lower and len(root_lower) >= 3:
            # 这个词包含某个 Tier 1 词作为子串 → 长尾扩展
            if burst_type == "first_burst":
                return "long_tail_expansion", peak
            break

    return burst_type, peak


def calc_volume_mom(monthly_volumes: list[dict]) -> Optional[float]:
    volumes = [m.get("searchVolume") or m.get("volume", 0) for m in monthly_volumes]
    volumes = [v for v in volumes if v and v > 0]
    if len(volumes) >= 2:
        prev, curr = volumes[-2], volumes[-1]
        if prev > 0:
            return (curr - prev) / prev
    return None


# ─── Sorftime 异步并发查询 ───

async def _sorftime_call(client: httpx.AsyncClient, method: str, arguments: dict) -> Optional[dict]:
    """Sorftime MCP 返回 SSE (text/event-stream)，需要解析 data: 行"""
    try:
        resp = await client.post(
            config.SORFTIME_BASE_URL,
            params={"key": config.SORFTIME_API_KEY},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                  "params": {"name": method, "arguments": arguments}},
            timeout=config.SORFTIME_TIMEOUT,
        )
        resp.raise_for_status()
        # 解析 SSE: 提取所有 data: 行，合并后解析 JSON
        text = resp.text
        result = None
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("data: "):
                try:
                    payload = json.loads(line[6:])
                    if "result" in payload:
                        result = payload["result"]
                except json.JSONDecodeError:
                    continue
        return result
    except Exception as e:
        # 不记录异常中的 request URL，避免查询参数里的 API Key 进入日志。
        logger.debug("Sorftime %s 失败 (%s): %s", method, arguments, type(e).__name__)
        return None


def _parse_response(raw) -> list[dict]:
    """解析 Sorftime MCP 响应为结构化数据。
    Sorftime 返回中文格式如 {"搜索量趋势":["2024年03月搜索量89085",...], "搜索排名趋势":[...], "推荐竞价趋势":[...]}
    需要转换为 [{"searchVolume": 89085, "searchRank": 17161, "month": "2024-03", "cpc": 1.95}, ...]
    """
    if not raw:
        return []
    try:
        # 提取 content[0].text 中的 JSON
        text_data = None
        if isinstance(raw, dict) and "content" in raw:
            content = raw["content"]
            if isinstance(content, list) and content:
                text_data = content[0].get("text", "")
        elif isinstance(raw, str):
            text_data = raw

        if not text_data:
            return []

        # 尝试从文本中提取 JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', text_data)
        if not json_match:
            return []
        parsed = json.loads(json_match.group())

        if not isinstance(parsed, dict):
            return parsed if isinstance(parsed, list) else []

        # 解析中文格式的趋势数据
        volumes = parsed.get("搜索量趋势", [])
        ranks = parsed.get("搜索排名趋势", [])
        cpcs = parsed.get("推荐竞价趋势", [])

        if not volumes and not ranks:
            # 可能是其他格式，尝试直接返回
            if "data" in parsed:
                return parsed["data"] if isinstance(parsed["data"], list) else []
            return []

        # 解析中文月度数据: "2024年03月搜索量89085" → {month, searchVolume}
        month_data = {}
        for item in volumes:
            m = re.match(r'(\d{4})年(\d{2})月搜索量(-?\d+\.?\d*)', str(item))
            if m:
                month = f"{m.group(1)}-{m.group(2)}"
                month_data.setdefault(month, {})["searchVolume"] = int(float(m.group(3)))
                month_data[month]["month"] = month

        for item in ranks:
            m = re.match(r'(\d{4})年(\d{2})月搜索排名(-?\d+\.?\d*)', str(item))
            if m:
                month = f"{m.group(1)}-{m.group(2)}"
                month_data.setdefault(month, {})["searchRank"] = int(float(m.group(3)))
                month_data[month]["month"] = month

        for item in cpcs:
            m = re.match(r'(\d{4})年(\d{2})月cpc推荐竞价(-?\d+\.?\d*)', str(item))
            if m:
                month = f"{m.group(1)}-{m.group(2)}"
                month_data.setdefault(month, {})["cpc"] = float(m.group(3))
                month_data[month]["month"] = month

        result = sorted(month_data.values(), key=lambda x: x.get("month", ""))
        return result
    except Exception as e:
        logger.debug(f"解析响应失败: {e}")
        return []


def _parse_extends(raw) -> list[dict]:
    """解析延伸词数据，返回结构化的 dict 列表"""
    if not raw:
        return []
    try:
        text_data = None
        if isinstance(raw, dict) and "content" in raw:
            content = raw["content"]
            if isinstance(content, list) and content:
                text_data = content[0].get("text", "")
        elif isinstance(raw, str):
            text_data = raw

        if not text_data:
            return []

        # Sorftime keyword_extends 返回的是中文格式的 dict 列表
        # 尝试用 ast.literal_eval 解析 Python dict 字符串
        import ast

        # 尝试提取 JSON 数组
        arr_match = re.search(r'\[[\s\S]*\]', text_data)
        if arr_match:
            try:
                inner = json.loads(arr_match.group())
            except json.JSONDecodeError:
                try:
                    inner = ast.literal_eval(arr_match.group())
                except Exception:
                    inner = []
            if isinstance(inner, list):
                result = []
                for item in inner[:10]:
                    if isinstance(item, dict):
                        result.append(item)
                    elif isinstance(item, str):
                        # 可能是 dict 的字符串表示
                        try:
                            parsed = ast.literal_eval(item)
                            if isinstance(parsed, dict):
                                result.append(parsed)
                            else:
                                result.append({"关键词": item})
                        except Exception:
                            result.append({"关键词": item})
                return result
    except Exception:
        pass
    return []


async def _query_keyword_full(client: httpx.AsyncClient, kw: str, sem: asyncio.Semaphore) -> tuple[str, dict]:
    """Tier 1: 查 trend + detail + extends"""
    async with sem:
        trend_raw, detail_raw, extends_raw = await asyncio.gather(
            _sorftime_call(client, "keyword_trend", {"keywordSupportSite": "US", "keyword": kw}),
            _sorftime_call(client, "keyword_detail", {"keywordSupportSite": "US", "keyword": kw}),
            _sorftime_call(client, "keyword_extends", {"keywordSupportSite": "US", "keyword": kw}),
        )
    result = {}
    if trend_raw:
        result["trend"] = _parse_response(trend_raw)
    if detail_raw:
        parsed = _parse_response(detail_raw)
        result["detail"] = parsed[0] if parsed else detail_raw
    result["extends"] = _parse_extends(extends_raw)
    return kw, result


async def _query_keyword_trend(client: httpx.AsyncClient, kw: str, sem: asyncio.Semaphore) -> tuple[str, dict]:
    """Tier 2: 只查 trend"""
    async with sem:
        trend_raw = await _sorftime_call(client, "keyword_trend", {"keywordSupportSite": "US", "keyword": kw})
    result = {}
    if trend_raw:
        result["trend"] = _parse_response(trend_raw)
    return kw, result


async def _batch_query(tier1_kws: list[str], tier2_kws: list[str]) -> dict:
    """异步并发查询所有关键词"""
    sem = asyncio.Semaphore(config.SORFTIME_CONCURRENCY)
    results = {}
    async with httpx.AsyncClient(verify=config.VERIFY_SSL, proxy=config.HTTPX_PROXY) as client:
        tasks = []
        for kw in tier1_kws:
            tasks.append(_query_keyword_full(client, kw, sem))
        for kw in tier2_kws:
            tasks.append(_query_keyword_trend(client, kw, sem))
        for coro in asyncio.as_completed(tasks):
            kw, data = await coro
            if data:
                results[kw] = data
                logger.info(f"  ✓ {kw}")
    return results


def query_sorftime_batch(tier1_kws: list[str], tier2_kws: list[str]) -> tuple[dict, dict]:
    """同步入口：批量查询 Sorftime，返回 (数据, 统计信息)"""
    total = len(tier1_kws) * 3 + len(tier2_kws)
    logger.info(f"🔍 Sorftime 异步查询: Tier1={len(tier1_kws)}×3 + Tier2={len(tier2_kws)}×1 = {total} 次调用")
    data = asyncio.run(_batch_query(tier1_kws, tier2_kws))
    stats = {
        "tier1_keywords": len(tier1_kws),
        "tier2_keywords": len(tier2_kws),
        "tier1_calls": len(tier1_kws) * 3,
        "tier2_calls": len(tier2_kws),
        "total_calls": total,
        "enriched": len(data),
    }
    return data, stats


# ─── 分层和丰富 ───

def enrich_with_sorftime(td: TrendData, kw_data: dict, all_tier1_keywords: list[str] = None):
    all_tier1_keywords = all_tier1_keywords or []
    if "trend" in kw_data and isinstance(kw_data["trend"], list):
        td.monthly_volumes = kw_data["trend"]
        td.volume_mom_change = calc_volume_mom(td.monthly_volumes)
        td.burst_type, td.historical_peak_rank = determine_burst_type_with_root(
            td.keyword, td.monthly_volumes, td.volume_mom_change, all_tier1_keywords
        )
    if "detail" in kw_data:
        detail = kw_data["detail"]
        td.cpc_history = detail if isinstance(detail, list) else [detail]
    if "extends" in kw_data and isinstance(kw_data["extends"], list):
        td.extended_keywords = kw_data["extends"][:10]


def analyze_keywords_basic(entries: list[dict], classifications: dict[str, str],
                           translations: dict[str, str] = None) -> list[TrendData]:
    results = []
    translations = translations or {}
    excluded_declining = 0
    for entry in entries:
        kw = entry["keyword"]
        if kw not in classifications:
            continue
        tier = assign_tier(entry["current_rank"], entry["rank_change"], entry.get("previous_rank"))
        if tier == 0:
            # ABA 排名下跌/持平，不是上升爆品，剔除
            excluded_declining += 1
            continue
        td = TrendData(
            keyword=kw, tier=tier, current_rank=entry["current_rank"],
            previous_rank=entry.get("previous_rank"), rank_change=entry["rank_change"],
            category=classifications[kw], combo_label=entry["combo_label"],
            zh_name=translations.get(kw, ""),
        )
        results.append(td)
    results.sort(key=lambda x: (x.tier, -x.rank_change))
    t1 = sum(1 for r in results if r.tier == 1)
    t2 = sum(1 for r in results if r.tier == 2)
    t3 = sum(1 for r in results if r.tier == 3)
    logger.info(f"分层完成: 共 {len(results)} 个, Tier1={t1}, Tier2={t2}, Tier3={t3}"
                f"（剔除 {excluded_declining} 个 ABA 排名下跌/持平词）")
    return results


def apply_sorftime_results(results: list[TrendData], sorftime_data: dict) -> list[TrendData]:
    # 收集所有 Tier 1 关键词用于长尾词根识别
    tier1_kws = [r.keyword for r in results if r.tier == 1]
    count = 0
    for td in results:
        if td.tier <= 2 and td.keyword in sorftime_data:
            enrich_with_sorftime(td, sorftime_data[td.keyword], tier1_kws)
            count += 1
    logger.info(f"深度分析完成: {count} 个关键词已丰富")
    return results
