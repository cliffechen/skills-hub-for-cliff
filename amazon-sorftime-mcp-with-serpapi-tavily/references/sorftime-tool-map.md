# Sorftime MCP tool map

This map reflects the live Codex tool schema observed on 2026-07-14. Always inspect the currently exposed tool declaration before calling because upstream repositories and live MCP schemas can drift.

## Core calls

| Need | Live tool | Required parameters | Notes |
| --- | --- | --- | --- |
| Broad product-to-category search | `category_search_from_product_name` | `productName`, optional `amzSite` | Returns related category markets; supports optional filters |
| Exact category-name search | `category_name_search` | `categoryName`, optional `amzSite` | Current live schema uses `categoryName`, not `searchName` |
| Category Top100 report | `category_report` | `nodeId`, optional `amzSite` | `nodeId` is a string |
| Category trend | `category_trend` | `nodeId`, optional `amzSite`, `trendIndex` | Keep sales-amount proxy definitions separate from unit metrics |
| Category keywords | `category_keywords` | `nodeId`, optional `amzSite`, `page` | Twenty results per page |
| Keyword detail | `keyword_detail` | `keyword`, optional `keywordSupportSite` | Site parameter is `keywordSupportSite` |
| Keyword extensions | `keyword_extends` | `keyword`, optional `keywordSupportSite`, `page` | Use for related-demand discovery |
| Product detail | `product_detail` | `asin`, optional `amzSite` | One ASIN per call |
| Product reviews | `product_reviews` | `asin`, optional `amzSite`, `reviewType` | Use `reviewType: "Negative"`; up to 100 recent-year reviews |

## Useful category trend values

- `SalesCount`
- `BrandProductCount`
- `SellerProductCount`
- `AvgPrice`
- `AvgRatingCount`
- `AvgScore`
- `NewProductSalesAmountShare`
- `AmazonSalesAmountShare`
- `Top3ProductSalesAmountShare`
- `Top3BrandSalesAmountShare`
- `Top3SellerSalesAmountShare`

## Parameter-drift warning

The upstream GitHub product-research skill documents `category_name_search` with `searchName`, while the live MCP schema observed by Codex requires `categoryName`. Treat the live tool declaration as authoritative. Do not repeat an old parameter after a 406/validation error.

## Metric discipline

- Three-month new-product sales share does not replace six-month new-listing count share.
- Top3/Top100 sales-amount share does not replace Top3/Top10 unit share.
- Top-brand sales share does not replace listing-count brand concentration.
- Broad-category Top100 evidence does not automatically describe a strict ingredient or niche subset.

## Upstream attribution

Tool research was cross-checked against `liangdabiao/amazon-sorftime-research-MCP-skill` at commit `1b7afac`. The live MCP schema overrides repository examples when they differ.
