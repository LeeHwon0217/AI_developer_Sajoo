"""점성술 페이지 (docs/<slug>/star/): 밤하늘 테마, 별자리 인트로, 호로스코프 휠."""
from __future__ import annotations

import math
from html import escape

from .astro import GLYPH, PLANET_GLYPH, SIGN_ELEMENT, SIGNS, SIGNS_EN
from .render import _section

FONTS = ("https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700"
         "&family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Nanum+Myeongjo:wght@400;700;800"
         "&family=Noto+Sans+Symbols+2&family=JetBrains+Mono:wght@400;600&display=swap")

# 황도 12궁 별자리 모양 (0~100 좌표, 선으로 잇는 별들). 실제 별 배치를 단순화한 장식용.
CONSTELLATION = {
    0: [[(10, 62), (40, 46), (62, 40), (72, 54)]],
    1: [[(18, 14), (42, 48), (50, 58), (58, 50), (82, 18)], [(50, 58), (47, 84)]],
    2: [[(22, 10), (26, 46), (30, 88)], [(48, 8), (52, 46), (56, 86)], [(26, 46), (52, 46)], [(22, 10), (48, 8)]],
    3: [[(50, 18), (50, 50), (24, 82)], [(50, 50), (78, 84)]],
    4: [[(32, 18), (22, 30), (25, 43), (36, 49), (47, 45)], [(36, 49), (42, 64), (76, 66), (86, 50), (62, 44), (47, 45)]],
    5: [[(8, 30), (28, 36), (45, 46), (60, 52), (82, 72)], [(45, 46), (52, 18)], [(60, 52), (64, 88)]],
    6: [[(50, 14), (24, 46), (76, 46), (50, 14)], [(24, 46), (20, 78)], [(76, 46), (82, 76)]],
    7: [[(8, 22), (18, 27), (25, 37), (31, 47), (41, 57), (56, 63), (70, 66), (80, 59), (86, 48)], [(8, 22), (6, 10)], [(8, 22), (16, 12)]],
    8: [[(20, 62), (35, 46), (50, 50), (56, 66), (40, 73), (20, 62)], [(50, 50), (62, 34), (76, 40)], [(56, 66), (72, 72)]],
    9: [[(10, 26), (32, 31), (56, 46), (86, 30), (72, 56), (40, 70), (10, 26)]],
    10: [[(8, 30), (24, 24), (40, 34), (52, 28)], [(40, 34), (46, 56), (34, 76)], [(46, 56), (62, 61), (76, 80), (92, 70)]],
    11: [[(6, 20), (16, 14), (24, 24), (16, 31), (6, 20)], [(16, 31), (40, 56), (60, 82)], [(60, 82), (76, 62), (90, 40)], [(90, 40), (95, 28), (84, 26), (90, 40)]],
}
EL_COLOR = {"불": "#e8a26a", "흙": "#a7c47e", "공기": "#a9c4ff", "물": "#7fb0e0"}
ASPECT_COLOR = {"삼분": "#8fb4ff", "육분": "#8fb4ff", "사각": "#ef8a73", "대립": "#ef8a73"}


def constellation_svg(sign: int) -> str:
    lines, stars = [], set()
    for poly in CONSTELLATION[sign]:
        pts = " ".join(f"{x},{y}" for x, y in poly)
        lines.append(f'<polyline points="{pts}" pathLength="100"/>')
        stars.update(poly)
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{1.6 if i % 3 else 2.2}" style="--i:{i}"/>' for i, (x, y) in enumerate(sorted(stars)))
    return (f'<svg class="constellation" viewBox="0 0 100 100" aria-hidden="true">'
            f'<g class="c-lines">{"".join(lines)}</g><g class="c-stars">{dots}</g></svg>')


