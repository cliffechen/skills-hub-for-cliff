# Web Signal Schema

`web_signal_analysis.json` 是 xCrawl 站外信号的结构化结果。它既可以作为独立工件保存，也可以映射进 `unified_payload.json` 的 `chapters.ch07_web_signal_intelligence`。

## 顶层结构

```json
{
  "ingredient": "Urolithin A",
  "data_date": "2026-06-16",
  "coverage": {},
  "search_results": [],
  "scraped_pages": [],
  "platform_summary": [],
  "demand_signals": [],
  "ingredient_feedback": [],
  "safety_signals": [],
  "brand_narratives": [],
  "trend_signals": [],
  "insight": ""
}
```

## coverage

```json
{
  "search_query_count": 6,
  "scraped_page_count": 12,
  "platforms": ["Google", "Reddit", "Brand Website"],
  "data_date": "2026-06-16"
}
```

## search_results

```json
{
  "query": "Urolithin A supplement review",
  "position": 1,
  "title": "Page title",
  "url": "https://example.com",
  "platform": "Google",
  "source_type": "search_result"
}
```

## scraped_pages

```json
{
  "url": "https://example.com",
  "platform": "Reddit",
  "title": "Thread title",
  "summary": "Short summary",
  "sentiment": "positive",
  "key_topics": ["energy", "mitochondria"],
  "source_query": "Urolithin A reddit supplement",
  "content_type": "discussion"
}
```

## platform_summary

```json
{
  "platform": "Reddit",
  "mention_count": 5,
  "sentiment_distribution": {
    "positive": 2,
    "neutral": 2,
    "negative": 1
  },
  "top_topics": ["energy", "price", "side effects"],
  "consumer_language": [
    "noticed better endurance",
    "too expensive to keep buying"
  ]
}
```

## demand_signals

```json
{
  "signal": "多处讨论将 Urolithin A 与线粒体健康、耐力恢复关联",
  "source_url": "https://example.com",
  "relevance": "验证功效方向中“能量/代谢”和“运动恢复”的需求真实性"
}
```

## ingredient_feedback

```json
{
  "type": "benefit",
  "feedback": "用户更常描述为能量、运动恢复、健康老化，而不是快速体感",
  "sentiment": "neutral-positive",
  "product_implication": "Listing 表达应偏长期健康与功能维持，避免即时强体感承诺",
  "source": "Reddit / brand FAQ / health article"
}
```

## safety_signals

```json
{
  "concern": "消费者会询问长期服用安全性、剂量与是否值得高价",
  "frequency": "medium",
  "source_platforms": ["Reddit", "Google"],
  "relevance": "需要在后续合规 Skill 中检查安全表达、剂量话术和引用证据"
}
```

## brand_narratives

```json
{
  "brand": "Timeline / Mitopure",
  "positioning": "premium clinically studied mitochondrial health ingredient",
  "source": "brand website",
  "implication": "新品牌不宜直接硬碰临床背书，应从透明配方、价格和剂型便利性切入"
}
```

## Excel 映射

| Sheet | 来源字段 |
|---|---|
| `Web情报_搜索结果` | `search_results[]` |
| `Web情报_抓取明细` | `scraped_pages[]` |
| `Web情报_综合洞察` | `platform_summary[]`、`demand_signals[]`、`safety_signals[]`、`brand_narratives[]` |

## 校验规则

- 如果 `metadata.data_sources` 包含 `xCrawl`，payload 必须包含 `ch07_web_signal_intelligence`
- 如果包含 `ch07_web_signal_intelligence`，Excel 必须包含 3 个 `Web情报_*` Sheet
- `platform_summary` 和 `insight` 不得为空
- 安全信号只作为风险提示，不作为合规结论
