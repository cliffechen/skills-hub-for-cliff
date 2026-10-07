"""Offline HTML for entry_check results: the card (tiny markdown renderer) + inline SVG charts."""
from __future__ import annotations

import html
import re


def _inline(s: str) -> str:
    s = html.escape(s, quote=False).replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>")
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def md(text: str) -> str:
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]
            out.append("<div class=tw><table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
                                                          for r in body) + "</tbody></table></div>")
            continue
        if ln.startswith("### "):
            out.append(f"<h2>{_inline(ln[4:])}</h2>")
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{_inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif ln.strip():
            out.append(f"<p>{_inline(ln)}</p>")
        i += 1
    return "\n".join(out)


def bars(item) -> str:
    rows = [t for t in item["table"] if not t["month"].startswith("<")] + [
        {**p, "post": True} for p in item.get("post_M", [])]
    if not rows:
        return ""
    W, H, pad = 640, 200, 28
    bw = (W - pad * 2) / len(rows)
    vmax = max(r["new"] for r in rows) or 1
    g = []
    for k, r in enumerate(rows):
        x = pad + k * bw
        h_all = (H - 50) * r["new"] / vmax
        h_win = (H - 50) * r["win"] / vmax
        cls = "post" if r.get("post") else "lose"
        g.append(f'<rect class="{cls}" x="{x + 2:.1f}" y="{H - 30 - h_all:.1f}" width="{bw - 4:.1f}" height="{h_all:.1f}"><title>{r["month"]}: {r["new"]} 新父体 / {r["win"]} 出单</title></rect>')
        g.append(f'<rect class="win" x="{x + 2:.1f}" y="{H - 30 - h_win:.1f}" width="{bw - 4:.1f}" height="{h_win:.1f}"/>')
        g.append(f'<text class="v" x="{x + bw / 2:.1f}" y="{H - 34 - h_all:.1f}">{r["new"]}</text>')
        g.append(f'<text class="m" x="{x + bw / 2:.1f}" y="{H - 14}">{r["month"][2:]}</text>')
    return (f'<figure><figcaption>逐月新父体（深色 = 月销 ≥{item["min_units"]}；浅灰 = 截止月之后）</figcaption>'
            f'<svg viewBox="0 0 {W} {H}" role="img">{"".join(g)}</svg></figure>')


def line(item) -> str:
    pts = [p for p in item["demand_series"] if p["month"] <= item["M"]][-24:]
    if len(pts) < 2:
        return ""
    W, H, pad = 640, 170, 30
    vmax = max(p["searches"] for p in pts) or 1
    xy = [(pad + k * (W - 2 * pad) / (len(pts) - 1), H - 28 - (H - 50) * p["searches"] / vmax) for k, p in enumerate(pts)]
    path = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(xy))
    lab = "".join(f'<text class="m" x="{x:.1f}" y="{H - 10}">{p["month"][2:]}</text>'
                  for k, ((x, _), p) in enumerate(zip(xy, pts)) if k % 3 == 0 or k == len(pts) - 1)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5"><title>{p["month"]}: {p["searches"]:,}</title></circle>'
                   for (x, y), p in zip(xy, pts))
    return (f'<figure><figcaption>需求词「{html.escape(item["demand_kw"])}」月搜索（最近 24 个月，峰值 {vmax:,}）</figcaption>'
            f'<svg viewBox="0 0 {W} {H}" role="img"><path class="ln" d="{path}"/>{dots}{lab}</svg></figure>')


CSS = """
:root{--bg:#fafaf9;--fg:#1c1917;--mut:#78716c;--line:#e7e5e4;--card:#fff;--win:#0f766e;--lose:#99f6e4;--post:#d6d3d1;--acc:#0f766e}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--line:#44403c;--card:#292524;--win:#2dd4bf;--lose:#115e59;--post:#57534e;--acc:#2dd4bf}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px}h2{margin:.2em 0 .4em;font-size:1.3em}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;margin:8px 0;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{color:var(--mut);font-weight:600}
code{background:var(--line);padding:0 4px;border-radius:4px}sub{color:var(--mut)}
figure{margin:8px 0}figcaption{color:var(--mut);font-size:13px}svg{width:100%;height:auto}
rect.win{fill:var(--win)}rect.lose{fill:var(--lose)}rect.post{fill:var(--post)}
text{fill:var(--mut);font-size:10px;text-anchor:middle}text.v{fill:var(--fg)}
path.ln{fill:none;stroke:var(--acc);stroke-width:2}circle{fill:var(--acc)}
.narr li{margin:.45em 0}summary{cursor:pointer;color:var(--mut);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
"""


def render(payload: dict, card_md: str, tables_md: str = "") -> str:
    charts = "".join(
        f'<section><h2>{html.escape(" / ".join(it["queries"]))} · {it["verdict"]}</h2>{bars(it)}{line(it)}</section>'
        for it in payload["items"])
    wrap = f'<div class="grid">{charts}</div>' if payload["mode"] == "compare" else charts
    return (f'<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>入场速判</title><style>{CSS}</style></head><body><main><section class="narr">{md(card_md)}</section>{wrap}'
            + (f'<section><details><summary>数据附录（逐月明细与指标表）</summary>{md(tables_md)}</details></section>' if tables_md else "")
            + '</main></body></html>')