def wheel_svg(ac: dict, d) -> str:
    asc = ac["asc"] if ac["asc"] is not None else 0.0

    def pos(lon: float, r: float) -> tuple[float, float]:
        phi = math.radians(180 + (lon - asc))
        return round(r * math.cos(phi), 2), round(-r * math.sin(phi), 2)

    def arc(l0: float, l1: float, r0: float, r1: float) -> str:
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pos(l0, r1), pos(l1, r1), pos(l1, r0), pos(l0, r0)
        return f"M{x0},{y0} A{r1},{r1} 0 0 0 {x1},{y1} L{x2},{y2} A{r0},{r0} 0 0 1 {x3},{y3} Z"

    parts = []
    for k in range(12):
        parts.append(f'<path class="seg" d="{arc(30 * k, 30 * k + 30, 212, 255)}" fill="{EL_COLOR[SIGN_ELEMENT[k]]}"/>')
        x0, y0 = pos(30 * k, 120)
        x1, y1 = pos(30 * k, 255)
        parts.append(f'<line class="cusp" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}"/>')
        gx, gy = pos(30 * k + 15, 233)
        parts.append(f'<text class="zg" x="{gx}" y="{gy}">{GLYPH[k]}</text>')
        if ac["asc_sign"] is not None:
            hx, hy = pos(30 * k + 15, 136)
            parts.append(f'<text class="hn" x="{hx}" y="{hy}">{(k - ac["asc_sign"]) % 12 + 1}</text>')
    if ac["asc"] is not None:
        for lon, label in ((ac["asc"], "ASC"), (ac["mc"], "MC")):
            x0, y0 = pos(lon, 120)
            x1, y1 = pos(lon, 268)
            lx, ly = pos(lon, 286)
            parts.append(f'<line class="axis" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}"/><text class="axl" x="{lx}" y="{ly}">{label}</text>')

    # 행성: 겹치지 않게 8° 이상 벌려 놓는다
    bodies = sorted(ac["bodies"], key=lambda b: b["lon"])
    shown = [b["lon"] for b in bodies]
    for _ in range(30):
        moved = False
        for i in range(len(shown)):
            j = (i + 1) % len(shown)
            gap = (shown[j] - shown[i]) % 360
            if gap < 8 and len(shown) > 1:
                shown[i] -= (8 - gap) / 2
                shown[j] += (8 - gap) / 2
                moved = True
        if not moved:
            break
    pt = {}
    for b, lon in zip(bodies, shown):
        tx0, ty0 = pos(b["lon"], 212)
        tx1, ty1 = pos(b["lon"], 202)
        px, py = pos(lon, 182)
        pt[b["name"]] = pos(b["lon"], 118)
        retro = '<tspan class="rx" dx="1">℞</tspan>' if b["retro"] else ""
        parts.append(f'<line class="tick" x1="{tx0}" y1="{ty0}" x2="{tx1}" y2="{ty1}"/>'
                     f'<text class="pg" x="{px}" y="{py}">{PLANET_GLYPH[b["name"]]}{retro}</text>')

    lines = []
    for i, a in enumerate(x for x in ac["aspects"] if x["type"] != "합"):
        (x0, y0), (x1, y1) = pt[a["a"]], pt[a["b"]]
        lines.append(f'<line class="asp" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{ASPECT_COLOR[a["type"]]}" style="--i:{i}" pathLength="100"/>')

    return (f'<div class="wheel-wrap a" {d()}><svg class="wheel" viewBox="-300 -300 600 600" role="img" aria-label="출생 차트 휠">'
            f'<circle class="ring" r="255"/><circle class="ring" r="212"/><circle class="ring inner" r="120"/>'
            f'<g class="aspects">{"".join(lines)}</g><g class="spin">{"".join(parts)}</g></svg></div>')


def _head(title: str, desc: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta name="theme-color" content="#060918">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../../assets/style.css">
<link rel="stylesheet" href="../../assets/astro.css">
<script src="../../assets/star.js" defer></script>
<script src="../../assets/app.js" defer></script>
</head>
<body class="deck astro">
<canvas id="sky" aria-hidden="true"></canvas>
"""


def render_astro(data: dict) -> str:
    ac, r = data["astro"], data["astro_reading"]
    sun = next(b for b in ac["bodies"] if b["name"] == "태양")
    born = escape(ac["birth"]) + (f" (음력 {escape(data['lunar'])})" if data.get("lunar") else "") + f" · {escape(ac['place'])}"
    hero = f"""<section class="slide hero" data-nav="표지">
  {constellation_svg(sun['sign'])}
  <div class="hero-text">
    <p class="kicker">ASTROLOGY · THE NATAL CHART</p>
    <h1 class="name"><span class="ink">{escape(data['name'])}</span><span class="name-sub">{SIGNS_EN[sun['sign']].upper()} · {escape(SIGNS[sun['sign']])}</span></h1>
    <p class="headline">{escape(r['headline'])}</p>
    <p class="meta">{born}</p>
  </div>
  <div class="seal" aria-hidden="true"><span class="seal-char">{GLYPH[sun['sign']]}</span></div>
  <button class="scroll-hint" data-go="next">별을 따라 내려가 보세요<span>↓</span></button>
</section>"""
    special = {"wheel": lambda d: wheel_svg(ac, d)}
    body = "".join(_section(i + 1, s, {}, special) for i, s in enumerate(r["sections"]))
    closing = f"""<section class="slide closing" data-anim="rise" data-nav="끝">
  <span class="wm" aria-hidden="true">✦</span>
  <div class="slide-inner">
    <p class="closing-text a" style="--d:1">{escape(r['closing'])}</p>
    <p class="a" style="--d:2"><button class="btn" data-go="0">처음부터 다시 보기</button> <a class="btn ghost" href="../">사주로도 보기 ☯</a></p>
    <footer class="a" style="--d:3">
      <p>AI 개발자가 봐주는 사주 · 별자리 · 재미로 보는 해석이며 중요한 결정의 근거가 아닙니다.</p>
    </footer>
  </div>
</section>"""
    return (_head(f"{data['name']} 님의 별자리", r["headline"]) + '<main class="track">'
            + hero + body + closing + "</main>\n</body>\n</html>\n")
