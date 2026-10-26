"""readings/*.json → docs/ 정적 HTML (GitHub Pages).

페이지는 한 화면짜리 슬라이드들의 묶음이다. app.js 가 휠·스와이프·키 한 번에 한 장씩 넘긴다.
"""
from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path

from .art import intro_layers

ROOT = Path(__file__).resolve().parent.parent
READINGS = ROOT / "readings"
DOCS = ROOT / "docs"
ASSETS = Path(__file__).resolve().parent / "assets"

EL_CLASS = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water"}
EL_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}
ANIMS = ["rise", "stamp", "slide", "flip"]

FONTS = ("https://fonts.googleapis.com/css2?family=Nanum+Brush+Script&family=Gowun+Batang:wght@400;700"
         "&family=Noto+Serif+KR:wght@500;900&family=JetBrains+Mono:wght@400;600&display=swap")


def _head(title: str, desc: str, depth: int, noindex: bool) -> str:
    up = "../" * depth
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta name="theme-color" content="#f3e8d0">
{robots}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}assets/style.css">
<script src="{up}assets/app.js" defer></script>
</head>
<body class="deck">
<div class="petals" aria-hidden="true"></div>
"""


def _hero(kicker: str, title: str, title_sub: str, headline: str, seal: str, extra: str = "") -> str:
    return f"""<section class="slide hero" data-nav="표지">
  <div class="layers">{intro_layers()}</div>
  <div class="hero-text">
    <p class="kicker">{escape(kicker)}</p>
    <h1 class="name"><span class="ink">{escape(title)}</span><span class="name-sub">{escape(title_sub)}</span></h1>
    <p class="headline">{escape(headline)}</p>
    {extra}
  </div>
  <div class="seal" aria-hidden="true">{seal}</div>
  <button class="scroll-hint" data-go="next">넘겨서 운명을 열어보세요<span>↓</span></button>
</section>"""


class _Seq:
    """슬라이드 안 요소마다 등장 순서(--d)를 매긴다."""

    def __init__(self):
        self.n = 0

    def __call__(self) -> str:
        self.n += 1
        return f'style="--d:{self.n}"'


def _opt(tag: str, cls: str, text: str | None) -> str:
    if not text:
        return ""
    c = f' class="{cls}"' if cls else ""
    return f"<{tag}{c}>{escape(text)}</{tag}>"


def _pillars(chart: dict, d: _Seq) -> str:
    order = {"시주": 0, "일주": 1, "월주": 2, "년주": 3}
    cells = []
    for p in sorted(chart["pillars"], key=lambda p: order[p["label"]]):
        me = " me" if not p["stem_god"] else ""
        cells.append(f"""<div class="pillar a{me}" {d()}>
  <div class="plabel">{escape(p['label'])}</div>
  <div class="pgod">{escape(p['stem_god'] or '나')}</div>
  <div class="char {EL_CLASS[p['stem_element']]}">{p['hanja'][0]}</div>
  <div class="char {EL_CLASS[p['branch_element']]}">{p['hanja'][1]}</div>
  <div class="pgod">{escape(p['branch_god'])}</div>
</div>""")
    els = "".join(f'<span class="el-chip {EL_CLASS[e]}-bg">{e} {n}</span>' for e, n in chart["elements"].items())
    return f'<div class="pillars">{"".join(cells)}</div><div class="el-chips a" {d()}>{els}</div>'


def _section(i: int, s: dict, chart: dict) -> str:
    d = _Seq()
    anim = ANIMS[i % len(ANIMS)]
    parts = [f"""<header class="s-head a" {d()}>
  <span class="hj">{escape(s['hanja'])}</span>
  <div><p class="s-num">{i:02d} · {escape(s['nav'])}</p><h2>{escape(s['title'])}</h2>
  {f'<p class="s-sub">{escape(s["sub"])}</p>' if s.get('sub') else ''}</div>
</header>"""]

    if s["key"] == "chart":
        parts.append(_pillars(chart, d))
    if s.get("lead"):
        parts.append(f'<p class="lead a" {d()}>{escape(s["lead"])}</p>')
    if s.get("stats"):
        parts.append('<div class="stats">' + "".join(
            f'<div class="stat a" {d()}><span class="st-label">{escape(x["label"])}</span>'
            f'<span class="st-value">{escape(x["value"])}</span>{_opt("span", "st-sub", x.get("sub"))}</div>'
            for x in s["stats"]) + "</div>")
    if s.get("bars"):
        parts.append('<div class="fit">' + "".join(
            f'<div class="fit-row a" {d()}><span class="fit-label">{escape(x["label"])}{_opt("small", "", x.get("note"))}</span>'
            f'<span class="fit-track"><span class="fit-fill" style="--v:{int(x["value"])}%"></span></span>'
            f'<span class="fit-val">{int(x["value"])}%</span></div>'
            for x in s["bars"]) + "</div>")
    for t in s.get("paras") or []:
        parts.append(f'<p class="para a" {d()}>{escape(t)}</p>')
    if s.get("cards"):
        parts.append('<div class="cards">' + "".join(
            f'<div class="card a" {d()}>{_opt("span", "badge", x.get("badge"))}'
            f'<h3>{escape(x["title"])}</h3><p>{escape(x["body"])}</p></div>'
            for x in s["cards"]) + "</div>")
    if s.get("timeline"):
        n = len(s["timeline"])
        many = f' many" style="--rows:{(n + 1) // 2}' if n > 5 else ""
        parts.append(f'<ol class="timeline{many}">' + "".join(
            f'<li class="tl a{" now" if x.get("now") else ""}" {d()}><span class="tl-when">{escape(x["when"])}</span>'
            f'<div><h3>{escape(x["title"])}{_opt("span", "now-badge", "지금" if x.get("now") else None)}</h3>'
            f'<p>{escape(x["body"])}</p></div></li>'
            for x in s["timeline"]) + "</ol>")
    if s.get("chips"):
        parts.append(f'<div class="chips a" {d()}>' + "".join(f"<span>{escape(c)}</span>" for c in s["chips"]) + "</div>")
    if s.get("evidence"):
        parts.append(f'<div class="evidence a" {d()}><span class="ev-label">근거</span>'
                     + "".join(f"<span>{escape(e)}</span>" for e in s["evidence"]) + "</div>")

    return f"""<section class="slide" data-anim="{anim}" data-nav="{escape(s['nav'])}">
  <span class="wm" aria-hidden="true">{escape(s['hanja'])}</span>
  <div class="slide-inner">{''.join(parts)}</div>
