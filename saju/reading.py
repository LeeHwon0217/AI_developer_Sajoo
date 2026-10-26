"""원국 + 분석 → 17개 섹션 풀이 (규칙 기반 초안). 개발 용어 없이 쉬운 우리말로 쓴다.

모든 섹션은 같은 모양의 dict 이고 렌더러는 있는 필드만 그린다.
  key, hanja, nav, title, sub, lead, paras[], cards[{title, body, badge}],
  stats[{label, value, sub}], bars[{label, value(0-100), note}],
  timeline[{when, title, body, now}], chips[], evidence[]
초안은 readings/*.json 에 저장되고, 사람이 다듬거나 --llm 으로 다시 쓴다.
"""
from __future__ import annotations

from datetime import date

from .analysis import Analysis
from .chart import ELEMENTS, Chart

EL_KO = {"木": "목", "火": "화", "土": "토", "金": "금", "水": "수"}

DAY_MASTER = {
    "甲": ("큰 나무", "곧은 리더", "곧고 책임감 있는 리더형. 한 번 정한 원칙은 잘 안 굽히고, 사람들이 기대는 기둥 같은 존재예요.", "고집이 세서 방향을 틀 타이밍을 놓치기 쉬워요."),
    "乙": ("덩굴과 꽃", "유연한 생존가", "유연하고 사교적인 생존형. 어떤 환경에서도 길을 찾아 감아 오르고, 분위기를 읽는 감각이 뛰어나요.", "겉으론 맞춰주지만 속으론 계산이 많고 예민해요."),
    "丙": ("태양", "밝은 분위기 메이커", "밝고 솔직한 확산형. 있는 곳을 환하게 만들고 사람을 끌어당겨요.", "기분이 표정에 다 드러나고, 디테일 마무리가 약해요."),
    "丁": ("촛불", "따뜻한 집중가", "따뜻하고 섬세한 집중형. 한 사람, 한 문제를 깊게 비추는 힘이 있어요.", "속으로 끓다가 한 번에 터지는 타입이에요."),
    "戊": ("큰 산", "믿음직한 버팀목", "묵직하고 믿음직한 포용형. 흔들리지 않고 다른 사람의 버팀목이 돼요.", "변화가 느리고 속마음을 잘 안 꺼내요."),
    "己": ("기름진 밭", "실속 있는 살림꾼", "실속 있고 꼼꼼한 관리형. 사람과 자원을 키워내는 데 재능이 있어요.", "걱정이 많고 남 눈치를 많이 봐요."),
    "庚": ("원석과 칼", "결단력 있는 개척자", "결단력 있고 의리 있는 돌파형. 옳다고 믿으면 밀어붙여요.", "말이 직설적이라 의도치 않게 상처를 줘요."),
    "辛": ("보석", "섬세한 완벽주의자", "예리하고 완벽주의적인 세공형. 품질과 자존심이 곧 정체성이에요.", "예민하고 상처를 오래 기억해요."),
    "壬": ("큰 강과 바다", "자유로운 모험가", "스케일이 크고 자유로운 흐름형. 넓게 보고 빠르게 흡수해요.", "한 곳에 오래 머무르기 힘들어해요."),
    "癸": ("비와 안개", "직관적인 사색가", "직관적이고 지적인 스며듦형. 조용히 패턴을 읽고 사람 마음을 적셔요.", "생각이 많아 결정을 미루곤 해요."),
}
GROUP_WORK = {
    "비겁": ("독립형", "내 방식, 내 오너십이 중요해요. 스스로 정한 기준으로 끝까지 밀어붙입니다."),
    "식상": ("메이커형", "만들고 표현하고 싶은 게 늘 있어요. 아이디어를 결과물로 옮기는 속도가 빨라요."),
    "재성": ("실리형", "결과와 쓸모, 돈이 되는지를 먼저 봐요. 지표로 우선순위를 잡아요."),
    "관성": ("조직형", "체계와 책임을 중시해요. 큰 조직에서 신뢰를 얻고 리더가 되기 쉬워요."),
    "인성": ("학습형", "배우고 정리하는 걸 좋아해요. 문서와 멘토링으로 팀을 키워요."),
}
CAREER = {
    "비겁": [("자영업 · 창업", 88), ("프리랜서 · 전문 기술직", 84), ("스포츠 · 현장 리더", 78)],
    "식상": [("디자인 · 예술 · 콘텐츠", 90), ("방송 · 강의 · 마케팅", 85), ("요리 · 뷰티 · 공예", 82)],
    "재성": [("영업 · 기획 · 마케팅", 90), ("금융 · 회계 · 유통", 86), ("사업 운영 · 관리", 80)],
    "관성": [("공무원 · 공기업", 88), ("대기업 관리직", 85), ("법 · 행정 · 군경", 80)],
    "인성": [("교육 · 연구", 88), ("의료 · 상담", 85), ("출판 · 글쓰기", 80)],
}
EL_LUCK = {
    "木": ("초록 · 청록", "동쪽", "3 · 8", "봄", "새로운 걸 꾸준히 배우는 습관"),
    "火": ("빨강 · 주황 · 보라", "남쪽", "2 · 7", "여름", "생각한 것, 만든 것을 밖으로 보여주는 습관"),
    "土": ("노랑 · 베이지 · 갈색", "중앙", "5 · 10", "환절기", "하루 루틴과 기록을 지키는 습관"),
    "金": ("흰색 · 은색 · 금색", "서쪽", "4 · 9", "가을", "마감과 약속을 스스로 정해 지키는 습관"),
    "水": ("검정 · 남색", "북쪽", "1 · 6", "겨울", "깊게 읽고 정리하는 시간"),
}
EL_BODY = {
    "木": "간 · 눈 · 근육 긴장(목·어깨)", "火": "심장 · 혈압 · 수면 리듬", "土": "위장 · 소화",
    "金": "폐 · 호흡기 · 피부", "水": "신장 · 허리 · 하체 순환",
}


