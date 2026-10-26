"""만세력 계산: 양력 출생 시각 → 년·월·일·시 네 기둥.

절기는 태양 황경으로 직접 계산한다 (Meeus 저정밀 공식, 오차 약 0.01° ≈ 15분).
절입 시각과 15분 이내로 겹치는 출생은 경계 케이스로 표시한다.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

STEMS = "甲乙丙丁戊己庚辛壬癸"
STEMS_KO = "갑을병정무기경신임계"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
BRANCHES_KO = "자축인묘진사오미신유술해"

KST = timezone(timedelta(hours=9))

# 한국 서머타임 (1987·1988). 이 구간의 시계 시각은 1시간 빼야 실제 KST.
_KOREA_DST = [
    (datetime(1987, 5, 10, 2, 0), datetime(1987, 10, 11, 3, 0)),
    (datetime(1988, 5, 8, 2, 0), datetime(1988, 10, 9, 3, 0)),
]


@dataclass(frozen=True)
class Pillar:
    stem: int    # 0..9
    branch: int  # 0..11

    @property
    def hanja(self) -> str:
        return STEMS[self.stem] + BRANCHES[self.branch]

    @property
    def hangul(self) -> str:
        return STEMS_KO[self.stem] + BRANCHES_KO[self.branch]

    @property
    def index60(self) -> int:
        return next(i for i in range(60) if i % 10 == self.stem and i % 12 == self.branch)

    @staticmethod
    def from_index60(i: int) -> "Pillar":
        i %= 60
        return Pillar(i % 10, i % 12)


@dataclass
class Pillars:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar | None
    solar_longitude: float
    near_term_boundary: bool   # 절입 15분 이내 → 년/월주가 틀릴 수 있음
    corrected_local: datetime  # 경도·서머타임 보정 후의 지방시


# ---------------------------------------------------------------- astronomy

def julian_day(dt_utc: datetime) -> float:
    y, m = dt_utc.year, dt_utc.month
    d = dt_utc.day + (dt_utc.hour + (dt_utc.minute + dt_utc.second / 60) / 60) / 24
    if m <= 2:
        y, m = y - 1, m + 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def solar_longitude(dt_utc: datetime) -> float:
    """겉보기 태양 황경 (도)."""
    t = (julian_day(dt_utc) - 2451545.0) / 36525
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = math.radians(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    omega = math.radians(125.04 - 1934.136 * t)
    return (l0 + c - 0.00569 - 0.00478 * math.sin(omega)) % 360


def month_index(lon: float) -> int:
    """절기 기준 월 순번. 0=寅월(입춘~) … 11=丑월(소한~)."""
    return int(((lon - 315) % 360) // 30)


def find_term(dt_utc: datetime, forward: bool) -> datetime:
    """dt_utc 다음(또는 직전) 절입 시각을 UTC로 찾는다."""
    step = timedelta(days=1 if forward else -1)
    start = month_index(solar_longitude(dt_utc))
    a = dt_utc
    b = a + step
    while month_index(solar_longitude(b)) == start:
        a, b = b, b + step
    # a 는 같은 달, b 는 다른 달 → 이분 탐색
    for _ in range(40):
        mid = a + (b - a) / 2
        if month_index(solar_longitude(mid)) == start:
            a = mid
        else:
            b = mid
    return b if forward else a


# ---------------------------------------------------------------- pillars

def _undo_dst(local: datetime) -> datetime:
    for s, e in _KOREA_DST:
        if s <= local < e:
            return local - timedelta(hours=1)
    return local


def _jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def compute_pillars(birth_local: datetime, hour_known: bool = True,
                    longitude: float | None = 127.0) -> Pillars:
    """birth_local: 한국 시계 기준 출생 시각 (tz 없는 naive datetime).

    longitude 를 주면 표준시(135°E)와의 차이만큼 지방시로 보정해 시주·일주 경계에 쓴다.
    서울 ≈ 127°E → 약 -32분. None 이면 보정하지 않는다.
    """
    kst = _undo_dst(birth_local)
    utc = kst.replace(tzinfo=KST).astimezone(timezone.utc)

    lon = solar_longitude(utc)
    midx = month_index(lon)

    # 년주: 입춘(315°) 전이면 전년도
    y = kst.year
    if kst.month <= 2 and midx >= 10:
        y -= 1
    year = Pillar((y - 4) % 10, (y - 4) % 12)

    # 월주: 寅월 천간은 년간으로 정해진다 (갑기년 → 병인월 …)
    first_stem = (year.stem % 5) * 2 + 2
    month = Pillar((first_stem + midx) % 10, (midx + 2) % 12)

    # 경계 판정: 앞뒤 절입이 15분 이내인가
    near = any(
        abs((find_term(utc, fwd) - utc).total_seconds()) < 15 * 60 for fwd in (True, False)
    )

    local = kst + timedelta(minutes=(longitude - 135) * 4) if longitude is not None else kst

    # 일주: 23시(子시 시작)부터 다음 날로 본다
    day_date = local.date() + timedelta(days=1 if local.hour >= 23 else 0)
    day = Pillar.from_index60(_jdn(day_date.year, day_date.month, day_date.day) + 49)

    hour = None
    if hour_known:
        branch = ((local.hour * 60 + local.minute + 60) // 120) % 12
        hour = Pillar(((day.stem % 5) * 2 + branch) % 10, branch)

    return Pillars(year, month, day, hour, lon, near, local)