</section>"""


def render_reading(data: dict) -> str:
    chart, r = data["chart"], data["reading"]
    gender = "남" if chart["gender"] == "M" else "여"
    notes = []
    if not chart["hour_known"]:
        notes.append("태어난 시간을 몰라 시주 없이 봤어요")
    if chart["near_term_boundary"]:
        notes.append("절입 시각과 가까워 월주가 달라질 수 있어요")
    born = escape(chart["birth"]) + (f" (음력 {escape(data['lunar'])})" if data.get("lunar") else "")
    meta = (f'<p class="meta">{born} · {gender}'
            + "".join(f" · ※ {escape(n)}" for n in notes) + "</p>")
    seal = f'<span class="seal-char">{chart["day_master"]}</span><span class="seal-sub">日干</span>'

    secs = r["sections"]
    body = "".join(_section(i + 1, s, chart) for i, s in enumerate(secs))
    closing = f"""<section class="slide closing" data-anim="rise" data-nav="끝">
  <span class="wm" aria-hidden="true">終</span>
  <div class="slide-inner">
    <p class="closing-text a" style="--d:1">{escape(r['closing'])}</p>
    <p class="a" style="--d:2"><button class="btn" data-go="0">처음부터 다시 보기</button></p>
    <footer class="a" style="--d:3">
      <p>AI 개발자가 봐주는 사주 · 재미로 보는 해석이며 중요한 결정의 근거가 아닙니다.</p>
      <p><a href="../">← 처음으로</a></p>
    </footer>
  </div>
</section>"""

    return (_head(f"{data['name']} 님의 사주", r["headline"], 1, True)
            + '<main class="track">'
            + _hero("AI 개발자가 봐주는 사주", data["name"], "님의 사주팔자", r["headline"], seal, meta)
            + body + closing + "</main>\n</body>\n</html>\n")


def render_index(site: dict) -> str:
    apply = site.get("apply_url") or ""
    button = (f'<a class="btn" href="{escape(apply)}" target="_blank" rel="noopener">사주 신청하기</a>'
              if apply else '<p class="meta">신청 링크 준비 중이에요.</p>')
    seal = '<span class="seal-char">命</span><span class="seal-sub">四柱</span>'
    secs = [
        {"key": "what", "hanja": "觀", "nav": "소개", "title": "이렇게 봐드려요", "sub": "20장의 풀이",
         "cards": [
             {"title": "성격 · 겉과 속", "body": "어떤 사람인지, 남들이 보는 나와 진짜 나"},
             {"title": "직업 · 재물", "body": "잘 맞는 직군과 적합도, 재물 그릇과 피크 시기"},
             {"title": "연애 · 결혼 · 자녀", "body": "연애 스타일, 결혼 시기, 자녀 수와 시기"},
             {"title": "대운 · 올해 · 개운법", "body": "10년 단위 로드맵과 운을 여는 습관"},
         ]},
        {"key": "why", "hanja": "證", "nav": "차별점", "title": "챗봇 사주와 다른 점", "sub": "계산은 코드로, 해석은 사람이",
         "cards": [
             {"title": "만세력 직접 계산", "body": "태양 황경으로 절기를, 출생지 경도로 시간을 보정해요."},
             {"title": "모든 해석에 근거", "body": "어느 글자에서 나온 말인지 장마다 보여드려요."},
         ]},
        {"key": "how", "hanja": "請", "nav": "신청", "title": "신청 방법", "sub": "세 단계",
         "timeline": [
             {"when": "1", "title": "정보 보내기", "body": "양력 생년월일, 태어난 시간(모르면 비워두세요), 성별, 닉네임"},
             {"when": "2", "title": "분석", "body": "개발자가 직접 계산하고 풀이를 다듬어요."},
             {"when": "3", "title": "결과 받기", "body": "나만 아는 링크로 결과 페이지를 받아요."},
         ]},
    ]
    body = "".join(_section(i + 1, s, {}) for i, s in enumerate(secs))
    return (_head(site["title"], site["description"], 0, False)
            + '<main class="track">'
            + _hero("AI 개발자가 봐주는 사주", "사주팔자", "만세력 계산부터 풀이까지", site["description"], seal, button)
            + body + "</main>\n</body>\n</html>\n")


def build() -> list[Path]:
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    DOCS.mkdir(exist_ok=True)
    (DOCS / "assets").mkdir(exist_ok=True)
    for f in ("style.css", "app.js"):
        shutil.copy(ASSETS / f, DOCS / "assets" / f)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "index.html").write_text(render_index(site), encoding="utf-8")

    out = []
    for f in sorted(READINGS.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        d = DOCS / data["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render_reading(data), encoding="utf-8")
        out.append(d / "index.html")
    return out
