#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parse Amazon search-result HTML captured by xCrawl into product-card and
organic-ASIN JSON files.

Usage:
  python parse_amazon_search_xcrawl.py \
    --input output/xcrawl_urolithin_a/amazon_search_urolithin_a_page1_raw.html \
    --keyword "urolithin a" \
    --output-dir output/xcrawl_urolithin_a
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _parse_price(text: str) -> float | None:
    match = re.search(r"\$\s*([0-9]+(?:\.[0-9]{2})?)", text)
    return float(match.group(1)) if match else None


def _parse_rating(text: str) -> float | None:
    match = re.search(r"([0-5](?:\.[0-9])?)\s+out of 5 stars", text)
    return float(match.group(1)) if match else None


def _parse_reviews(text: str) -> int | None:
    match = re.search(r"\(([0-9,]+)\)", text)
    return int(match.group(1).replace(",", "")) if match else None


def _product_url(card: Any, asin: str) -> str:
    for link in card.find_all("a", href=True):
        href = link["href"]
        if asin in href:
            return "https://www.amazon.com" + href if href.startswith("/") else href
    return f"https://www.amazon.com/dp/{asin}"


def parse_cards(html: str, keyword: str, page: int) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select('[data-component-type="s-search-result"][data-asin]')
    rows: list[dict[str, Any]] = []
    for position, card in enumerate(cards, start=1):
        asin = card.get("data-asin") or ""
        if not asin:
            continue

        text = _clean(card.get_text(" ", strip=True))
        title_node = card.find("h2")
        title = _clean(title_node.get_text(" ", strip=True)) if title_node else ""
        if not title:
            image = card.find("img", alt=True)
            title = _clean(image.get("alt", "")) if image else ""

        sponsored = bool(re.search(r"\bSponsored\b", text, re.IGNORECASE)) or bool(
            card.select('[aria-label*="Sponsored"], .puis-sponsored-label-text')
        )
        badge = ""
        if "Overall Pick" in text:
            badge = "Overall Pick"
        elif "Amazon's Choice" in text:
            badge = "Amazon's Choice"
        elif "Best Seller" in text:
            badge = "Best Seller"

        rows.append(
            {
                "search_keyword": keyword,
                "page": page,
                "position_on_page": position,
                "asin": asin,
                "title_from_xcrawl": title,
                "sponsored": sponsored,
                "organic": not sponsored,
                "badge": badge,
                "price_visible": _parse_price(text),
                "rating_visible": _parse_rating(text),
                "reviews_visible": _parse_reviews(text),
                "product_url": _product_url(card, asin),
                "text_sample": text[:500],
            }
        )
    return rows


def unique_organic(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for card in cards:
        asin = card["asin"]
        if card["organic"] and asin not in seen:
            seen.add(asin)
            rows.append({**card, "organic_rank": len(rows) + 1})
    return rows


def unique_all(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for card in cards:
        asin = card["asin"]
        if asin not in seen:
            seen.add(asin)
            rows.append(card)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Amazon search raw HTML captured by xCrawl.")
    parser.add_argument("--input", required=True, help="Path to xCrawl raw_html file")
    parser.add_argument("--keyword", required=True, help="Amazon search keyword")
    parser.add_argument("--page", type=int, default=1, help="Amazon search result page number")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON outputs")
    parser.add_argument("--prefix", default="", help="Optional output filename prefix")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = args.prefix or re.sub(r"\W+", "_", args.keyword.strip().lower()).strip("_")
    html = input_path.read_text(encoding="utf-8", errors="ignore")
    cards = parse_cards(html, args.keyword, args.page)
    organic = unique_organic(cards)
    all_unique = unique_all(cards)

    (output_dir / f"{prefix}_cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / f"{prefix}_organic_asins.json").write_text(
        json.dumps(organic, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / f"{prefix}_unique_all_asins.json").write_text(
        json.dumps(all_unique, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "cards": len(cards),
                "unique_all_asins": len(all_unique),
                "organic_unique_asins": len(organic),
                "sponsored_cards": sum(1 for row in cards if row["sponsored"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
