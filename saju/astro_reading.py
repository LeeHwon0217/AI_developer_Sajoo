"""출생 차트 → 점성술 풀이 섹션 (사주 풀이와 같은 섹션 모양).

섹션에는 en(영문 소제목)과 key 가 있고, key == "wheel" 이면 렌더러가 호로스코프 휠을 그린다.
"""
from __future__ import annotations

from datetime import date

from .astro import GLYPH, PLANET_GLYPH, SIGN_ELEMENT, SIGNS, SIGNS_EN, AstroChart

# 별자리별 성향 (태양=본질, 달=감정, 상승=첫인상, 금성=사랑, 화성=행동, 수성=생각)
SIGN = {
    0: dict(key="개척자", sun="먼저 부딪히고 먼저 길을 여는 사람. 솔직하고 뜨겁고, 기다리는 걸 못 참아요.",
            moon="감정이 빠르게 끓고 빠르게 식어요. 속에 담아 두기보다 바로 털어내는 쪽.",
            asc="첫인상이 시원시원하고 에너지가 넘쳐 보여요.",
            venus="좋아하면 먼저 다가가는 직진형 사랑. 설렘이 식으면 금방 지루해해요.",
            mars="결단이 빠르고 추진력이 강해요. 경쟁이 붙으면 더 힘이 나요.",
            mercury="생각보다 말이 먼저 나가는 편. 핵심만 빠르게 짚어요."),
    1: dict(key="수집가", sun="천천히, 하지만 확실하게. 감각이 좋고 한 번 가진 건 오래 지켜요.",
            moon="익숙한 것, 맛있는 것, 편안한 공간에서 마음이 풀려요. 변화를 싫어해요.",
            asc="차분하고 믿음직해 보이고, 분위기가 부드러워요.",
            venus="오감으로 사랑하는 사람. 스킨십과 함께하는 시간, 선물로 마음을 표현해요.",
            mars="느리지만 끝까지 가요. 한 번 화나면 오래 가요.",
            mercury="천천히 생각하고 확실하게 결론 내요. 실용적인 생각을 좋아해요."),
    2: dict(key="소통가", sun="호기심이 많고 말이 재치 있어요. 여러 가지를 동시에 굴리는 사람.",
            moon="대화로 마음을 풀어요. 지루하면 마음이 먼저 떠나요.",
            asc="밝고 말을 잘하고 젊어 보여요.",
            venus="말이 통하는 사람에게 끌려요. 대화가 끊기면 사랑도 식어요.",
            mars="여러 일을 동시에 벌이는 순발력. 말로 싸우면 지지 않아요.",
            mercury="머리 회전이 빠르고 정보를 엮는 데 천재적이에요."),
    3: dict(key="보호자", sun="정이 깊고 가족과 내 사람을 지키는 데 온 힘을 써요.",
            moon="감정이 풍부하고 기억을 오래 품어요. 집과 가족이 마음의 기지.",
            asc="부드럽고 다정해 보여요. 처음 만난 사람도 편하게 해주는 분위기.",
            venus="돌봐주고 챙겨주는 사랑. 안정감이 있어야 마음을 열어요.",
            mars="내 사람을 건드리면 누구보다 강해져요. 돌려 말하는 편.",
            mercury="감정과 기억으로 생각해요. 공감 능력이 뛰어나요."),
    4: dict(key="주인공", sun="무대 위에서 빛나는 사람. 자존심이 강하고 마음이 넓어요.",
            moon="인정받고 사랑받을 때 마음이 채워져요. 서운함도 크게 느껴요.",
            asc="존재감이 크고 당당해 보여요.",
            venus="화끈하고 낭만적인 사랑. 상대를 자랑스러워하고 싶어 해요.",
            mars="자신감으로 밀어붙여요. 자존심이 걸리면 절대 안 물러서요.",
            mercury="말에 힘이 있고 설득력이 강해요."),
    5: dict(key="장인", sun="꼼꼼하고 성실해요. 쓸모 있는 사람이 되는 게 기쁨이에요.",
            moon="정리된 환경에서 마음이 편해요. 걱정이 많은 편.",
            asc="단정하고 똑똑해 보여요.",
            venus="작은 것까지 챙기는 섬세한 사랑. 말보다 실천으로 보여줘요.",
            mars="계획대로 차근차근 해내는 힘. 완벽주의가 발목을 잡기도 해요.",
            mercury="분석력과 정확성이 최고예요. 디테일을 놓치지 않아요."),
    6: dict(key="조율가", sun="균형과 조화를 중시하는 사람. 아름다운 것과 공정한 관계를 사랑해요.",
            moon="관계가 편해야 마음이 편해요. 갈등을 피하려 참는 편.",
            asc="세련되고 상냥해 보여요.",
            venus="로맨틱하고 우아한 사랑. 파트너와 함께일 때 더 빛나요.",
            mars="부드럽게 설득해서 움직여요. 결정을 미루는 게 약점.",
            mercury="양쪽을 다 보는 균형 잡힌 생각. 외교적인 말솜씨."),
    7: dict(key="탐구자", sun="깊고 강렬해요. 겉으론 조용해도 속에는 엄청난 집중력과 의지가 있어요.",
            moon="감정이 깊고 진해요. 쉽게 믿지 않지만 한 번 믿으면 끝까지 가요.",
            asc="신비롭고 쉽게 속을 알 수 없어 보여요.",
            venus="전부 아니면 전무. 깊고 뜨겁고 운명 같은 사랑을 원해요.",
            mars="목표가 정해지면 끝까지 파고들어요. 쉽게 포기하지 않아요.",
            mercury="겉말 뒤의 진짜 의도를 꿰뚫어 봐요."),
    8: dict(key="모험가", sun="자유롭고 낙천적이에요. 더 넓은 세상과 더 큰 의미를 찾아 떠나요.",
            moon="얽매이면 답답해해요. 여행과 배움이 마음의 숨통.",
            asc="밝고 유쾌하고 자유로워 보여요.",
            venus="함께 모험할 수 있는 사랑. 구속하면 멀어져요.",
            mars="큰 목표를 향해 단숨에 달려요. 세부는 약해요.",
            mercury="큰 그림을 보고 철학적으로 생각해요. 솔직한 말투."),
    9: dict(key="설계자", sun="책임감 있고 야망이 커요. 시간이 걸려도 결국 정상에 오르는 사람.",
            moon="감정을 잘 드러내지 않아요. 할 일을 해야 마음이 편해요.",
            asc="어른스럽고 믿음직해 보여요.",
            venus="진지하고 신중한 사랑. 천천히, 하지만 오래 가는 관계를 원해요.",
            mars="계획적이고 끈기 있게 목표를 이뤄요. 인내심이 무기.",
            mercury="현실적이고 체계적으로 생각해요."),
    10: dict(key="혁신가", sun="남들과 다른 길을 가는 사람. 독창적이고 미래를 먼저 봐요. 자유와 우정을 사랑해요.",
             moon="감정도 한 발 떨어져서 바라봐요. 친구 같은 관계에서 편안해요.",
             asc="독특하고 개성 있어 보여요.",
             venus="친구 같은 사랑. 서로의 자유를 존중하는 관계를 원해요.",
             mars="새로운 방식으로 판을 바꾸고 싶어 해요. 반골 기질.",
             mercury="독창적이고 앞서가는 생각. 아이디어가 남들보다 몇 걸음 빨라요."),
    11: dict(key="몽상가", sun="감수성이 풍부하고 공감 능력이 뛰어나요. 예술과 꿈의 세계에 사는 사람.",
             moon="다른 사람의 감정을 내 것처럼 느껴요. 혼자만의 시간이 꼭 필요해요.",
             asc="부드럽고 몽환적인 분위기예요.",
             venus="헌신적이고 낭만적인 사랑. 상대를 이상화하는 경향이 있어요.",
             mars="흐름을 타며 움직여요. 직감으로 길을 찾아요.",
             mercury="상상력과 직관으로 생각해요. 말보다 이미지로 기억해요."),
}
HOUSE = {1: "나 자신과 첫인상", 2: "돈과 가치", 3: "배움과 소통", 4: "집과 가족", 5: "연애와 창작", 6: "일상과 건강",
         7: "배우자와 파트너", 8: "깊은 변화와 공동의 재산", 9: "해외와 배움, 신념", 10: "일과 명예", 11: "친구와 꿈", 12: "쉼과 내면"}
