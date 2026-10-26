"""readings/*.json → docs/ 정적 HTML (GitHub Pages)."""
from __future__ import annotations

import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

from .art import intro_layers

ROOT = Path(__file__).resolve().parent.parent
READINGS = ROOT / "readings"
DOCS = ROOT / "docs"
ASSETS = Path(__file__).resolve().parent / "assets"

EL_CLASS = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water"}
EL_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}
EL_SKILL = {"木": "성장 · 학습", "火": "표현 · 출시", "土": "안정 · 운영", "金": "규칙 · 품질", "水": "지식 · 리서치"}
GROUP_HANJA = {"비겁": "比劫", "식상": "食傷", "재성": "財星", "관성": "官星", "인성": "印星"}
NUMERALS = "壹貳參肆伍陸"

FONTS = ("https://fonts.googleapis.com/css2?family=Nanum+Brush+Script&family=Gowun+Batang:wght@400;700"
         "&family=Noto+Serif+KR:wght@500;900&family=JetBrains+Mono:wght@400;600&display=swap")

BRUSH_LINE = ('<svg class="brush" viewBox="0 0 300 16" preserveAspectRatio="none" aria-hidden="true">'
              '<path d="M4 10 C 60 4 120 13 180 8 S 270 6 296 9" /></svg>')


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
<body>
<div class="petals" aria-hidden="true"></div>
"""


def _title(i: int, name: str, sub: str) -> str:
    return (f'<h2 class="sec-title reveal"><span class="hj">{NUMERALS[i]}</span>'
            f'<span class="t">{escape(name)}</span><small>{escape(sub)}</small>{BRUSH_LINE}</h2>')


def _hero(kicker: str, title: str, title_sub: str, headline: str, seal: str, extra: str = "") -> str:
    return f"""<header class="hero">
  <div class="layers">{intro_layers()}</div>
  <div class="hero-text">
    <p class="kicker">{escape(kicker)}</p>
    <h1 class="name"><span class="ink">{escape(title)}</span><span class="name-sub">{escape(title_sub)}</span></h1>
    <p class="headline">{escape(headline)}</p>
    {extra}
  </div>
  <div class="seal" aria-hidden="true">{seal}</div>
  <a class="scroll-hint" href="#start">스크롤을 내려 운명을 열어보세요<span>↓</span></a>
</header>"""


def _pillar(p: dict, i: int) -> str:
    s_el, b_el = p["stem_element"], p["branch_element"]
    top = p["stem_god"] or "나 (일간)"
    me = " me" if not p["stem_god"] else ""
    return f"""<div class="pillar stamp{me}" style="--i:{i}">
  <div class="plabel">{escape(p['label'])}</div>
  <div class="pgod">{escape(top)}</div>
  <div class="char {EL_CLASS[s_el]}">{p['hanja'][0]}</div>
  <div class="ko">{p['hangul'][0]} · {EL_KO[s_el]}</div>
  <div class="char {EL_CLASS[b_el]}">{p['hanja'][1]}</div>
  <div class="ko">{p['hangul'][1]} · {EL_KO[b_el]}</div>
  <div class="pgod">{escape(p['branch_god'])}</div>
</div>"""


def _bars(elements: dict[str, int]) -> str:
    total = sum(elements.values()) or 1
    rows = []
    for i, (el, n) in enumerate(elements.items()):
        status = "부족" if n == 0 else ("과다" if n >= 3 else "적정")
        cls = {"부족": "missing", "과다": "high", "적정": "ok"}[status]
        rows.append(f"""<div class="el-row reveal" style="--i:{i}; --v:{n / total * 100:.0f}%">
  <span class="el-hj {EL_CLASS[el]}">{el}</span>
  <span class="el-name">{EL_KO[el]} <small>{EL_SKILL[el]}</small></span>
  <span class="el-track"><span class="el-fill {EL_CLASS[el]}-bg"></span></span>
  <span class="el-val">{n}<em class="st-{cls}">{status}</em></span>
</div>""")
    return "\n".join(rows)


def _lint(items: list[str], seal: str, cls: str) -> str:
    return "\n".join(
        f'<li class="lint-item {cls} reveal"><span class="mini-seal">{seal}</span><p>{escape(t)}</p></li>'
        for t in items
    )


def render_reading(data: dict) -> str:
    chart, r = data["chart"], data["reading"]
    order = {"시주": 0, "일주": 1, "월주": 2, "년주": 3}
    pillars = sorted(chart["pillars"], key=lambda p: order[p["label"]])
    gender = "남" if chart["gender"] == "M" else "여"
    today = date.today()
    age = today.year - int(chart["birth"][:4]) + 1  # 대운수는 세는나이 기준

    notes = []
    if not chart["hour_known"]:
        notes.append("태어난 시간을 몰라 시주 없이 세 기둥으로 봤어요.")
    if chart["near_term_boundary"]:
        notes.append("절기가 바뀌는 시각과 아주 가까워 월주가 달라질 수 있어요.")
    note_html = "".join(f'<p class="notice reveal">※ {escape(n)}</p>' for n in notes)

    main_group = max(chart["groups"], key=chart["groups"].get)

    road = []
    for i, x in enumerate(r["roadmap"]):
        start = int(x["version"].lstrip("v"))
        now = start <= age < start + 10
        badge = '<span class="now">지금 여기</span>' if now else ""
        road.append(f"""<li class="road-item reveal{' current' if now else ''}" style="--i:{i}">
  <div class="road-age">{start}<small>세</small></div>
  <div class="road-body">
    <h3><span class="ganji">{escape(x['pillar'])}</span><span class="tag">{escape(x['version'])}</span>{badge}</h3>
    <p>{escape(x['note'])}</p>
  </div>
