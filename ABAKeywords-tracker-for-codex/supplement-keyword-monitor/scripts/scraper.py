"""AMZ123 ABA 热搜词榜单抓取与解析"""
import re
import time
import logging
from dataclasses import dataclass, asdict
from typing import Optional

import httpx
from selectolax.parser import HTMLParser

import config

logger = logging.getLogger(__name__)


@dataclass
class KeywordEntry:
    """单条关键词数据"""
    keyword: str
    current_rank: int
    previous_rank: Optional[int]
    rank_change: int
    combo_label: str


def build_url(page: int, rank: str, uprank: str) -> str:
    return f"{config.AMZ123_BASE_URL}/{page}?rank={rank}&uprank={uprank}&s=&k=&o="


def parse_page(html: str, combo_label: str) -> list[KeywordEntry]:
    """解析 AMZ123 页面 HTML，提取关键词数据"""
    entries = []
    tree = HTMLParser(html)
    items = tree.css("div.table-body-item")
    if not items:
        logger.warning(f"[{combo_label}] 未找到 div.table-body-item，页面结构可能已变更")
        return entries

    for item in items:
        try:
            kw_el = item.css_first("a.table-body-item-words-word span")
            if not kw_el:
                kw_el = item.css_first("a.table-body-item-words-word")
            if not kw_el:
                continue
            keyword = kw_el.text(strip=True).lower()
            if not keyword or len(keyword) < 2:
                continue

            rank_div = item.css_first("div.table-body-item-rank")
            if not rank_div:
                continue

            spans = rank_div.css("span")
            numbers = []
            for sp in spans:
                text = sp.text(strip=True).replace(",", "").replace("，", "")
                m = re.search(r'\d+', text)
                if m:
                    numbers.append(int(m.group()))

            if len(numbers) < 1:
                continue

            # AMZ123 在 rank cell 内用 up.svg / down.svg 箭头表示涨跌方向，
            # 仅靠数字无法判断方向，必须读取箭头 img 才能区分"排名上升"与"排名下跌"。
            fluct_img = rank_div.css_first("div.table-body-item-rank-fluctuation img")
            is_down = False
            if fluct_img:
                src = fluct_img.attributes.get("src", "") or ""
                is_down = "down." in src.lower()

            current_rank = numbers[0]
            previous_rank = numbers[1] if len(numbers) > 1 else None
            magnitude = numbers[2] if len(numbers) > 2 else (
                abs(previous_rank - current_rank) if previous_rank else 0
            )

            # 有符号涨幅：正数 = ABA 排名上升（数字变小/变好），负数 = 排名下跌。
            # 优先用 previous-current（同时编码了方向与幅度）；缺少 previous 时用箭头定向。
            if previous_rank is not None:
                rank_change = previous_rank - current_rank
            else:
                rank_change = -magnitude if is_down else magnitude

            entries.append(KeywordEntry(
                keyword=keyword,
                current_rank=current_rank,
                previous_rank=previous_rank,
                rank_change=rank_change,
                combo_label=combo_label,
            ))
        except Exception as e:
            logger.debug(f"解析条目失败: {e}")
            continue

    return entries


def fetch_page(url: str) -> Optional[str]:
    """通过 httpx 抓取页面（自动使用修正后的代理配置）"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        resp = httpx.get(
            url, headers=headers, timeout=30,
            verify=config.VERIFY_SSL, follow_redirects=True,
            proxy=config.HTTPX_PROXY,
        )
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error(f"抓取失败 {url}: {e}")
        return None


def scrape_all_combos() -> list[KeywordEntry]:
    """按 6 个组合 × 最多 5 页抓取，去重合并"""
    all_entries: dict[str, KeywordEntry] = {}

    for combo in config.SCRAPE_COMBOS:
        label = combo["label"]
        logger.info(f"开始抓取组合: {label}")

        for page in range(1, config.MAX_PAGES + 1):
            url = build_url(page, combo["rank"], combo["uprank"])
            logger.info(f"  第 {page} 页: {url}")

            html = fetch_page(url)
            if not html:
                logger.warning(f"  第 {page} 页抓取失败，跳过")
                break

            entries = parse_page(html, label)
            if not entries:
                logger.info(f"  第 {page} 页无数据，停止翻页")
                break

            for entry in entries:
                if entry.keyword not in all_entries or entry.rank_change > all_entries[entry.keyword].rank_change:
                    all_entries[entry.keyword] = entry

            logger.info(f"  第 {page} 页解析到 {len(entries)} 条")
            time.sleep(1.5)

        time.sleep(2)

    result = list(all_entries.values())
    logger.info(f"抓取完成，共 {len(result)} 个去重关键词")
    return result


def entries_to_dicts(entries: list[KeywordEntry]) -> list[dict]:
    return [asdict(e) for e in entries]
