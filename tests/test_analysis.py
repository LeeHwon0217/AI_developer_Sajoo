from datetime import date, datetime

from saju.analysis import analyze, relations
from saju.chart import build_chart


def leehwon():
    return analyze(build_chart(datetime(1998, 2, 17, 14, 30), "M"), date(2026, 10, 26))


def test_relations():
    assert "충" in relations("寅", "申")
    assert "육합" in relations("午", "未")
    assert "반합" in relations("寅", "午")
    assert "귀문" in relations("寅", "未")
    assert relations("寅", "寅") == []


def test_strength_and_yongsin():
    a = leehwon()
    assert a.strong and (a.support, a.total) == (6, 10)
    assert a.yongsin_group == "식상" and a.yongsin_element == "火"


def test_hidden_stems_reveal_fire():
    a = leehwon()
    assert a.hidden["일주"] == "丁乙己"
    assert a.hidden_groups["식상"] == 4


def test_shinsal_and_spouse():
    a = leehwon()
    assert sorted(a.shinsal["화개"]) == ["시주", "일주"]
    assert a.spouse_palace == "未" and a.spouse_palace_god == "편재"
    assert a.child_star_count == 0


def test_years():
    y = {x.year: x for x in leehwon().years}
    assert y[2026].hanja == "丙午" and "육합" in y[2026].with_day_branch
    assert y[2028].stem_god == "정재" and "인연" in y[2028].tags
    assert y[2030].stem_god == "정관" and "자녀" in y[2030].tags


def test_daeun_years():
    d = leehwon().daeun_years
    assert d[2]["hanja"] == "丁巳" and (d[2]["from"], d[2]["to"]) == (2023, 2032)