</li>""")

    releases = "\n".join(f"""<article class="release flip reveal{' this-year' if x['year'] == today.year else ''}" style="--i:{i}">
  <span class="wm">{escape(x['pillar'][:2])}</span>
  <h3><span class="year">{x['year']}</span> {escape(x['pillar'])}</h3>
  <p>{escape(x['note'])}</p>
</article>""" for i, x in enumerate(r["releases"]))

    meta = f'<p class="meta">{escape(chart["birth"])} · {gender} · 보정 지방시 {escape(chart["corrected_local"])}</p>'
    seal = f'<span class="seal-char">{chart["day_master"]}</span><span class="seal-sub">日干</span>'

    return _head(f"{data['name']} 님의 개발자 사주", r["headline"], 1, True) + _hero(
        "AI 개발자가 봐주는 사주", data["name"], "님의 사주팔자", r["headline"], seal, meta
    ) + f"""
<main class="paper" id="start">
  {note_html}
  <section>
    {_title(0, "시스템 스펙", "사주 원국 여덟 글자")}
    <div class="pillars">{''.join(_pillar(p, i) for i, p in enumerate(pillars))}</div>
    <p class="lead reveal">{escape(r['summary'])}</p>
  </section>

  <section>
    {_title(1, "리소스 모니터", "오행 분포")}
    <div class="panel elements">{_bars(chart['elements'])}</div>
  </section>

  <section>
    {_title(2, "워크 스타일", "십성")}
    <div class="panel style-card reveal">
      <span class="wm big">{GROUP_HANJA[main_group]}</span>
      <h3>{escape(r['work_style']['title'])}</h3>
      <p>{escape(r['work_style']['body'])}</p>
    </div>
  </section>

  <section>
    {_title(3, "린트 결과", "길 · 경 · 보")}
    <ul class="lint">
      {_lint(r['strengths'], '吉', 'good')}
      {_lint(r['warnings'], '警', 'warn')}
      {_lint(r['patches'], '補', 'patch')}
    </ul>
  </section>

  <section>
    {_title(4, "릴리즈 로드맵", f"대운 · {'순행' if chart['luck_forward'] else '역행'} · {chart['luck_start_age']}세 시작")}
    <div class="scroll-roll reveal">
      <div class="rod"></div>
      <ol class="road">{''.join(road)}</ol>
      <div class="rod"></div>
    </div>
  </section>

  <section>
    {_title(5, "릴리즈 노트", "세운")}
    <div class="releases">{releases}</div>
  </section>

  <section class="closing reveal">
    <p>{escape(r['closing'])}</p>
  </section>

  <footer>
    <p>AI 개발자가 봐주는 사주 · 재미로 보는 해석이며 중요한 결정의 근거가 아닙니다.</p>
    <p><a href="../">← 처음으로</a></p>
  </footer>
</main>
</body>
</html>
"""


def render_index(site: dict) -> str:
    apply = site.get("apply_url") or ""
    button = (f'<a class="btn" href="{escape(apply)}" target="_blank" rel="noopener">사주 신청하기</a>'
              if apply else '<p class="meta">신청 링크 준비 중이에요.</p>')
    seal = '<span class="seal-char">命</span><span class="seal-sub">四柱</span>'
    cards = [
        ("壹", "시스템 스펙", "사주 원국 여덟 글자를 만세력으로 정확히 계산해요."),
        ("貳", "리소스 모니터", "오행 분포를 내 개발 역량 그래프로 바꿔 보여드려요."),
        ("參", "워크 스타일", "십성으로 메이커형인지, 리서처형인지 알려드려요."),
        ("肆", "릴리즈 로드맵", "10년 단위 대운을 버전 태그처럼 정리해요."),
    ]
    grid = "".join(f'<div class="panel feature reveal" style="--i:{i}"><span class="mini-seal">{h}</span>'
                   f'<h3>{t}</h3><p>{d}</p></div>' for i, (h, t, d) in enumerate(cards))
    return _head(site["title"], site["description"], 0, False) + _hero(
        "$ saju --help", "개발자 사주", "AI 개발자가 봐드립니다", site["description"], seal, button
    ) + f"""
<main class="paper" id="start">
  <section>
    {_title(0, "이렇게 봐드려요", "개발자 언어로 푸는 사주")}
    <div class="features">{grid}</div>
  </section>
  <section>
    {_title(1, "신청 방법", "세 단계")}
    <ol class="steps">
      <li class="reveal">양력 생년월일, 태어난 시간(모르면 비워두세요), 성별, 닉네임을 보내주세요.</li>
      <li class="reveal">개발자가 직접 분석하고 다듬어요.</li>
      <li class="reveal">나만 아는 링크로 결과 페이지를 받아요.</li>
    </ol>
  </section>
  <footer><p>{escape(site.get('footer', ''))}</p></footer>
</main>
</body>
</html>
"""


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