# 그해(또는 그 대운)에 무슨 일이 있었을지: 십성별 과거형 문장
GOD_PAST = {
    "비견": "친구나 형제와 늘 붙어 다니고, 비교도 많이 당했을 거예요.",
    "겁재": "경쟁이 붙고, 내 것을 지키려고 고집이 세졌을 거예요.",
    "식신": "하고 싶은 게 많아지고 재능이 드러났을 거예요.",
    "상관": "반항심이 커지고 정해진 방식에 반기를 들었을 거예요.",
    "편재": "활동 범위가 넓어지고 바깥일에 관심이 많았을 거예요.",
    "정재": "현실적인 책임과 돈 관리를 처음 배웠을 거예요.",
    "편관": "압박이나 스트레스가 큰 일을 겪었을 거예요.",
    "정관": "규칙을 잘 지켜 칭찬받거나 책임 있는 역할을 맡았을 거예요.",
    "편인": "생각이 많아지고 혼자 있는 시간이 늘었을 거예요.",
    "정인": "좋은 선생님이나 어른의 도움을 받았을 거예요.",
}
GOD_FUTURE = {
    "비견": "같은 길을 가는 동료가 생기고 함께 커 가는 시기예요.",
    "겁재": "경쟁 속에서 내 몫을 지키며 독립하는 시기예요.",
    "식신": "하고 싶은 걸 마음껏 하며 재능이 결과로 바뀌는 시기예요.",
    "상관": "틀을 깨고 방향을 바꾸는 시기예요. 말조심만 하면 큰 도약이 돼요.",
    "편재": "활동 범위가 넓어지고 큰 기회와 돈이 오가는 시기예요.",
    "정재": "꾸준한 노력이 안정적인 수입과 자산으로 쌓이는 시기예요.",
    "편관": "책임과 압박이 커지지만 버티면 크게 단단해지는 시기예요.",
    "정관": "자리와 직함, 공식적인 인정이 따라오는 시기예요.",
    "편인": "생각이 깊어지고 나만의 분야를 파고드는 시기예요.",
    "정인": "배움과 도움이 들어오고 마음이 편안해지는 시기예요.",
}
TAG_PAST = {
    "변동": "이사, 전학, 가족의 변화처럼 환경이 크게 바뀌었을 가능성이 커요.",
    "이동": "새로운 곳으로 옮기거나 멀리 다녀올 일이 있었을 거예요.",
    "도화": "인기가 많았거나 마음이 설레는 일이 있었을 거예요.",
    "인연": "오래 기억에 남는 사람을 만났을 거예요.",
}
YONGSIN_RULE = {
    "비겁": "혼자 버티지 말고 내 편을 만드세요. 사람이 곧 운이에요.",
    "식상": "안에 있는 걸 밖으로 꺼내 보이세요. 보여줄수록 운이 열려요.",
    "재성": "결과와 실속을 챙기세요. 계획을 숫자로 적으면 운이 붙어요.",
    "관성": "스스로 규칙과 마감을 정하세요. 틀이 있을 때 더 크게 자라요.",
    "인성": "배우고 쉬는 시간을 지키세요. 채워야 꺼낼 수 있어요.",
}


