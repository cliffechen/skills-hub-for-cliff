# Agent exchange schemas

Preserve UTF-8 JSON, exact keyword spelling, and exact key coverage.

## Classification input and output

Read:

```text
<workspace>/reports/.exchange/llm_input.json
```

Write:

```json
{
  "ashwagandha gummies": {
    "label": "ingredient",
    "zh": "南非醉茄软糖"
  },
  "unrelated example": {
    "label": "unrelated",
    "zh": "无关示例"
  }
}
```

Rules:

1. Return exactly one object for every string in `keywords`.
2. Reuse every keyword as an unchanged JSON key.
3. Use only `ingredient`, `benefit`, `brand`, `condition`, `form`, or `unrelated`.
4. Provide a non-empty Chinese `zh` value for every keyword.
5. Mark ambiguous non-supplement retail terms as `unrelated`; do not force a supplement classification.

The script rejects missing keys, extra keys, invalid labels, non-object values, and empty translations before dictionary writeback.

## Analysis input and output

Read:

```text
<workspace>/reports/.exchange/analysis_input.json
```

Write:

```json
{
  "keyword_analysis": {
    "ashwagandha gummies": "ABA 排名……竞争与机会……风险……"
  },
  "tracks": [
    {
      "name": "压力与睡眠支持",
      "icon": "🌙",
      "keywords": ["ashwagandha gummies"],
      "summary": "该赛道本周由……驱动。"
    }
  ],
  "core_findings": [
    "本周最强的早期信号是……"
  ]
}
```

Rules:

1. Include every Tier 1 keyword exactly once in `keyword_analysis`.
2. Include every Tier 1 keyword exactly once across all `tracks[].keywords`.
3. Use non-empty `name`, `icon`, and `summary` strings for every track.
4. Use only non-empty strings in `core_findings`.
5. Base claims only on fields present in the input.
6. Lead with ABA rank direction. Treat volume, CPC, and extensions as supporting evidence.
7. Label missing data as unavailable; never infer a numeric value.

The renderer rejects missing, extra, duplicated, or unclustered Tier 1 keywords.
