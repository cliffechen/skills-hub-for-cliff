# Formula Reconstruction Skill

## What it does

Turns upstream compliance reports (Skill 1) and safe-rebuild briefs (Skill 2)
into a science-backed, market-driven, keyword-optimized formula upgrade plan.

## When to use

After you have both:
- `{name}-upstream-risk-report.md` from Skill 1
- `{name}-safe-rebuild-brief.md` from Skill 2

## Three decision dimensions

1. **Keyword Competition** — find blue-ocean keywords on Amazon
2. **Market Demand** — mine pain points from Amazon reviews, Reddit, and web
3. **Scientific Evidence** — validate ingredients with literature

## Data sources

| Dimension | Primary Tool | Backup Tool |
|---|---|---|
| Keyword Competition | sorftime MCP | — |
| Market Demand (Amazon) | sorftime MCP `product_reviews` | — |
| Market Demand (Reddit) | Apify MCP `parseforge/reddit-posts-scraper` | — |
| Market Demand (Web) | exa MCP `web_search_exa` | web search |
| Scientific Evidence | exa MCP `web_search_exa` | web search / web fetch |

## Output

A single deliverable: `{name}-formula-reconstruction.md` saved to `formula-reconstruction-result/{name}/`
