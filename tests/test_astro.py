from datetime import datetime, timezone

from saju.astro import angles, build_astro, longitude
from saju.calendar import solar_longitude


def test_planets_at_j2000():
    t = datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)
    ref = {"태양": 280.4, "달": 223.3, "수성": 271.9, "금성": 241.6, "화성": 327.9,
           "목성": 25.2, "토성": 40.4, "천왕성": 314.8, "해왕성": 303.2, "명왕성": 251.4}
    for name, lon in ref.items():
        assert abs((longitude(name, t) - lon + 180) % 360 - 180) < 0.3, name


def test_ascendant_equals_sun_at_sunrise():
    # 서울 일출(2024-06-21 05:11 KST) 무렵엔 상승궁 ≈ 태양 황경
    t = datetime(2024, 6, 20, 20, 11, tzinfo=timezone.utc)
    asc, _ = angles(t, 37.5665, 126.978)
    assert abs(asc - solar_longitude(t)) < 2


def test_leehwon_big_three():
    c = build_astro(datetime(1998, 2, 17, 14, 30), True, years=(2026, 2027))
    assert (c.body("태양").sign, c.body("달").sign, c.asc_sign) == (10, 7, 3)  # 물병 · 전갈 · 게
    assert any(r["what"] == "토성 회귀" and r["year"] == 2027 for r in c.returns)
