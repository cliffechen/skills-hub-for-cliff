#!/usr/bin/env python3
"""Build an offline-friendly HTML trend report from payload.json (structure: references/output-schema.md).

Usage: python build_html.py <payload.json> [<output.html>]
Default output: <meta.out_dir>/{topic}_趋势选品_v{version}_{YYYYMMDD}_{AM|PM}{hhmm}.html

Charts: inline SVG (no external scripts), one chart per series so differing sources/units are never merged.
Forecasts are shown as text cards only; no fabricated forecast line is drawn.
"""
import html
import json
import os
import re
import sys
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STAMP_RE = re.compile(r"_\d{8}_(AM|PM)\d{4}$")
TAIL = "本结论不含供给与利润判断。"
COLORS = ["#2a6fdb", "#e07b00", "#2e9e5b", "#b04ad0", "#c2410c"]


def stamp(now=None):
    now = now or datetime.now()
    return f"{now:%Y%m%d}_{'AM' if now.hour < 12 else 'PM'}{now.hour % 12 or 12:02d}{now:%M}"


def esc(x):
    return html.escape(str(x if x is not None else ""))


def fmt(v):
    if v is None:
        return ""
    a = abs(v)
    return f"{v/1e6:.1f}M" if a >= 1e6 else f"{v/1e3:.0f}k" if a >= 1e4 else f"{v:g}"


