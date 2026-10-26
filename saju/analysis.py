"""원국에서 해석에 쓸 사실들을 계산한다: 지장간, 신강약, 용신, 합충형, 신살, 연도별 운.

여기 나온 값들이 풀이의 '근거' 칩이 된다. 해석 문장은 reading.py 가 만든다.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

from .calendar import BRANCHES, STEMS, Pillar
from .chart import BRANCH_MAIN_STEM, ELEMENTS, STEM_ELEMENT, TEN_GOD_GROUP, Chart, ten_god

# 지장간 (여기, 중기, 정기 순)
HIDDEN = {
    "子": "癸", "丑": "癸辛己", "寅": "戊丙甲", "卯": "乙", "辰": "乙癸戊", "巳": "戊庚丙",
    "午": "丙己丁", "未": "丁乙己", "申": "戊壬庚", "酉": "庚辛", "戌": "辛丁戊", "亥": "戊甲壬",
}
SIX_HARMONY = {frozenset("子丑"), frozenset("寅亥"), frozenset("卯戌"), frozenset("辰酉"), frozenset("巳申"), frozenset("午未")}
TRIADS = ["申子辰", "亥卯未", "寅午戌", "巳酉丑"]
TRIAD_ELEMENT = {"申子辰": "水", "亥卯未": "木", "寅午戌": "火", "巳酉丑": "金"}
PUNISH = ["寅巳申", "丑戌未", "子卯"]
GHOST_GATE = {frozenset("子酉"), frozenset("丑午"), frozenset("寅未"), frozenset("卯申"), frozenset("辰亥"), frozenset("巳戌")}
# 삼합 그룹 → (도화, 역마, 화개)
SHINSAL = {"申子辰": "酉寅辰", "寅午戌": "卯申戌", "巳酉丑": "午亥丑", "亥卯未": "子巳未"}

GROUPS = ["비겁", "식상", "재성", "관성", "인성"]


def group_element(day_el: str, group: str) -> str:
    return ELEMENTS[(ELEMENTS.index(day_el) + GROUPS.index(group)) % 5]


def relations(a: str, b: str) -> list[str]:
    """두 지지 사이의 관계 이름들."""
    out = []
    if (BRANCHES.index(a) - BRANCHES.index(b)) % 12 == 6:
        out.append("충")
    if frozenset(a + b) in SIX_HARMONY:
        out.append("육합")
    if a != b and any(a in t and b in t for t in TRIADS):
        out.append("반합")
    if a != b and any(a in t and b in t for t in PUNISH):
        out.append("형")
    if frozenset(a + b) in GHOST_GATE:
        out.append("귀문")
    return out


def _triad(branch: str) -> str:
    return next(t for t in TRIADS if branch in t)


@dataclass
class YearLuck:
    year: int
    age: int  # 세는나이
    hanja: str
    stem_god: str
    branch_god: str
    with_day_branch: list[str]
    tags: list[str] = field(default_factory=list)


@dataclass
class Analysis:
    strong: bool
    support: int
    total: int
    yongsin_group: str
    yongsin_element: str
    heesin_element: str
    gisin_element: str
    hidden: dict[str, str]
    hidden_groups: dict[str, int]
    spouse_star: str           # 남: 재성, 여: 관성
    spouse_star_count: int
    spouse_palace: str         # 일지 글자
    spouse_palace_god: str
    child_star: str            # 남: 관성, 여: 식상
    child_star_count: int
    child_palace_gods: list[str]
    shinsal: dict[str, list[str]]  # 이름 → 원국에 있는 위치들
    chart_relations: list[str]
    daeun_years: list[dict]
    years: list[YearLuck]
    birth_year: int
    past_years: list[YearLuck] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def analyze(chart: Chart, today: date | None = None, span: int = 15) -> Analysis:
    today = today or date.today()
    birth_year = int(chart.birth[:4])
    ds = STEMS.index(chart.day_master)
    day_el = chart.day_master_element
    by_label = {p.label: p for p in chart.pillars}

    # 신강/신약: 월지 3, 일지 2, 나머지 1점
    support = total = 0
    for p in chart.pillars:
        for pos, ch in (("stem", p.hanja[0]), ("branch", p.hanja[1])):
            if p.label == "일주" and pos == "stem":
                continue
            w = 3 if (p.label == "월주" and pos == "branch") else 2 if (p.label == "일주" and pos == "branch") else 1
            stem = STEMS.index(ch) if pos == "stem" else BRANCH_MAIN_STEM[BRANCHES.index(ch)]
            total += w
            if TEN_GOD_GROUP[ten_god(ds, stem)] in ("비겁", "인성"):
                support += w
    strong = support * 2 >= total

    g = chart.groups
    if strong:
        cands = ["식상", "관성", "재성"]
    else:
        cands = ["비겁", "인성"] if g["재성"] + g["관성"] >= g["식상"] else ["인성", "비겁"]
    yongsin = min(cands, key=lambda c: (g[c], cands.index(c)))
    ys_el = group_element(day_el, yongsin)
    hee_el = ELEMENTS[(ELEMENTS.index(ys_el) + 1) % 5] if strong else ELEMENTS[(ELEMENTS.index(ys_el) - 1) % 5]
    gi_el = day_el if strong else group_element(day_el, "재성")

    hidden = {p.label: HIDDEN[p.hanja[1]] for p in chart.pillars}
    hidden_groups = {k: 0 for k in GROUPS}
    for hs in hidden.values():
        for ch in hs:
            hidden_groups[TEN_GOD_GROUP[ten_god(ds, STEMS.index(ch))]] += 1

    male = chart.gender == "M"
    spouse_star = "재성" if male else "관성"
    child_star = "관성" if male else "식상"
    day_branch = by_label["일주"].hanja[1]
    hour = by_label.get("시주")

    # 신살: 년지·일지 기준
    branches = {p.label: p.hanja[1] for p in chart.pillars}
    shinsal: dict[str, list[str]] = {"도화": [], "역마": [], "화개": []}
    for base in {branches["년주"], day_branch}:
        for name, target in zip(("도화", "역마", "화개"), SHINSAL[_triad(base)]):
            for label, b in branches.items():
                if b == target and label not in shinsal[name]:
                    shinsal[name].append(label)

    rels = []
    labels = list(branches)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            for r in relations(branches[a], branches[b]):
                rels.append(f"{a[0]}{branches[a]}–{b[0]}{branches[b]} {r}")

    daeun_years = [{
        "start_age": p.start_age, "hanja": p.hanja,
        "from": birth_year + p.start_age - 1, "to": birth_year + p.start_age + 8,
        "stem_god": p.stem_god, "branch_god": p.branch_god, "element": p.element,
    } for p in chart.luck]

    dohwa = {SHINSAL[_triad(b)][0] for b in {branches["년주"], day_branch}}
    yeokma = {SHINSAL[_triad(b)][1] for b in {branches["년주"], day_branch}}
    def year_luck(y: int) -> YearLuck:
        p = Pillar((y - 4) % 10, (y - 4) % 12)
        sg = ten_god(ds, p.stem)
        bg = ten_god(ds, BRANCH_MAIN_STEM[p.branch])
        br = BRANCHES[p.branch]
        rel = relations(br, day_branch)
        groups_here = {TEN_GOD_GROUP[sg], TEN_GOD_GROUP[bg]}
        tags = []
        if TEN_GOD_GROUP[sg] == spouse_star or "육합" in rel:
            tags.append("인연")
        if TEN_GOD_GROUP[sg] == child_star:
            tags.append("자녀")
        if "재성" in groups_here or (yongsin == "식상" and "식상" in groups_here):
            tags.append("재물")
        if yongsin in groups_here or ys_el in (ELEMENTS[STEM_ELEMENT[p.stem]],):
            tags.append("용신")
        if br in yeokma:
            tags.append("이동")
        if br in dohwa:
            tags.append("도화")
        if "충" in rel or "형" in rel:
            tags.append("변동")
        return YearLuck(y, y - birth_year + 1, p.hanja, sg, bg, rel, tags)

    years = [year_luck(y) for y in range(today.year, today.year + span)]
    past_years = [year_luck(y) for y in range(birth_year, today.year)]

    return Analysis(
        strong=strong, support=support, total=total,
        yongsin_group=yongsin, yongsin_element=ys_el, heesin_element=hee_el, gisin_element=gi_el,
        hidden=hidden, hidden_groups=hidden_groups,
        spouse_star=spouse_star, spouse_star_count=g[spouse_star],
        spouse_palace=day_branch, spouse_palace_god=by_label["일주"].branch_god,
        child_star=child_star, child_star_count=g[child_star],
        child_palace_gods=[hour.stem_god, hour.branch_god] if hour else [],
        shinsal=shinsal, chart_relations=rels,
        daeun_years=daeun_years, years=years, birth_year=birth_year, past_years=past_years,
    )
