# payload JSON 结构（scan_flags / build_xlsx / build_html 共用）

```json
{
  "meta": {
    "topic": "补剂趋势选品-US",
    "marketplace": "US",
    "as_of": "2026-10-07",
    "forecast_horizon_months": 5,
    "forecast_target_date": "2027-03",
    "entry": "A 趋势扫描",
    "version": 1,
    "out_dir": ".",
    "thresholds": "近3月增长≥30%，月搜索量≥5000（可调起点）",
    "tools_used": ["sellersprite.aba_research_monthly", "sif.market_get_keyword_history"],
    "unknowns": ["sorftime category_trend 未返回 2024 年数据"]
  },
  "candidates": [
    {
      "id": "C01",
      "keyword": "magnesium glycinate",
      "zh": "甘氨酸镁",
      "entry": "B",
      "archetype": "结构性增长",
      "demand": "需求真实性结论（精准词、需求结构）",
      "trend": "趋势诊断结论（含各源方向）",
      "window": "进入窗口结论（需求流向）",
      "gap": "需求缺口（需求句）",
      "forecast": {
        "direction": "上升",
        "stage": "上升中期",
        "target_position": "到 2027-03 预计处于…",
        "weeks_to_peak": 12,
        "peak_basis": "2024、2025 同在 1 月起峰",
        "scenarios": {"conservative": "…", "base": "…", "optimistic": "…"},
        "confidence": "中",
        "confidence_basis": "2 个独立源同向，历史 30 个月",
        "confirm": ["SIF 周搜索量连续 4 周同比为正"],
        "refute": ["Google 趋势转平且站内环比转负"]
      },
      "verdict": "推荐",
      "verdict_reason": "…",
      "unknowns": [],
      "flags": [],
      "series": [
        {"name": "ABA 月搜索量", "source": "sif.market_get_keyword_history", "granularity": "month",
         "unit": "searches", "tag": "ESTIMATE", "dates": ["2025-01", "2025-02"], "values": [120000, 130000]}
      ],
      "evidence": [
        {"tool": "sif.market_get_keyword_demand", "params": "keywords=[…], country=US",
         "data_period": "2023-01~2026-09", "tag": "FACT", "finding": "诊断：健康增长，动量：稳定"}
      ]
    }
  ],
  "watchlist": [
    {"candidate": "C01", "what": "SIF 周搜索量同比", "when": "每月第一周", "trigger": "连续 2 周同比转负 → 降为观察"}
  ]
}
```

约定：
- `verdict` ∈ 推荐 / 观察 / 放弃；`archetype` 用 trend-reading 的 7 类名称。
- `series.dates` 与 `values` 等长；不同源的序列分开列，不合并。缺失值用 `null`。
- `flags` 由 scan_flags.py 写入，元素 `{"type": "功效-疾病|品牌词|…", "text": "命中词与说明"}`。
- 没有该项信息写空字符串，不要编造。