def svg_chart(s, color, marker_date=None):
    dates, vals = s.get("dates", []), s.get("values", [])
    pts = [(i, v) for i, v in enumerate(vals) if v is not None]
    if len(pts) < 2:
        return "<p class='muted'>序列点数不足，无法绘图。</p>"
    W, H, L, R, T, B = 640, 190, 52, 12, 14, 28
    ys = [v for _, v in pts]
    lo, hi = min(0, min(ys)), max(ys)
    hi = hi if hi > lo else lo + 1
    n = max(len(vals) - 1, 1)
    X = lambda i: L + (W - L - R) * i / n
    Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    path = " ".join(("M" if k == 0 or pts[k - 1][0] != i - 1 else "L") + f"{X(i):.1f},{Y(v):.1f}" for k, (i, v) in enumerate(pts))
    grid = "".join(
        f"<line x1='{L}' x2='{W-R}' y1='{Y(lo+(hi-lo)*t):.1f}' y2='{Y(lo+(hi-lo)*t):.1f}' class='grid'/>"
        f"<text x='{L-6}' y='{Y(lo+(hi-lo)*t)+4:.1f}' class='ax' text-anchor='end'>{fmt(lo+(hi-lo)*t)}</text>"
        for t in (0, 0.5, 1))
    step = max(1, len(dates) // 6)
    xl = "".join(f"<text x='{X(i):.1f}' y='{H-8}' class='ax' text-anchor='middle'>{esc(dates[i])}</text>"
                 for i in range(0, len(dates), step))
    mark = ""
    if marker_date and marker_date in dates:
        mx = X(dates.index(marker_date))
        mark = f"<line x1='{mx:.1f}' x2='{mx:.1f}' y1='{T}' y2='{H-B}' class='mark'/>"
    last = pts[-1]
    dot = f"<circle cx='{X(last[0]):.1f}' cy='{Y(last[1]):.1f}' r='3.5' fill='{color}'/>"
    return (f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='{esc(s.get('name'))}'>{grid}{xl}{mark}"
            f"<path d='{path}' fill='none' stroke='{color}' stroke-width='2'/>{dot}</svg>")


def ul(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>" if items else "<p class='muted'>—</p>"


def card(c, meta):
    f = c.get("forecast", {})
    sc = f.get("scenarios", {})
    charts = ""
    for k, s in enumerate(c.get("series", [])):
        charts += (f"<figure><figcaption>{esc(s.get('name'))} · {esc(s.get('source'))} · {esc(s.get('granularity'))}"
                   f" · <b>{esc(s.get('tag'))}</b></figcaption>{svg_chart(s, COLORS[k % len(COLORS)], meta.get('forecast_target_date'))}</figure>")
    flags = "".join(f"<span class='flag'>{esc(x.get('type'))}：{esc(x.get('text'))}</span>" for x in c.get("flags", []))
    verdict = esc(c.get("verdict"))
    return f"""
<section class="card" id="{esc(c.get('id'))}">
  <header>
    <h2>{esc(c.get('keyword'))} <small>{esc(c.get('zh'))}</small></h2>
    <span class="pill v-{verdict}">{verdict}</span><span class="pill">{esc(c.get('archetype'))}</span>
  </header>
  <p>{esc(c.get('verdict_reason'))}</p>
  <div class="grid2">
    <div><h3>趋势序列</h3>{charts or "<p class='muted'>无序列数据</p>"}</div>
    <div>
      <h3>预测（定性）</h3>
      <p><b>{esc(f.get('direction'))} · {esc(f.get('stage'))}</b>　置信度 <b>{esc(f.get('confidence'))}</b>
         <span class="muted">（{esc(f.get('confidence_basis'))}）</span></p>
      <p>{esc(f.get('target_position'))}　距峰 {esc(f.get('weeks_to_peak'))} 周 <span class="muted">{esc(f.get('peak_basis'))}</span></p>
      <table class="sc"><tr><th>保守</th><td>{esc(sc.get('conservative'))}</td></tr>
      <tr><th>基准</th><td>{esc(sc.get('base'))}</td></tr>
      <tr><th>乐观</th><td>{esc(sc.get('optimistic'))}</td></tr></table>
      <h4>证实信号</h4>{ul(f.get('confirm', []))}
      <h4>证伪信号</h4>{ul(f.get('refute', []))}
      <p class="muted">{TAIL}</p>
    </div>
  </div>
  <details><summary>需求真实性 / 趋势诊断 / 进入窗口 / 需求缺口</summary>
    <p><b>需求真实性：</b>{esc(c.get('demand'))}</p><p><b>趋势诊断：</b>{esc(c.get('trend'))}</p>
    <p><b>进入窗口：</b>{esc(c.get('window'))}</p><p><b>需求缺口：</b>{esc(c.get('gap'))}</p>
    {('<p><b>UNKNOWN：</b>' + esc('；'.join(c.get('unknowns', []))) + '</p>') if c.get('unknowns') else ''}
  </details>
  {('<div class="flags">' + flags + '</div>') if flags else ''}
</section>"""


CSS = """
:root{--bg:#fff;--fg:#1b1f24;--muted:#6b7280;--line:#e5e7eb;--card:#f8fafc;--pill:#eef2f7;--flag:#fff3cd;--flagfg:#7a5a00}
@media(prefers-color-scheme:dark){:root{--bg:#14171c;--fg:#e6e8eb;--muted:#9aa3ad;--line:#2b313a;--card:#1b2027;--pill:#262d36;--flag:#3b3210;--flagfg:#f1d27a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,Segoe UI,Arial,sans-serif;padding:16px;max-width:1180px;margin:auto}
h1{font-size:22px;margin:8px 0}h2{font-size:18px;margin:0}h2 small{color:var(--muted);font-weight:400;font-size:13px}h3{font-size:14px;margin:10px 0 6px}h4{font-size:13px;margin:8px 0 2px}
.muted{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:14px 0}
.card header{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.pill{background:var(--pill);border-radius:99px;padding:1px 10px;font-size:12px}
.v-推荐{background:#cfe8d6;color:#14532d}.v-观察{background:#fde9a8;color:#6b4e00}.v-放弃{background:#f4c7cb;color:#7f1d1d}
.grid2{display:grid;grid-template-columns:1.2fr 1fr;gap:18px}@media(max-width:820px){.grid2{grid-template-columns:1fr}}
figure{margin:0 0 10px}figcaption{font-size:12px;color:var(--muted)}svg{width:100%;height:auto}
.grid{stroke:var(--line)}.ax{fill:var(--muted);font-size:10px}.mark{stroke:#c2410c;stroke-dasharray:4 3}
table.sc{border-collapse:collapse;width:100%}table.sc th{width:52px;text-align:left;vertical-align:top;color:var(--muted)}table.sc td,table.sc th{padding:3px 4px;border-top:1px solid var(--line)}
ul{margin:2px 0 6px 18px;padding:0}.flag{display:inline-block;background:var(--flag);color:var(--flagfg);border-radius:6px;padding:2px 8px;margin:4px 6px 0 0;font-size:12px}
table.ov{border-collapse:collapse;width:100%}table.ov th,table.ov td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
details{margin-top:8px}summary{cursor:pointer;color:var(--muted)}.note{font-size:12px;color:var(--muted)}
"""


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    meta, cands = data.get("meta", {}), data.get("candidates", [])
    topic = meta.get("topic", "趋势选品")
    safe = re.sub(r'[\\/:*?"<>|]', "_", topic)
    if not out:
        out = os.path.join(meta.get("out_dir", "."), f"{safe if '趋势选品' in safe else safe + '_趋势选品'}_v{meta.get('version', 1)}.html")
    root, ext = os.path.splitext(out)
    if not STAMP_RE.search(root):
        out = f"{root}_{stamp()}{ext or '.html'}"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    ov = "".join(
        f"<tr><td><a href='#{esc(c.get('id'))}'>{esc(c.get('keyword'))}</a></td><td>{esc(c.get('archetype'))}</td>"
        f"<td>{esc(c.get('forecast', {}).get('direction'))} / {esc(c.get('forecast', {}).get('stage'))}</td>"
        f"<td>{esc(c.get('forecast', {}).get('confidence'))}</td><td><span class='pill v-{esc(c.get('verdict'))}'>{esc(c.get('verdict'))}</span></td>"
        f"<td>{esc(c.get('verdict_reason'))}</td></tr>" for c in cands)
    wl = "".join(f"<tr><td>{esc(w.get('candidate'))}</td><td>{esc(w.get('what'))}</td><td>{esc(w.get('when'))}</td><td>{esc(w.get('trigger'))}</td></tr>"
                 for w in data.get("watchlist", []))
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(topic)} 趋势选品</title><style>{CSS}</style></head><body>
<h1>{esc(topic)}</h1>
<p class="note">站点 {esc(meta.get('marketplace'))} · 数据截至 {esc(meta.get('as_of'))} · 预测时点 {esc(meta.get('forecast_target_date'))}（虚线）· 入口 {esc(meta.get('entry'))}<br>
阈值：{esc(meta.get('thresholds'))}（可调起点）。只看需求端趋势，{TAIL}预测为定性判断；红旗仅提示。</p>
<table class="ov"><tr><th>关键词</th><th>原型</th><th>预测</th><th>置信度</th><th>结论</th><th>理由</th></tr>{ov}</table>
{''.join(card(c, meta) for c in cands)}
<h2>监测清单</h2>
<table class="ov"><tr><th>候选</th><th>复查什么</th><th>何时</th><th>触发条件</th></tr>{wl}</table>
{('<p class="note"><b>数据缺口/降级：</b>' + esc('；'.join(meta.get('unknowns', []))) + '</p>') if meta.get('unknowns') else ''}
</body></html>"""
    open(out, "w", encoding="utf-8").write(page)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
