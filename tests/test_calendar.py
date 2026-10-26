from datetime import datetime, timezone

from saju.calendar import KST, compute_pillars, find_term
from saju.chart import build_chart, ten_god


def pillars(s, **kw):
    p = compute_pillars(datetime.strptime(s, "%Y-%m-%d %H:%M"), **kw)
    return p.year.hanja, p.month.hanja, p.day.hanja, p.hour.hanja


def test_day_pillar_anchors():
    assert pillars("2000-01-01 12:00")[2] == "戊午"
    assert pillars("1900-01-01 12:00")[2] == "甲戌"


def test_year_changes_at_ipchun():
    # 2024 입춘 = 2024-02-04 17:27 KST
    assert pillars("2024-02-04 12:00")[:2] == ("癸卯", "乙丑")
    assert pillars("2024-02-05 12:00")[:2] == ("甲辰", "丙寅")


def test_ipchun_time_within_15_minutes():
    t = find_term(datetime(2024, 2, 1, tzinfo=timezone.utc), True).astimezone(KST)
    expected = datetime(2024, 2, 4, 17, 27, tzinfo=KST)
    assert abs((t - expected).total_seconds()) < 15 * 60


def test_hour_pillar_and_late_night_rolls_day():
    # 甲일 子시는 甲子시. 2000-01-01(戊午) 다음 날은 己未.
    y, m, d, h = pillars("2000-01-01 23:40", longitude=None)
    assert d == "己未" and h == "甲子"


def test_longitude_correction_moves_hour():
    # 13:10 KST → 서울 지방시 12:38 → 午시
    assert pillars("2000-01-01 13:10")[3][1] == "午"
    assert pillars("2000-01-01 13:10", longitude=None)[3][1] == "未"


def test_ten_gods():
    assert ten_god(0, 0) == "비견"   # 甲-甲
    assert ten_god(0, 3) == "상관"   # 甲-丁
    assert ten_god(0, 7) == "정관"   # 甲-辛
    assert ten_god(8, 2) == "편재"   # 壬-丙


def test_luck_direction():
    # 乙亥년(음) 남자 → 역행
    c = build_chart(datetime(1995, 3, 2, 14, 30), "M")
    assert not c.luck_forward and c.luck[0].hanja == "丁丑"
    c = build_chart(datetime(1995, 3, 2, 14, 30), "F")
    assert c.luck_forward and c.luck[0].hanja == "己卯"