def _stage(age: int) -> str:
    return ("아기 때" if age <= 4 else "어린 시절" if age <= 7 else "초등학생 때" if age <= 13
            else "중고등학생 때" if age <= 19 else f"{age // 10 * 10}대")


def _past_items(years, lo, hi, limit):
    picks = []
    for y in years:
        if not lo <= y.age <= hi:
            continue
        tags = [t for t in ("변동", "이동", "도화", "인연") if t in y.tags
                and not (t == "도화" and y.age < 12) and not (t == "인연" and y.age < 17)]
        if tags:
            picks.append((y, tags))
    return [{"when": f"{y.year} · {y.age}세", "title": f"{y.hanja} · {_stage(y.age)}",
             "body": f"{GOD_PAST[y.stem_god]} {TAG_PAST[tags[0]]}", "now": False}
            for y, tags in picks[:limit]]

def _sec(key, hanja, nav, title, sub="", **kw) -> dict:
    return {"key": key, "hanja": hanja, "nav": nav, "title": title, "sub": sub, **kw}


def _first(years, tag, min_age=0):
    return [y for y in years if tag in y.tags and y.age >= min_age]


def draft_reading(chart: Chart, a: Analysis, name: str, today: date | None = None) -> dict:
    today = today or date.today()
    image, role, good, bad = DAY_MASTER[chart.day_master]
    yy = "양" if chart.day_master_yang else "음"
    els, g = chart.elements, chart.groups
    top_group = max(g, key=g.get)
    missing = [e for e in ELEMENTS if els[e] == 0]
    excess = [e for e in ELEMENTS if els[e] >= 3]
    ys = a.yongsin_element
    p = {x.label: x for x in chart.pillars}
    dm = f"일간 {chart.day_master}({yy}{chart.day_master_element})"
    strength = f"{'신강' if a.strong else '신약'} {a.support}/{a.total}"
    male = chart.gender == "M"

    sections = []

    sections.append(_sec("chart", "命", "명식", "명식 한눈에", "어려운 건 이것만 알면 돼요",
        lead=f"{name} 님은 {image}의 기운을 타고난 사람.",
        paras=[
            f"사주의 주인공 글자(일간)는 {chart.day_master}, {image}예요.",
            f"내 편 기운이 {a.support}/{a.total}로 {'강해서 밀어붙이는 힘이 있고' if a.strong else '약해서 주변 도움을 잘 받아야 하고'}, "
            f"가장 필요한 기운(용신)은 {ys}({EL_KO[ys]})예요.",
        ],
        evidence=[dm, strength, f"용신 {ys}"]))


    # 지나온 길: 나이별로 있었을 법한 일들
    age_now = today.year - a.birth_year + 1
    first = a.daeun_years[0]
    spans = [(1, 13, "어린 시절"), (14, age_now - 1, "10대부터 지금까지")] if age_now >= 18 else [(1, age_now - 1, "태어나서 지금까지")]
    for n, (lo, hi, label) in enumerate(spans):
        items = _past_items(a.past_years, lo, hi, 6)
        if n == 0:
            items.insert(0, {"when": f"{a.birth_year}–{first['from'] - 1}", "title": f"대운 전 · 1~{first['start_age'] - 1}세",
                             "body": f"타고난 기운 그대로 자란 시기. {DAY_MASTER[chart.day_master][2]}", "now": False})
        for d in a.daeun_years:
            if lo <= d["start_age"] <= hi and d["from"] < today.year:
                items.append({"when": f"{d['from']} · {d['start_age']}세", "title": f"대운 {d['hanja']} 시작",
                              "body": f"10년의 흐름이 바뀌었어요. 앞 5년엔 {GOD_PAST[d['stem_god']]} 뒤 5년엔 {GOD_PAST[d['branch_god']]}",
                              "now": False})
        items.sort(key=lambda x: x["when"])
        sections.append(_sec(f"past{n + 1}", "往", "지나온 길", f"지나온 길{' ' + '①②'[n] if len(spans) > 1 else ''}", label,
            lead="지금까지 이렇게 살아왔을 거예요. 맞는지 하나씩 맞춰 보세요.",
            timeline=items[:7],
            evidence=[f"대운 {d['hanja']} ({d['from']}–)" for d in a.daeun_years if d["from"] <= today.year] + ["연운 " + str(a.birth_year) + "–" + str(today.year - 1)]))

    sections.append(_sec("persona", "性", "성격", "어떤 사람인가", f"{role}",
        lead=good, paras=[bad],
        evidence=[dm, f"가장 많은 십성: {top_group}"]))

    sections.append(_sec("mask", "面", "겉과 속", "남들이 보는 나 vs 진짜 나", "월주는 사회의 얼굴, 일지는 속마음",
        cards=[
            {"title": "남들이 보는 나", "badge": p["월주"].hanja, "body": f"사회에선 {p['월주'].stem_god}의 얼굴로 보여요."},
            {"title": "진짜 나", "badge": p["일주"].hanja, "body": f"속마음 자리에는 {p['일주'].branch_god}가 앉아 있어요."},
        ],
        evidence=[f"월주 {p['월주'].hanja}", f"일지 {p['일주'].hanja[1]}"]))

    sections.append(_sec("talent", "才", "재능", "타고난 재능", "",
        cards=[{"title": f"{e} 많음", "body": f"{EL_KO[e]} 기운이 넉넉해요."} for e in excess] or [{"title": "균형", "body": "오행이 고르게 퍼져 있어요."}],
        evidence=[f"오행 {' '.join(f'{k}{v}' for k, v in els.items())}"]))

    sections.append(_sec("bug", "病", "약점", "조심할 버그", "",
        cards=[{"title": f"{e} 없음", "body": f"{EL_KO[e]} 기운이 빠져 있어요."} for e in missing] or [{"title": "치명적 버그 없음", "body": "크게 빠진 기운은 없어요."}],
        evidence=[f"없는 오행: {', '.join(missing) or '없음'}"]))

    title, body = GROUP_WORK[top_group]
    sections.append(_sec("work", "工", "일하는 법", "일하는 방식", title, lead=body,
        evidence=[f"{k} {v}" for k, v in g.items()]))

    sections.append(_sec("career", "業", "직업", "잘 맞는 직업", "적합도",
        bars=[{"label": l, "value": v, "note": ""} for l, v in CAREER[top_group]],
        evidence=[f"주력 십성 {top_group}", f"용신 {a.yongsin_group}"]))

    peak = max(a.daeun_years, key=lambda d: (d["stem_god"] in ("정재", "편재")) * 2 + (d["branch_god"] in ("정재", "편재")) * 2
               + (d["stem_god"] in ("식신", "상관")) + (d["branch_god"] in ("식신", "상관")))
    score = min(g["재성"], 3) * 2 + min(g["식상"] + a.hidden_groups["식상"], 2) + (2 if a.strong and g["재성"] else 0)
    tier = ("소박하지만 안정", "5억 안팎") if score <= 2 else ("중산층 상단", "10~20억") if score <= 4 else \
           ("부자 그릇", "20~40억") if score <= 6 else ("큰 부자 그릇", "50억 이상")
    sections.append(_sec("money", "財", "재물", "돈은 얼마나 벌까", "재물 그릇",
        stats=[
            {"label": "재물 그릇", "value": tier[0], "sub": f"순자산 {tier[1]} 수준"},
            {"label": "재물 피크", "value": f"{peak['from']}–{peak['to']}", "sub": f"{peak['start_age']}세 대운 {peak['hanja']}"},
        ],
        evidence=[f"재성 {g['재성']}", f"식상(지장간 포함) {g['식상'] + a.hidden_groups['식상']}", strength]))

    sections.append(_sec("love", "愛", "연애", "연애 스타일", "",
        lead=f"배우자 자리(일지)에 {a.spouse_palace_god}가 있어요.",
        evidence=[f"일지 {a.spouse_palace}({a.spouse_palace_god})", f"배우자성 {a.spouse_star} {a.spouse_star_count}"]))

    wed = _first(a.years, "인연", 27)[:2]
    sections.append(_sec("marriage", "緣", "결혼", "결혼과 배우자", "",
        timeline=[{"when": str(y.year), "title": f"{y.hanja} · {y.age}세", "body": f"{y.stem_god}/{y.branch_god} {' '.join(y.with_day_branch)}"} for y in wed],
        evidence=[f"배우자성 {a.spouse_star}", f"일지 {a.spouse_palace}"]))

    c = a.child_star_count
    kids = "1명 (늦게 오는 편)" if c == 0 else "1~2명" if c == 1 else "2명" if c == 2 else "2~3명"
    first = _first(a.years, "자녀", 28)[:1]
    sections.append(_sec("children", "子", "자녀", "자녀운", "",
        stats=[{"label": "자녀 수", "value": kids, "sub": f"자녀성 {a.child_star} {c}개"},
               {"label": "첫째 시기", "value": str(first[0].year) if first else "–", "sub": first[0].hanja if first else ""}],
        evidence=[f"자녀성 {a.child_star} {c}", f"시주 {'·'.join(a.child_palace_gods) or '모름'}"]))

    sections.append(_sec("people", "友", "인연", "인간관계와 궁합", "",
        lead=f"{ys}({EL_KO[ys]}) 기운이 강한 사람이 귀인이에요.",
        evidence=[f"용신 {ys}"] + a.chart_relations[:2]))

    body_risk = [f"{e} 과다: {EL_BODY[e]}" for e in excess] + [f"{e} 부족: {EL_BODY[e]}" for e in missing]
    sections.append(_sec("health", "身", "건강", "컨디션 관리", "오행 전통 해석 · 의학적 진단 아님",
        cards=[{"title": t.split(':')[0], "body": t.split(': ')[1]} for t in body_risk] or [{"title": "균형", "body": "크게 치우친 곳이 없어요."}],
        evidence=[f"오행 {' '.join(f'{k}{v}' for k, v in els.items())}"]))

    sections.append(_sec("roadmap", "運", "대운", "인생 로드맵", "10년 단위 대운",
        timeline=[{"when": f"{d['from']}–{d['to']}", "title": f"{d['hanja']} · {d['start_age']}세",
                   "body": f"{d['stem_god']} / {d['branch_god']}",
                   "now": d["from"] <= today.year <= d["to"]} for d in a.daeun_years[:8]],
        evidence=[f"{'순행' if chart.luck_forward else '역행'} {chart.luck_start_age}세 시작"]))

    sections.append(_sec("year", "年", "올해", "올해와 내년", "",
        cards=[{"title": f"{y.year} {y.hanja}", "badge": " · ".join(y.tags) or "평", "body": f"{y.stem_god} / {y.branch_god}"} for y in a.years[:2]],
        evidence=[f"{y.year} {y.hanja}: {y.stem_god}/{y.branch_god}" for y in a.years[:2]]))

    color, direction, num, season, habit = EL_LUCK[ys]
    sections.append(_sec("luck", "福", "개운법", "운을 여는 법", f"용신 {ys}({EL_KO[ys]})",
        stats=[{"label": "행운의 색", "value": color}, {"label": "방향", "value": direction},
               {"label": "숫자", "value": num}, {"label": "계절", "value": season}],
        lead=habit, evidence=[f"용신 {ys}"]))


    cur = next((d for d in a.daeun_years if d["from"] <= today.year <= d["to"]), a.daeun_years[0])
    nxt = [d for d in a.daeun_years if d["from"] > today.year][:2]
    sections.append(_sec("future", "來", "앞으로", "앞으로 어떻게 살까", "시기별 숙제",
        lead=YONGSIN_RULE[a.yongsin_group],
        cards=[{"title": f"지금 ~ {cur['to']}", "badge": cur["hanja"],
                "body": f"{cur['stem_god']}·{cur['branch_god']} 대운의 한가운데. {habit}을 붙이면 이 10년이 훨씬 수월해져요."}]
              + [{"title": f"{d['from']} ~ {d['to']}", "badge": d["hanja"],
                  "body": f"{d['start_age']}세부터는 {GOD_FUTURE[d['stem_god']]} 후반엔 {GOD_FUTURE[d['branch_god']]}"}
                 for d in nxt],
        evidence=[f"용신 {ys}", f"현재 대운 {cur['hanja']}"] + [f"다음 대운 {d['hanja']}" for d in nxt]))

    sections.append(_sec("proof", "證", "근거", "이 풀이가 다른 이유", "그냥 LLM 사주와 무엇이 다른가",
        cards=[
            {"title": "만세력을 코드로 직접 계산", "body": f"태양 황경으로 절기를 계산하고, 출생 시각을 지방시로 보정했어요 ({chart.birth} → {chart.corrected_local}). 일반 챗봇은 날짜를 간지로 바꾸는 단계에서 자주 틀려요."},
            {"title": "지장간 · 합충 · 신살까지", "body": "겉 글자 8개만이 아니라 숨은 글자, 글자끼리의 관계, 신살, 15년치 연운을 모두 계산한 데이터에서 출발했어요."},
            {"title": "모든 문장에 근거", "body": "각 장 아래의 근거 칩이 그 해석이 어느 글자에서 나왔는지 보여줘요."},
            {"title": "사람이 검수", "body": "계산은 코드가, 해석은 AI 개발자가 직접 읽고 다듬었어요."},
        ],
        evidence=a.chart_relations + [f"{k}: {', '.join(v)}" for k, v in a.shinsal.items() if v]))

    return {
        "headline": f"{name} 님은 {image}의 기운을 가진 {role}",
        "sections": sections,
        "closing": "사주는 타고난 지도일 뿐, 어디로 걸어갈지는 내가 정해요.",
    }
