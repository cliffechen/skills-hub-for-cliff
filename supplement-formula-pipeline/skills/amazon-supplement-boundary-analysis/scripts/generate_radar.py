#!/usr/bin/env python
"""Generate self-contained radar chart HTML and PNG from a score JSON file."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_COLORS = ["#e76f51", "#2a9d8f", "#f4a261", "#457b9d", "#8d5a97"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scores_json", help="Radar score JSON file.")
    parser.add_argument("--output-dir", required=True, help="Directory for outputs.")
    parser.add_argument("--name", default="radar-chart", help="Output file prefix.")
    return parser.parse_args()


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend([r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"])
    candidates.extend(
        [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]
    )
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def render_png(data: dict, output: Path) -> None:
    axes = data["axes"]
    series = data["series"]
    weights = data.get("weights", [0.25, 0.20, 0.15, 0.15, 0.15, 0.10])
    display_axes = [
        re.sub(r'\s*\(\d+%\)\s*$', '', label).strip() + f" ({int(w * 100)}%)"
        for label, w in zip(axes, weights)
    ]
    width, height = 1500, 1050
    image = Image.new("RGB", (width, height), "#f6f2ea")
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, True)
    subtitle_font = load_font(22)
    label_font = load_font(22, True)
    small_font = load_font(18)
    legend_font = load_font(22)
    score_font = load_font(18, True)

    draw.ellipse([-220, -260, 520, 430], fill="#e8f1ed")
    draw.ellipse([1060, 720, 1710, 1300], fill="#f8ded1")
    draw.rounded_rectangle([52, 50, width - 52, height - 52], radius=34, fill="#fffaf1", outline="#ded4c3", width=2)
    draw.text((96, 86), data.get("title", "成分与流量边界雷达图"), font=title_font, fill="#20302d")
    draw.text((98, 144), data.get("subtitle", "评分范围 0-10。"), font=subtitle_font, fill="#66746f")

    center_x, center_y, radius = 540, 568, 292
    angles = [-math.pi / 2 + 2 * math.pi * index / len(axes) for index in range(len(axes))]

    def point(score: float, angle: float) -> tuple[float, float]:
        return (center_x + math.cos(angle) * radius * score / 10, center_y + math.sin(angle) * radius * score / 10)

    for level in range(2, 11, 2):
        points = [point(level, angle) for angle in angles]
        draw.polygon(points, outline="#d4cbc0")
        draw.text((center_x + 8, center_y - radius * level / 10 - 8), str(level), font=small_font, fill="#9b9288")

    for angle, label in zip(angles, display_axes):
        x, y = point(10, angle)
        draw.line([center_x, center_y, x, y], fill="#d6cec4", width=2)
        lx = center_x + math.cos(angle) * (radius + 70)
        ly = center_y + math.sin(angle) * (radius + 58)
        bbox = draw.textbbox((0, 0), label, font=label_font)
        draw.text((lx - (bbox[2] - bbox[0]) / 2, ly - (bbox[3] - bbox[1]) / 2), label, font=label_font, fill="#243733")

    overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for index, item in enumerate(series):
        color = item.get("color", DEFAULT_COLORS[index % len(DEFAULT_COLORS)])
        rgb = hex_to_rgb(color)
        points = [point(score, angle) for score, angle in zip(item["scores"], angles)]
        overlay_draw.polygon(points, fill=rgb + (42,), outline=rgb + (230,))
        overlay_draw.line(points + [points[0]], fill=rgb + (255,), width=4)
        for score_index, (x, y) in enumerate(points):
            overlay_draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=rgb + (255,), outline=(255, 255, 255, 255), width=2)
            tx = x + math.cos(angles[score_index]) * 18
            ty = y + math.sin(angles[score_index]) * 18
            overlay_draw.text((tx - 8, ty - 10), str(item["scores"][score_index]), font=score_font, fill=rgb + (255,))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle([965, 220, 1408, 810], radius=28, fill="#ffffff", outline="#e1d8cb", width=2)
    draw.text((1010, 252), "方案图例", font=load_font(28, True), fill="#20302d")
    for index, item in enumerate(series):
        y = 276 + 58 * index
        color = item.get("color", DEFAULT_COLORS[index % len(DEFAULT_COLORS)])
        draw.rounded_rectangle([1010, y, 1054, y + 22], radius=8, fill=color)
        draw.text((1070, y - 5), item["name"], font=legend_font, fill="#293936")

    draw.text((1010, 485), "快速判断", font=load_font(28, True), fill="#20302d")
    for index, note in enumerate(data.get("notes", [])[:4]):
        draw.text((1010, 535 + 58 * index), note, font=small_font, fill="#5f6b67")

    wt_y = 535 + 58 * min(len(data.get("notes", [])), 4) + 20
    draw.text((1010, wt_y), "加权总分", font=load_font(28, True), fill="#20302d")
    for index, item in enumerate(series):
        wt = sum(s * w for s, w in zip(item["scores"], weights))
        draw.text((1010, wt_y + 40 + 30 * index), f"{item['name']}: {wt:.2f}", font=small_font, fill="#5f6b67")

    footer = data.get("footer", "数据源：Sif Excel + Sorftime MCP + Exa/Apify 轻度站外交叉验证。")
    draw.text((96, 950), footer, font=small_font, fill="#7a7168")
    image.save(output, quality=95)


def render_html(data: dict, output: Path) -> None:
    axes = data["axes"]
    series = data["series"]
    weights = data.get("weights", [0.25, 0.20, 0.15, 0.15, 0.15, 0.10])
    display_axes = [
        re.sub(r'\s*\(\d+%\)\s*$', '', label).strip() + f" ({int(w * 100)}%)"
        for label, w in zip(axes, weights)
    ]
    center_x, center_y, radius = 460, 380, 260
    angles = [-math.pi / 2 + 2 * math.pi * index / len(axes) for index in range(len(axes))]

    def point(score: float, angle: float) -> tuple[float, float]:
        return (center_x + math.cos(angle) * radius * score / 10, center_y + math.sin(angle) * radius * score / 10)

    def points_attr(points: list[tuple[float, float]]) -> str:
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    grid = []
    for level in range(2, 11, 2):
        grid.append(f'<polygon points="{points_attr([point(level, angle) for angle in angles])}" fill="none" stroke="#d8cec1" stroke-width="1.2"/>')
        grid.append(f'<text x="{center_x + 9}" y="{center_y - radius * level / 10 + 5}" class="tick">{level}</text>')
    for angle, label in zip(angles, display_axes):
        x, y = point(10, angle)
        lx = center_x + math.cos(angle) * (radius + 86)
        ly = center_y + math.sin(angle) * (radius + 56)
        grid.append(f'<line x1="{center_x}" y1="{center_y}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d8cec1" stroke-width="1.2"/>')
        grid.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" class="axis-label">{label}</text>')

    polygons = []
    for index, item in enumerate(series):
        color = item.get("color", DEFAULT_COLORS[index % len(DEFAULT_COLORS)])
        points = [point(score, angle) for score, angle in zip(item["scores"], angles)]
        polygons.append(f'<polygon points="{points_attr(points)}" fill="{color}22" stroke="{color}" stroke-width="3"/>')
        for score_index, (x, y) in enumerate(points):
            tx = x + math.cos(angles[score_index]) * 22
            ty = y + math.sin(angles[score_index]) * 22
            polygons.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{color}" stroke="#fffaf1" stroke-width="2"/>')
            polygons.append(f'<text x="{tx:.1f}" y="{ty:.1f}" class="score" fill="{color}" text-anchor="middle" dominant-baseline="middle">{item["scores"][score_index]}</text>')

    legend = "\n".join(
        f'<div class="legend-item"><span style="background:{item.get("color", DEFAULT_COLORS[index % len(DEFAULT_COLORS)])}"></span>{item["name"]}</div>'
        for index, item in enumerate(series)
    )
    notes = "\n".join(f"<li>{note}</li>" for note in data.get("notes", []))
    rows = "\n".join(
        "<tr><td>{axis}</td>{cells}</tr>".format(
            axis=axis,
            cells="".join(f"<td>{item['scores'][index]}</td>" for item in series),
        )
        for index, axis in enumerate(axes)
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{data.get('title', '成分与流量边界雷达图')}</title>
  <style>
    body {{ margin:0; min-height:100vh; background:#f6f2ea; color:#20302d; font-family:"Aptos","Microsoft YaHei","Noto Sans SC",sans-serif; }}
    main {{ width:min(1180px, calc(100vw - 32px)); margin:36px auto; padding:38px; border:1px solid #ded4c3; border-radius:32px; background:#fffaf1; }}
    h1 {{ margin:0 0 10px; font-size:42px; letter-spacing:-.04em; }}
    .subtitle {{ margin:0; color:#66746f; line-height:1.7; }}
    .layout {{ display:grid; grid-template-columns:minmax(0,1fr) 320px; gap:28px; align-items:center; margin-top:28px; }}
    .chart,.card,table {{ background:#fffdf8; border:1px solid #ded4c3; border-radius:24px; }}
    svg {{ width:100%; height:auto; display:block; }}
    .axis-label {{ font-size:19px; font-weight:700; fill:#243733; }}
    .tick {{ font-size:13px; fill:#998f83; }}
    .score {{ font-size:13px; font-weight:800; }}
    .card {{ padding:22px; margin-bottom:18px; }}
    .legend-item {{ display:grid; grid-template-columns:34px 1fr; gap:10px; align-items:center; margin:12px 0; color:#66746f; }}
    .legend-item span {{ height:14px; border-radius:999px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:28px; overflow:hidden; }}
    th,td {{ padding:14px 16px; border-bottom:1px solid #eee4d7; text-align:center; }}
    th:first-child,td:first-child {{ text-align:left; }}
    th {{ background:#f1eadf; }}
    @media (max-width:920px) {{ main {{ padding:24px; }} .layout {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <main>
    <h1>{data.get('title', '成分与流量边界雷达图')}</h1>
    <p class="subtitle">{data.get('subtitle', '评分范围 0-10。')} 当前推荐：{data.get('recommended', '')}</p>
    <p class="subtitle" style="margin-top:4px;font-size:14px;color:#8a8279;">权重: 锚定度25% | 闭环度20% | 延伸力15% | 合理性15% | 合规15% | 差异化10%</p>
    <section class="layout">
      <div class="chart"><svg viewBox="0 0 980 780">{''.join(grid)}{''.join(polygons)}</svg></div>
      <aside><div class="card"><h2>方案图例</h2>{legend}</div><div class="card"><h2>快速判断</h2><ul>{notes}</ul></div></aside>
    </section>
    <table><thead><tr><th>评分维度</th>{''.join(f'<th>{item["name"]}</th>' for item in series)}</tr></thead><tbody>{rows}</tbody></table>
    <table><thead><tr><th>加权总分</th>{''.join(f'<th>{item["name"]}</th>' for item in series)}</tr></thead><tbody><tr><td>Σ(得分×权重)</td>{''.join(f'<td><strong>{sum(s * w for s, w in zip(item["scores"], weights)):.2f}</strong></td>' for item in series)}</tr></tbody></table>
  </main>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    data = json.loads(Path(args.scores_json).read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{args.name}.png"
    html_path = output_dir / f"{args.name}.html"
    render_png(data, png_path)
    render_html(data, html_path)
    print(json.dumps({"png": str(png_path), "html": str(html_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
