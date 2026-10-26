"""readings/*.json → docs/ 정적 HTML (GitHub Pages)."""
from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READINGS = ROOT / "readings"
DOCS = ROOT / "docs"
ASSETS = Path(__file__).resolve().parent / "assets"

EL_CLASS = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water"}
EL_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}


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
{robots}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
"""


def _pillar_cell(p: dict) -> str:
    s_el, b_el = p["stem_element"], p["branch_element"]
    god_top = p["stem_god"] or "일간 (나)"
    return f"""<div class="pillar">
  <div class="plabel">{escape(p['label'])}</div>
  <div class="pgod">{escape(god_top)}</div>
  <div class="char {EL_CLASS[s_el]}">{p['hanja'][0]}<small>{p['hangul'][0]} · {EL_KO[s_el]}</small></div>
  <div class="char {EL_CLASS[b_el]}">{p['hanja'][1]}<small>{p['hangul'][1]} · {EL_KO[b_el]}</small></div>
  <div class="pgod">{escape(p['branch_god'])}</div>
</div>"""


def _bars(elements: dict[str, int]) -> str:
    total = sum(elements.values()) or 1
    rows = []
    for el, n in elements.items():
        pct = round(n / total * 100)
        status = "MISSING" if n == 0 else ("HIGH" if n >= 3 else "OK")
        rows.append(f"""<div class="bar-row">
  <span class="bar-name {EL_CLASS[el]}-text">{el} {EL_KO[el]}</span>
  <span class="bar-track"><span class="bar-fill {EL_CLASS[el]}" style="width:{max(pct, 2) if n else 0}%"></span></span>
  <span class="bar-val">{n} <em class="st-{status.lower()}">{status}</em></span>
</div>""")
    return "\n".join(rows)


def _lis(items: list[str], cls: str, mark: str) -> str:
    if not items:
        return f'<li class="{cls} empty">{mark} 해당 없음</li>'
    return "\n".join(f'<li class="{cls}"><span class="mark">{mark}</span> {escape(t)}</li>' for t in items)


def render_reading(data: dict) -> str:
    chart, r = data["chart"], data["reading"]
    order = {"시주": 0, "일주": 1, "월주": 2, "년주": 3}
    pillars = sorted(chart["pillars"], key=lambda p: order[p["label"]])
    gender = "남" if chart["gender"] == "M" else "여"
    notes = []
    if not chart["hour_known"]:
        notes.append("태어난 시간을 몰라 시주 없이 세 기둥으로 봤어요.")
    if chart["near_term_boundary"]:
        notes.append("절기가 바뀌는 시각과 아주 가까워 월주가 달라질 수 있어요.")

    roadmap = "\n".join(f"""<li>
  <span class="tag">{escape(x['version'])}</span>
  <span class="ganji">{escape(x['pillar'])}</span>
  <p>{escape(x['note'])}</p>
</li>""" for x in r["roadmap"])

    releases = "\n".join(f"""<article class="release">
  <h3><span class="tag">{x['year']}</span> {escape(x['pillar'])}</h3>
  <p>{escape(x['note'])}</p>
</article>""" for x in r["releases"])

    note_html = "".join(f'<p class="notice">⚠ {escape(n)}</p>' for n in notes)

    return _head(f"{data['name']} 님의 개발자 사주", r["headline"], 1, True) + f"""
<main class="wrap">
  <header class="hero">
    <p class="prompt">$ saju analyze --user "{escape(data['name'])}"</p>
    <h1>{escape(r['headline'])}</h1>
    <p class="meta">{escape(chart['birth'])} · {gender} · 보정 지방시 {escape(chart['corrected_local'])}</p>
    {note_html}
  </header>

  <section>
    <h2><span class="num">01</span> 시스템 스펙 <small>사주 원국</small></h2>
    <div class="pillars">{''.join(_pillar_cell(p) for p in pillars)}</div>
    <p class="lead">{escape(r['summary'])}</p>
  </section>

  <section>
    <h2><span class="num">02</span> 리소스 모니터 <small>오행 분포</small></h2>
    <div class="bars">{_bars(chart['elements'])}</div>
  </section>

  <section>
    <h2><span class="num">03</span> 워크 스타일 <small>십성</small></h2>
    <div class="card">
      <h3>{escape(r['work_style']['title'])}</h3>
      <p>{escape(r['work_style']['body'])}</p>
    </div>
  </section>

  <section>
    <h2><span class="num">04</span> 린트 결과 <small>강점 · 경고 · 패치</small></h2>
    <ul class="lint">
      {_lis(r['strengths'], 'ok', '✓')}
      {_lis(r['warnings'], 'warn', '⚠')}
      {_lis(r['patches'], 'patch', '+')}
    </ul>
  </section>

  <section>
    <h2><span class="num">05</span> 릴리즈 로드맵 <small>대운 · {'순행' if chart['luck_forward'] else '역행'}, {chart['luck_start_age']}세 시작</small></h2>
    <ol class="roadmap">{roadmap}</ol>
  </section>

  <section>
    <h2><span class="num">06</span> 릴리즈 노트 <small>세운</small></h2>
    {releases}
  </section>

  <section class="closing">
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
    button = (f'<a class="btn" href="{escape(apply)}" target="_blank" rel="noopener">사주 신청하기 →</a>'
              if apply else '<p class="notice">신청 링크 준비 중이에요.</p>')
    return _head(site["title"], site["description"], 0, False) + f"""
<main class="wrap">
  <header class="hero">
    <p class="prompt">$ npx saju --help</p>
    <h1>{escape(site['title'])}</h1>
    <p class="lead">{escape(site['description'])}</p>
    {button}
  </header>

  <section>
    <h2><span class="num">&gt;</span> 이렇게 봐드려요</h2>
    <div class="grid">
      <div class="card"><h3>시스템 스펙</h3><p>사주 원국 여덟 글자를 만세력으로 정확히 계산해요.</p></div>
      <div class="card"><h3>리소스 모니터</h3><p>오행 분포를 내 개발 역량 그래프로 바꿔 보여드려요.</p></div>
      <div class="card"><h3>워크 스타일</h3><p>십성으로 메이커형인지, 리서처형인지 알려드려요.</p></div>
      <div class="card"><h3>릴리즈 로드맵</h3><p>10년 단위 대운을 버전 태그처럼 정리해요.</p></div>
    </div>
  </section>

  <section>
    <h2><span class="num">&gt;</span> 신청 방법</h2>
    <ol class="steps">
      <li>양력 생년월일, 태어난 시간(모르면 비워두세요), 성별, 닉네임을 보내주세요.</li>
      <li>개발자가 직접 분석하고 다듬어요.</li>
      <li>나만 아는 링크로 결과 페이지를 받아요.</li>
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
    shutil.copy(ASSETS / "style.css", DOCS / "assets" / "style.css")
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