ELEMENT_TEXT = {
    "불": ("열정과 실행", "마음먹은 걸 바로 행동으로 옮기는 힘"),
    "흙": ("현실과 안정", "꾸준히 쌓고 결과를 손에 쥐는 힘"),
    "공기": ("생각과 소통", "아이디어를 내고 사람을 잇는 힘"),
    "물": ("감정과 직관", "느끼고 공감하고 꿰뚫어 보는 힘"),
}
RETURN_TEXT = {
    "목성 회귀": "12년마다 오는 새 출발. 기회와 성장이 한꺼번에 열리는 해예요.",
    "토성 사각": "성장통의 해. 압박 속에서 중요한 선택을 하게 돼요.",
    "토성 대립": "바깥 세상과 부딪히며 균형을 배우는 해예요.",
    "토성 회귀": "진짜 어른이 되는 시험. 삶의 틀을 다시 짜고 책임을 받아들이는 해예요.",
}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII",
         "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


def _sec(key, glyph, nav, en, title, sub="", **kw) -> dict:
    return {"key": key, "hanja": glyph, "nav": nav, "en": en, "title": title, "sub": sub, **kw}


def _where(c: AstroChart, name: str) -> str:
    b = c.body(name)
    h = f" · {b.house}하우스" if b.house else ""
    return f"{name} {SIGNS[b.sign]} {int(b.deg)}°{h}{' (역행)' if b.retro else ''}"


