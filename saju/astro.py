"""서양 점성술 출생 차트 계산: 행성 황경, 상승궁(ASC), 중천(MC), 하우스, 애스펙트, 트랜짓.

행성: JPL 근사 케플러 요소 (Standish, 1800–2050, 오차 수 분각).
달: Meeus 47장 주요 항 (오차 약 0.05°). 태양: calendar.solar_longitude (겉보기 황경).
하우스: 홀사인(상승궁이 있는 별자리 = 1하우스).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone

from .calendar import KST, _undo_dst, julian_day, solar_longitude

SIGNS = ["양자리", "황소자리", "쌍둥이자리", "게자리", "사자자리", "처녀자리",
         "천칭자리", "전갈자리", "사수자리", "염소자리", "물병자리", "물고기자리"]
SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
GLYPH = [chr(0x2648 + i) + "︎" for i in range(12)]
SIGN_ELEMENT = ["불", "흙", "공기", "물"] * 3
SIGN_MODE = ["활동", "고정", "변통"] * 4

PLANETS = ["태양", "달", "수성", "금성", "화성", "목성", "토성", "천왕성", "해왕성", "명왕성"]
PLANETS_EN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
PLANET_GLYPH = {"태양": "☉", "달": "☽", "수성": "☿", "금성": "♀", "화성": "♂", "목성": "♃",
                "토성": "♄", "천왕성": "♅", "해왕성": "♆", "명왕성": "♇"}

# a, e, I, L, 근일점 경도, 승교점 경도 (J2000 값, 세기당 변화율)
_ELEMENTS = {
    "수성": ((0.38709927, 0.00000037), (0.20563593, 0.00001906), (7.00497902, -0.00594749),
             (252.25032350, 149472.67411175), (77.45779628, 0.16047689), (48.33076593, -0.12534081)),
    "금성": ((0.72333566, 0.00000390), (0.00677672, -0.00004107), (3.39467605, -0.00078890),
             (181.97909950, 58517.81538729), (131.60246718, 0.00268329), (76.67984255, -0.27769418)),
    "지구": ((1.00000261, 0.00000562), (0.01671123, -0.00004392), (-0.00001531, -0.01294668),
             (100.46457166, 35999.37244981), (102.93768193, 0.32327364), (0.0, 0.0)),
    "화성": ((1.52371034, 0.00001847), (0.09339410, 0.00007882), (1.84969142, -0.00813131),
             (-4.55343205, 19140.30268499), (-23.94362959, 0.44441088), (49.55953891, -0.29257343)),
    "목성": ((5.20288700, -0.00011607), (0.04838624, -0.00013253), (1.30439695, -0.00183714),
             (34.39644051, 3034.74612775), (14.72847983, 0.21252668), (100.47390909, 0.20469106)),
    "토성": ((9.53667594, -0.00125060), (0.05386179, -0.00050991), (2.48599187, 0.00193609),
             (49.95424423, 1222.49362201), (92.59887831, -0.41897216), (113.66242448, -0.28867794)),
    "천왕성": ((19.18916464, -0.00196176), (0.04725744, -0.00004397), (0.77263783, -0.00242939),
              (313.23810451, 428.48202785), (170.95427630, 0.40805281), (74.01692503, 0.04240589)),
    "해왕성": ((30.06992276, 0.00026291), (0.00859048, 0.00005105), (1.77004347, 0.00035372),
              (-55.12002969, 218.45945325), (44.96476227, -0.32241464), (131.78422574, -0.00508664)),
    "명왕성": ((39.48211675, -0.00031596), (0.24882730, 0.00005170), (17.14001206, 0.00004818),
              (238.92903833, 145.20780515), (224.06891629, -0.04062942), (110.30393684, -0.01183482)),
}

ASPECTS = [("합", 0, 8), ("육분", 60, 5), ("사각", 90, 7), ("삼분", 120, 7), ("대립", 180, 8)]


def _rad(x: float) -> float:
    return math.radians(x)


def _helio(name: str, t: float) -> tuple[float, float, float]:
    (a0, a1), (e0, e1), (i0, i1), (l0, l1), (w0, w1), (o0, o1) = _ELEMENTS[name]
    a, e, inc = a0 + a1 * t, e0 + e1 * t, _rad(i0 + i1 * t)
    L, varpi, node = l0 + l1 * t, w0 + w1 * t, o0 + o1 * t
    arg, M = _rad(varpi - node), _rad((L - varpi) % 360)
    E = M
    for _ in range(12):
        E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    xp, yp = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    co, so, cn, sn, ci, si = math.cos(arg), math.sin(arg), math.cos(_rad(node)), math.sin(_rad(node)), math.cos(inc), math.sin(inc)
    x = (co * cn - so * sn * ci) * xp + (-so * cn - co * sn * ci) * yp
    y = (co * sn + so * cn * ci) * xp + (-so * sn + co * cn * ci) * yp
    z = (so * si) * xp + (co * si) * yp
    return x, y, z


def _moon(t: float) -> float:
    Lp = 218.3164477 + 481267.88123421 * t
    D = _rad(297.8501921 + 445267.1114034 * t)
    M = _rad(357.5291092 + 35999.0502909 * t)
    Mp = _rad(134.9633964 + 477198.8675055 * t)
    F = _rad(93.2720950 + 483202.0175233 * t)
    E = 1 - 0.002516 * t
    s = (6.288774 * math.sin(Mp) + 1.274027 * math.sin(2 * D - Mp) + 0.658314 * math.sin(2 * D)
         + 0.213618 * math.sin(2 * Mp) - 0.185116 * E * math.sin(M) - 0.114332 * math.sin(2 * F)
         + 0.058793 * math.sin(2 * D - 2 * Mp) + 0.057066 * E * math.sin(2 * D - M - Mp)
         + 0.053322 * math.sin(2 * D + Mp) + 0.045758 * E * math.sin(2 * D - M)
         - 0.040923 * E * math.sin(M - Mp) - 0.034720 * math.sin(D) - 0.030383 * E * math.sin(M + Mp)
         + 0.015327 * math.sin(2 * D - 2 * F) - 0.012528 * math.sin(Mp + 2 * F) + 0.010980 * math.sin(Mp - 2 * F)
         + 0.010675 * math.sin(4 * D - Mp) + 0.010034 * math.sin(3 * Mp) + 0.008548 * math.sin(4 * D - 2 * Mp)
         - 0.007888 * E * math.sin(2 * D + M - Mp) - 0.006766 * E * math.sin(2 * D + M)
         - 0.005163 * math.sin(D - Mp) + 0.004987 * E * math.sin(D + M) + 0.004036 * E * math.sin(2 * D - M + Mp))
    return (Lp + s) % 360


def longitude(name: str, utc: datetime) -> float:
    """지구에서 본 황경 (그 날의 춘분점 기준, 도)."""
    if name == "태양":
        return solar_longitude(utc)
    jd = julian_day(utc)
    t = (jd - 2451545.0) / 36525
    if name == "달":
        return _moon(t)
    px, py, pz = _helio(name, t)
    ex, ey, ez = _helio("지구", t)
    lon = math.degrees(math.atan2(py - ey, px - ex))
    return (lon + 1.3969713 * t) % 360  # J2000 → 그 날의 춘분점 (세차)


def angles(utc: datetime, lat: float, lon_east: float) -> tuple[float, float]:
    """(상승궁 ASC, 중천 MC) 황경."""
    jd = julian_day(utc)
    t = (jd - 2451545.0) / 36525
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t
    ramc = _rad((gmst + lon_east) % 360)
    eps = _rad(23.4392911 - 0.0130042 * t)
    asc = math.degrees(math.atan2(math.cos(ramc), -(math.sin(ramc) * math.cos(eps) + math.tan(_rad(lat)) * math.sin(eps))))
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps)))
    return asc % 360, mc % 360


def sign_of(lon: float) -> int:
    return int(lon // 30) % 12


@dataclass
class Body:
    name: str
    lon: float
    sign: int
    deg: float          # 별자리 안에서의 도수
    house: int | None   # 홀사인 하우스 (생시 모르면 None)
    retro: bool

    @property
    def label(self) -> str:
        return f"{SIGNS[self.sign]} {int(self.deg)}°"


@dataclass
class AstroChart:
    birth: str
    hour_known: bool
    place: str
    bodies: list[Body]
    asc: float | None
    mc: float | None
    asc_sign: int | None
    mc_sign: int | None
    elements: dict[str, int]
    modes: dict[str, int]
    aspects: list[dict]
    moon_uncertain: bool  # 생시를 몰라 달 별자리가 하루 사이에 바뀌는 경우
    transits: list[dict] = field(default_factory=list)
    returns: list[dict] = field(default_factory=list)

    def body(self, name: str) -> Body:
        return next(b for b in self.bodies if b.name == name)

    def to_dict(self) -> dict:
        d = asdict(self)
        for b in d["bodies"]:
            b["label"] = f"{SIGNS[b['sign']]} {int(b['deg'])}°"
        return d


def _aspects(bodies: list[Body]) -> list[dict]:
    out = []
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            diff = abs((a.lon - b.lon + 180) % 360 - 180)
            for name, angle, orb in ASPECTS:
                extra = 1 if "태양" in (a.name, b.name) or "달" in (a.name, b.name) else 0
                if abs(diff - angle) <= orb + extra:
                    out.append({"a": a.name, "b": b.name, "type": name, "orb": round(abs(diff - angle), 1)})
    return sorted(out, key=lambda x: x["orb"])


def _ingresses(name: str, start: datetime, end: datetime) -> list[tuple[datetime, int]]:
    """start~end 사이 별자리 이동 (역행으로 되돌아가는 것 포함)."""
    out, t = [], start
    prev = sign_of(longitude(name, t))
    out.append((start, prev))
    while t < end:
        t += timedelta(days=3)
        s = sign_of(longitude(name, t))
        if s != prev:
            out.append((t, s))
            prev = s
    return out


def build_astro(birth_local: datetime, hour_known: bool = True, lat: float = 37.5665,
                lon_east: float = 126.978, place: str = "서울", years: tuple[int, ...] = ()) -> AstroChart:
    local = birth_local if hour_known else birth_local.replace(hour=12, minute=0)
    utc = _undo_dst(local).replace(tzinfo=KST).astimezone(timezone.utc)

    asc = mc = None
    if hour_known:
        asc, mc = angles(utc, lat, lon_east)
    first_house = sign_of(asc) if asc is not None else None

    bodies = []
    for name in PLANETS:
        lon = longitude(name, utc)
        lon_next = longitude(name, utc + timedelta(hours=12))
        retro = name not in ("태양", "달") and ((lon_next - lon + 540) % 360 - 180) < 0
        house = (sign_of(lon) - first_house) % 12 + 1 if first_house is not None else None
        bodies.append(Body(name, lon, sign_of(lon), lon % 30, house, retro))

    moon_uncertain = False
    if not hour_known:
        day0 = _undo_dst(birth_local.replace(hour=0, minute=0)).replace(tzinfo=KST).astimezone(timezone.utc)
        moon_uncertain = sign_of(longitude("달", day0)) != sign_of(longitude("달", day0 + timedelta(hours=23, minutes=59)))

    elements = {e: 0 for e in ("불", "흙", "공기", "물")}
    modes = {m: 0 for m in ("활동", "고정", "변통")}
    for b in bodies[:7]:  # 개인 행성 + 목성·토성
        elements[SIGN_ELEMENT[b.sign]] += 2 if b.name in ("태양", "달") else 1
        modes[SIGN_MODE[b.sign]] += 2 if b.name in ("태양", "달") else 1
    if asc is not None:
        elements[SIGN_ELEMENT[sign_of(asc)]] += 2
        modes[SIGN_MODE[sign_of(asc)]] += 2

    chart = AstroChart(
        birth=birth_local.strftime("%Y-%m-%d %H:%M") if hour_known else birth_local.strftime("%Y-%m-%d"),
        hour_known=hour_known, place=place, bodies=bodies, asc=asc, mc=mc,
        asc_sign=first_house, mc_sign=sign_of(mc) if mc is not None else None,
        elements=elements, modes=modes, aspects=_aspects(bodies), moon_uncertain=moon_uncertain,
    )

    # 앞으로의 목성·토성 별자리 이동 (그 별자리가 내 차트의 몇 하우스인지)
    if years:
        start = datetime(min(years), 1, 1, tzinfo=timezone.utc)
        end = datetime(max(years), 12, 31, tzinfo=timezone.utc)
        for name in ("목성", "토성"):
            for when, s in _ingresses(name, start, end):
                house = (s - first_house) % 12 + 1 if first_house is not None else None
                sun_house = (s - chart.body("태양").sign) % 12 + 1
                chart.transits.append({"planet": name, "from": when.strftime("%Y-%m"), "sign": s,
                                       "house": house, "from_sun": sun_house})

    # 지나온 길: 목성 회귀(약 12년)와 토성 회귀(약 29년), 토성 사각·대립
    jup0, sat0 = chart.body("목성").lon, chart.body("토성").lon
    t, end = utc + timedelta(days=200), datetime(max(years or (2030,)), 12, 31, tzinfo=timezone.utc)
    seen = set()
    while t < end:
        for name, base, cycles in (("목성", jup0, {0: "목성 회귀"}), ("토성", sat0, {0: "토성 회귀", 90: "토성 사각", 180: "토성 대립", 270: "토성 사각"})):
            d = (longitude(name, t) - base) % 360
            for ang, label in cycles.items():
                if abs((d - ang + 180) % 360 - 180) < 1.5:
                    key = (label, t.year)
                    if key not in seen and not any(k[0] == label and abs(k[1] - t.year) <= 1 for k in seen):
                        seen.add(key)
                        chart.returns.append({"what": label, "year": t.year,
                                              "age": t.year - birth_local.year + (0 if (t.month, t.day) < (birth_local.month, birth_local.day) else 0)})
        t += timedelta(days=10)
    chart.returns.sort(key=lambda r: r["year"])
    return chart
