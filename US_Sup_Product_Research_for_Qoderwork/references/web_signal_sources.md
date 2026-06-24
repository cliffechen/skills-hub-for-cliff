# Web Signal Sources

本文件定义 xCrawl 站外网络信号采集策略。它用于补充 Sorftime 的 Amazon 站内数据，回答“消费者在站外怎么讨论这个成分”。

## 推荐搜索 Query

| 目的 | Query 模板 |
|---|---|
| 泛需求 | `{ingredient} supplement review` |
| 功效反馈 | `{ingredient} benefits` |
| 负面反馈 | `{ingredient} side effects` |
| 社区讨论 | `{ingredient} reddit supplement` |
| 竞品口碑 | `{ingredient} brand review` |
| 科研/可信内容 | `{ingredient} clinical trial` |
| 购买疑虑 | `is {ingredient} worth it` |
| 竞品叙事 | `{competitor_brand} {ingredient}` |

默认参数：

```json
{
  "location": "US",
  "language": "en",
  "limit": 5
}
```

## 来源优先级

| 优先级 | 来源类型 | 价值 |
|---|---|---|
| P1 | Reddit、专业论坛、用户问答 | 真实体验、顾虑、非购买者语言 |
| P1 | 竞品官网、品牌 FAQ | 竞品如何教育市场与构建信任 |
| P1 | Amazon/Walmart/Trustpilot 评论 | 购买后体验、差评痛点 |
| P2 | 健康媒体、专业博客、YouTube 文稿 | 市场叙事、趋势解释 |
| P2 | 科研摘要、机构页面 | 成分可信度与风险提示线索 |
| P3 | 新闻、泛内容页 | 热度与话题补充 |

## xCrawl 输出格式

单页抓取推荐：

```json
{
  "url": "https://example.com",
  "output": {
    "formats": ["markdown", "links", "summary", "json"]
  },
  "json": {
    "prompt": "Extract supplement consumer feedback, sentiment, benefits, side effects, brand positioning, and purchase objections from this page."
  }
}
```

需要人工检查页面渲染时，可额外加入：

```json
{
  "output": {
    "formats": ["markdown", "links", "summary", "screenshot"]
  }
}
```

## 去重规则

- 同一个 `final_url` 只保留一次
- 同一域名最多保留 3 个页面，竞品官网例外
- 搜索结果标题和摘要完全相似时，只保留排名更高的一条
- 低正文长度页面不进入最终洞察，但保留在 `web_signal_sources.json`

## 情绪分类

| 情绪 | 判定 |
|---|---|
| positive | 明确提到有效、复购、推荐、愿意付费、体验改善 |
| neutral | 科普、询问、对比、无明确使用结论 |
| negative | 明确提到无效、副作用、价格不值、退货、失望 |

## 风险标注规则

- 只写“风险信号”或“需另行评估”
- 不写医学诊断、治疗结论
- 与 FDA/FTC/专利/商标相关内容交给专用合规 Skill