def draft_astro(c: AstroChart, name: str, saju: dict | None = None, today: date | None = None) -> dict:
    today = today or date.today()
    sun, moon = c.body("태양"), c.body("달")
    ven, mar, mer, jup, sat = (c.body(n) for n in ("금성", "화성", "수성", "목성", "토성"))
    asc = c.asc_sign
    big3 = f"태양 {SIGNS[sun.sign]} · 달 {SIGNS[moon.sign]}" + (f" · 상승 {SIGNS[asc]}" if asc is not None else "")
    els = c.elements
    top = max(els, key=els.get)
    low = [e for e, v in els.items() if v <= 1]
    sections = []

    sections.append(_sec("wheel", "✶", "차트", "THE NATAL CHART", "하늘의 지도", "태어난 순간의 하늘",
        lead=f"{name} 님이 태어난 순간, 하늘은 이렇게 생겼어요.",
        stats=[{"label": "태양 · 본질", "value": f"{SIGNS[sun.sign]}", "sub": f"{SIGNS_EN[sun.sign]} {int(sun.deg)}°"},
               {"label": "달 · 감정", "value": f"{SIGNS[moon.sign]}", "sub": f"{SIGNS_EN[moon.sign]} {int(moon.deg)}°" + (" · 하루 중 바뀜" if c.moon_uncertain else "")}]
              + ([{"label": "상승 · 첫인상", "value": SIGNS[asc], "sub": f"{SIGNS_EN[asc]} {int(c.asc % 30)}°"}] if asc is not None else []),
        evidence=[_where(c, n) for n in ("태양", "달")] + ([f"ASC {SIGNS[asc]} {int(c.asc % 30)}°"] if asc is not None else ["생시 모름: 상승궁·하우스 없음"])))

    sections.append(_sec("sun", GLYPH[sun.sign], "태양", "THE SUN", f"태양 {SIGNS[sun.sign]}", "나의 본질",
        lead=SIGN[sun.sign]["sun"],
        paras=[f"태양은 인생의 중심 테마예요. {SIGNS[sun.sign]}의 '{SIGN[sun.sign]['key']}' 기질이 평생의 방향을 정해요."]
              + ([f"태양이 {sun.house}하우스({HOUSE[sun.house]})에 있어, 이 영역에서 가장 빛나요."] if sun.house else []),
        evidence=[_where(c, "태양")]))

    sections.append(_sec("moon", GLYPH[moon.sign], "달", "THE MOON", f"달 {SIGNS[moon.sign]}", "속마음과 감정",
        lead=SIGN[moon.sign]["moon"],
        paras=["달은 남들이 잘 모르는 속마음, 편안함을 느끼는 방식이에요."]
              + ([f"달이 {moon.house}하우스({HOUSE[moon.house]})에 있어, 이 영역에서 마음이 가장 크게 움직여요."] if moon.house else [])
              + (["※ 태어난 날 하루 사이에 달이 별자리를 옮겨서, 생시를 알면 더 정확해져요."] if c.moon_uncertain else []),
        evidence=[_where(c, "달")]))

    if asc is not None:
        sections.append(_sec("asc", GLYPH[asc], "상승궁", "THE ASCENDANT", f"상승 {SIGNS[asc]}", "남들이 보는 첫인상",
            lead=SIGN[asc]["asc"],
            paras=["상승궁은 태어난 순간 동쪽 지평선에 떠오르던 별자리예요. 세상을 대하는 첫 태도, 남들 눈에 비친 나예요."],
            evidence=[f"ASC {SIGNS[asc]} {int(c.asc % 30)}°"]))

    sections.append(_sec("mercury", PLANET_GLYPH["수성"], "수성", "MERCURY", f"수성 {SIGNS[mer.sign]}", "생각하고 말하는 방식",
        lead=SIGN[mer.sign]["mercury"], evidence=[_where(c, "수성")]))
    sections.append(_sec("venus", PLANET_GLYPH["금성"], "금성", "VENUS", f"금성 {SIGNS[ven.sign]}", "사랑하는 방식",
        lead=SIGN[ven.sign]["venus"], evidence=[_where(c, "금성")]))
    sections.append(_sec("mars", PLANET_GLYPH["화성"], "화성", "MARS", f"화성 {SIGNS[mar.sign]}", "움직이는 힘",
        lead=SIGN[mar.sign]["mars"], evidence=[_where(c, "화성")]))

    total = sum(els.values()) or 1
    sections.append(_sec("elements", "△", "원소", "THE ELEMENTS", "네 원소의 균형", f"{top}이 가장 강해요",
        bars=[{"label": f"{e} · {ELEMENT_TEXT[e][0]}", "value": round(v / total * 100), "note": ELEMENT_TEXT[e][1]} for e, v in els.items()],
        paras=[f"가장 강한 원소는 {top}({ELEMENT_TEXT[top][0]})" + (f", 부족한 원소는 {', '.join(low)}이에요." if low else "이에요.")],
        evidence=[f"{e} {v}" for e, v in els.items()]))

    if c.mc_sign is not None:
        tenth = [b.name for b in c.bodies if b.house == 10]
        sections.append(_sec("career", "⌂", "일", "VOCATION", "일과 사명", f"중천 {SIGNS[c.mc_sign]}",
            lead=f"사회에서 이루고 싶은 모습은 {SIGNS[c.mc_sign]}의 '{SIGN[c.mc_sign]['key']}'.",
            paras=[f"10하우스에 {', '.join(tenth)}이(가) 있어요." if tenth else "10하우스가 비어 있어, 일보다 다른 영역에서 더 큰 의미를 찾을 수 있어요."],
            evidence=[f"MC {SIGNS[c.mc_sign]} {int(c.mc % 30)}°"] + [_where(c, n) for n in tenth]))

    past = [{"when": f"{r['year']} · {r['age']}세", "title": r["what"], "body": RETURN_TEXT[r["what"]], "now": False}
            for r in c.returns if r["year"] < today.year]
    if past:
        sections.append(_sec("past", "↺", "지나온 길", "THE PAST", "지나온 길", "목성과 토성의 주기",
            lead="큰 행성들이 내 차트의 같은 자리로 돌아올 때마다 삶의 마디가 생겨요.",
            timeline=past[:8], evidence=[f"{r['what']} {r['year']}" for r in c.returns if r["year"] < today.year][:6]))

    ahead = [{"when": t["from"], "title": f"{t['planet']} → {SIGNS[t['sign']]}",
              "body": (f"{t['house']}하우스({HOUSE[t['house']]})" if t["house"] else f"태양에서 {t['from_sun']}번째 자리") +
                      (" 영역에 행운과 확장이 들어와요." if t["planet"] == "목성" else " 영역을 단단히 다지라는 시험이 와요."),
              "now": False} for t in c.transits]
    ahead += [{"when": str(r["year"]), "title": r["what"], "body": RETURN_TEXT[r["what"]], "now": False}
              for r in c.returns if r["year"] >= today.year]
    ahead.sort(key=lambda x: x["when"])
    sections.append(_sec("ahead", "→", "앞으로", "THE YEARS AHEAD", "앞으로의 흐름", "목성과 토성이 지나가는 길",
        timeline=ahead[:8], evidence=[f"{t['planet']} {SIGNS[t['sign']]} {t['from']}~" for t in c.transits][:6]))

    sections.append(_sec("proof", "✧", "근거", "THE METHOD", "이 별자리 풀이가 다른 이유", "계산은 천문학으로",
        cards=[
            {"title": "실제 하늘을 계산", "badge": "☉", "body": "태어난 시각의 태양·달·행성 위치를 천문 계산으로 구했어요. 태양 별자리만 보는 운세와 달리 열 개의 천체를 모두 봐요."},
            {"title": "상승궁까지", "badge": "↑", "body": f"태어난 곳({c.place})의 위도·경도와 시각으로 동쪽 지평선의 별자리를 계산했어요." if c.hour_known else "생시를 몰라 상승궁과 하우스는 빼고 봤어요."},
            {"title": "모든 장에 근거", "badge": "✧", "body": "각 장 아래 근거 칩에 행성의 정확한 위치를 적었어요."},
        ],
        evidence=[_where(c, n) for n in ("태양", "달", "수성", "금성", "화성", "목성", "토성")]))

    return {"headline": f"{name} 님은 {big3}", "sections": sections,
            "closing": "별은 길을 비출 뿐, 걸어가는 건 당신이에요."}
