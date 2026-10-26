"""사용법

  py -m saju new --name 닉네임 --birth "1995-03-02 14:30" --gender M
  py -m saju new --name 닉네임 --birth 1995-03-02 --gender F      # 시간 모름
  py -m saju build                                                # docs/ 생성
  py -m saju list
"""
from __future__ import annotations

import argparse
import json
import secrets
from datetime import date, datetime

from .analysis import analyze
from .chart import build_chart
from .reading import draft_reading
from .render import DOCS, READINGS, build


def _parse_birth(s: str) -> tuple[datetime, bool]:
    for fmt, has_hour in (("%Y-%m-%d %H:%M", True), ("%Y-%m-%d", False)):
        try:
            return datetime.strptime(s.strip(), fmt), has_hour
        except ValueError:
            pass
    raise SystemExit(f"생년월일 형식이 이상해요: {s!r} (예: 1995-03-02 14:30 또는 1995-03-02)")


def cmd_new(a: argparse.Namespace) -> None:
    birth, has_hour = _parse_birth(a.birth)
    this_year = date.today().year
    chart = build_chart(birth, a.gender, has_hour, None if a.no_lon else a.lon,
                        years=(this_year, this_year + 1))
    analysis = analyze(chart)
    reading = draft_reading(chart, analysis, a.name)

    if a.llm:
        from .llm import rewrite
        reading = rewrite(a.llm, {**chart.to_dict(), "analysis": analysis.to_dict()}, reading, a.note)

    slug = a.slug or secrets.token_hex(4)
    data = {
        "slug": slug,
        "name": a.name,
        "note": a.note,
        "created": date.today().isoformat(),
        "chart": chart.to_dict(),
        "analysis": analysis.to_dict(),
        "reading": reading,
    }
    READINGS.mkdir(exist_ok=True)
    path = READINGS / f"{slug}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    p = {x["label"]: x["hanja"] for x in data["chart"]["pillars"]}
    print(f"원국  {p.get('시주', '--')} {p['일주']} {p['월주']} {p['년주']}  (시 일 월 년)")
    if chart.near_term_boundary:
        print("주의  절입 시각과 15분 이내 — 다른 만세력과 월주를 대조해 보세요.")
    print(f"저장  {path}")
    print("다음  reading 부분을 다듬은 뒤 `py -m saju build`")


def cmd_build(_: argparse.Namespace) -> None:
    pages = build()
    print(f"{len(pages)}개 결과 페이지 + index → {DOCS}")
    for p in pages:
        print(f"  /{p.parent.name}/")


def cmd_list(_: argparse.Namespace) -> None:
    for f in sorted(READINGS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        print(f"{d['slug']}  {d['created']}  {d['name']}  {d['chart']['birth']}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="saju", description="AI 개발자가 봐주는 사주")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="신청 한 건을 계산하고 초안 JSON 생성")
    n.add_argument("--name", required=True, help="페이지에 나갈 닉네임 (실명 비추천)")
    n.add_argument("--birth", required=True, help='양력 "YYYY-MM-DD HH:MM" 또는 "YYYY-MM-DD"')
    n.add_argument("--gender", required=True, choices=["M", "F"])
    n.add_argument("--lon", type=float, default=127.0, help="출생지 경도, 지방시 보정용 (기본 127=서울)")
    n.add_argument("--no-lon", action="store_true", help="지방시 보정 끄기")
    n.add_argument("--note", default="", help="신청자가 남긴 고민/질문")
    n.add_argument("--llm", help="초안을 LLM 으로 다시 쓰기 (예: anthropic)")
    n.add_argument("--slug", help="URL 경로 직접 지정 (기본: 랜덤 8자)")
    n.set_defaults(func=cmd_new)

    sub.add_parser("build", help="docs/ 에 정적 사이트 생성").set_defaults(func=cmd_build)
    sub.add_parser("list", help="저장된 신청 목록").set_defaults(func=cmd_list)

    a = ap.parse_args()
    a.func(a)
