"""사주 원국 분석: 오행 분포, 십성, 대운, 세운."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from .calendar import KST, Pillar, Pillars, compute_pillars, find_term, _undo_dst

ELEMENTS = ["木", "火", "土", "金", "水"]
ELEMENTS_KO = ["목", "화", "토", "금", "수"]

STEM_ELEMENT = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
BRANCH_ELEMENT = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]
# 지지의 본기(정기) 천간
BRANCH_MAIN_STEM = [9, 5, 0, 1, 4, 2, 3, 5, 6, 7, 4, 8]


def stem_yang(stem: int) -> bool:
    return stem % 2 == 0


def ten_god(day_stem: int, other_stem: int) -> str:
    me, it = STEM_ELEMENT[day_stem], STEM_ELEMENT[other_stem]
    same = stem_yang(day_stem) == stem_yang(other_stem)
    rel = (it - me) % 5  # 0 같음, 1 내가 생함, 2 내가 극함, 3 나를 극함, 4 나를 생함
    return [
        ("비견", "겁재"), ("식신", "상관"), ("편재", "정재"), ("편관", "정관"), ("편인", "정인"),
    ][rel][0 if same else 1]


TEN_GOD_GROUP = {
    "비견": "비겁", "겁재": "비겁", "식신": "식상", "상관": "식상",
    "편재": "재성", "정재": "재성", "편관": "관성", "정관": "관성",
    "편인": "인성", "정인": "인성",
}


@dataclass
class PillarInfo:
    label: str
    hanja: str
    hangul: str
    stem_element: str
    branch_element: str
    stem_god: str | None
    branch_god: str


@dataclass
class LuckPeriod:
    start_age: int
    hanja: str
    hangul: str
    stem_god: str
    branch_god: str
    element: str


@dataclass
class Chart:
    birth: str
    gender: str
    hour_known: bool
    pillars: list[PillarInfo]
    day_master: str           # 일간 한자
    day_master_element: str
    day_master_yang: bool
    elements: dict[str, int]  # 오행 개수 (천간+지지)
    groups: dict[str, int]    # 십성 그룹 개수 (일간 제외)
    luck_forward: bool
    luck_start_age: int
    luck: list[LuckPeriod]
    yearly: list[dict] = field(default_factory=list)
    near_term_boundary: bool = False
    corrected_local: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _info(label: str, p: Pillar, day_stem: int, is_day: bool) -> PillarInfo:
    return PillarInfo(
        label=label,
        hanja=p.hanja,
        hangul=p.hangul,
        stem_element=ELEMENTS[STEM_ELEMENT[p.stem]],
        branch_element=ELEMENTS[BRANCH_ELEMENT[p.branch]],
        stem_god=None if is_day else ten_god(day_stem, p.stem),
        branch_god=ten_god(day_stem, BRANCH_MAIN_STEM[p.branch]),
    )


def _luck(ps: Pillars, birth_local: datetime, gender: str, ds: int) -> tuple[bool, int, list[LuckPeriod]]:
    # 양남음녀 순행, 음남양녀 역행
    forward = stem_yang(ps.year.stem) == (gender == "M")
    utc = _undo_dst(birth_local).replace(tzinfo=KST).astimezone(timezone.utc)
    days = abs((find_term(utc, forward) - utc).total_seconds()) / 86400
    start = max(1, round(days / 3))
    base = ps.month.index60
    periods = []
    for k in range(1, 10):
        p = Pillar.from_index60(base + (k if forward else -k))
        periods.append(LuckPeriod(
            start_age=start + (k - 1) * 10,
            hanja=p.hanja, hangul=p.hangul,
            stem_god=ten_god(ds, p.stem),
            branch_god=ten_god(ds, BRANCH_MAIN_STEM[p.branch]),
            element=ELEMENTS[STEM_ELEMENT[p.stem]] + ELEMENTS[BRANCH_ELEMENT[p.branch]],
        ))
    return forward, start, periods


def build_chart(birth_local: datetime, gender: str, hour_known: bool = True,
                longitude: float | None = 127.0, years: tuple[int, ...] = ()) -> Chart:
    ps = compute_pillars(birth_local, hour_known, longitude)
    ds = ps.day.stem

    infos = [_info("년주", ps.year, ds, False), _info("월주", ps.month, ds, False),
             _info("일주", ps.day, ds, True)]
    if ps.hour:
        infos.insert(0, _info("시주", ps.hour, ds, False))

    elements = {e: 0 for e in ELEMENTS}
    groups = {g: 0 for g in ("비겁", "식상", "재성", "관성", "인성")}
    for p in [ps.year, ps.month, ps.day] + ([ps.hour] if ps.hour else []):
        elements[ELEMENTS[STEM_ELEMENT[p.stem]]] += 1
        elements[ELEMENTS[BRANCH_ELEMENT[p.branch]]] += 1
        if p is not ps.day:
            groups[TEN_GOD_GROUP[ten_god(ds, p.stem)]] += 1
        groups[TEN_GOD_GROUP[ten_god(ds, BRANCH_MAIN_STEM[p.branch])]] += 1

    forward, start, luck = _luck(ps, birth_local, gender, ds)

    yearly = []
    for y in years:
        p = Pillar((y - 4) % 10, (y - 4) % 12)
        yearly.append({
            "year": y, "hanja": p.hanja, "hangul": p.hangul,
            "stem_god": ten_god(ds, p.stem),
            "branch_god": ten_god(ds, BRANCH_MAIN_STEM[p.branch]),
            "element": ELEMENTS[STEM_ELEMENT[p.stem]] + ELEMENTS[BRANCH_ELEMENT[p.branch]],
        })

    return Chart(
        birth=birth_local.strftime("%Y-%m-%d %H:%M") if hour_known else birth_local.strftime("%Y-%m-%d"),
        gender=gender,
        hour_known=hour_known,
        pillars=infos,
        day_master=ps.day.hanja[0],
        day_master_element=ELEMENTS[STEM_ELEMENT[ds]],
        day_master_yang=stem_yang(ds),
        elements=elements,
        groups=groups,
        luck_forward=forward,
        luck_start_age=start,
        luck=luck,
        yearly=yearly,
        near_term_boundary=ps.near_term_boundary,
        corrected_local=ps.corrected_local.strftime("%Y-%m-%d %H:%M"),
    )
