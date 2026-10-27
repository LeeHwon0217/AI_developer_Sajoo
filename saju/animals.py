"""12띠 동물 (민화풍). 사주 인트로 오른쪽 아래에서 고개를 내민다.

모두 호랑이와 같은 틀을 쓴다: viewBox 0 0 400 380, <g class="tiger-body"> 가 아래에서 올라오고,
<g class="eyes"> 가 깜빡이고, .pupil 이 두리번거린다 (style.css 의 애니메이션).
"""
from __future__ import annotations

from .art import TIGER

INK = "#2b1a0c"


def _eyes(lx: int, rx: int, y: int, r: int = 30, iris: str = "#f5d33a", pupil: int = 15, slit: bool = False) -> str:
    if slit:
        p = (f'<ellipse class="pupil" cx="{lx}" cy="{y}" rx="5" ry="{r - 6}" fill="{INK}"/>'
             f'<ellipse class="pupil" cx="{rx}" cy="{y}" rx="5" ry="{r - 6}" fill="{INK}"/>')
    else:
        p = (f'<circle class="pupil" cx="{lx + 4}" cy="{y + 3}" r="{pupil}" fill="{INK}"/>'
             f'<circle class="pupil" cx="{rx - 4}" cy="{y + 3}" r="{pupil}" fill="{INK}"/>')
    shine = (f'<circle cx="{lx + 9}" cy="{y - 5}" r="{max(3, r // 6)}" fill="#fff"/>'
             f'<circle cx="{rx + 1}" cy="{y - 5}" r="{max(3, r // 6)}" fill="#fff"/>')
    return (f'<g class="eyes"><circle cx="{lx}" cy="{y}" r="{r}" fill="{iris}" stroke="{INK}" stroke-width="5"/>'
            f'<circle cx="{rx}" cy="{y}" r="{r}" fill="{iris}" stroke="{INK}" stroke-width="5"/>{p}{shine}</g>')


def _wrap(name: str, body: str) -> str:
    return (f'<svg class="tiger animal-{name}" viewBox="0 0 400 380" aria-hidden="true">'
            f'<g class="tiger-body">{body}</g></svg>')


def _whiskers(y: int, color: str = INK) -> str:
    return (f'<g stroke="{color}" stroke-width="3" stroke-linecap="round">'
            f'<path d="M125 {y} l -70 -10"/><path d="M125 {y + 12} l -72 8"/>'
            f'<path d="M275 {y} l 70 -10"/><path d="M275 {y + 12} l 72 8"/></g>')


RAT = _wrap("rat", f"""
  <circle cx="90" cy="105" r="72" fill="#a39d96" stroke="{INK}" stroke-width="6"/><circle cx="90" cy="108" r="46" fill="#ecb9b4"/>
  <circle cx="310" cy="105" r="72" fill="#a39d96" stroke="{INK}" stroke-width="6"/><circle cx="310" cy="108" r="46" fill="#ecb9b4"/>
  <ellipse cx="200" cy="235" rx="150" ry="140" fill="#a39d96" stroke="{INK}" stroke-width="6"/>
  <ellipse cx="200" cy="292" rx="78" ry="58" fill="#e4ded6"/>
  {_eyes(140, 260, 210, 26, "#1d1d1d", 10)}
  <path d="M182 262 Q200 250 218 262 Q208 278 200 280 Q192 278 182 262 Z" fill="#e58a8a" stroke="{INK}" stroke-width="4"/>
  <rect x="188" y="292" width="11" height="18" rx="3" fill="#fff" stroke="{INK}" stroke-width="3"/>
  <rect x="201" y="292" width="11" height="18" rx="3" fill="#fff" stroke="{INK}" stroke-width="3"/>
  {_whiskers(278)}
  <ellipse cx="128" cy="262" rx="18" ry="10" fill="#e9a3a3" opacity=".6"/><ellipse cx="272" cy="262" rx="18" ry="10" fill="#e9a3a3" opacity=".6"/>
""")

OX = _wrap("ox", f"""
  <path d="M118 120 C 70 110 40 70 60 30 C 80 70 110 85 140 95 Z" fill="#efe2c2" stroke="{INK}" stroke-width="5"/>
  <path d="M282 120 C 330 110 360 70 340 30 C 320 70 290 85 260 95 Z" fill="#efe2c2" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="55" cy="175" rx="50" ry="26" fill="#8a5a35" stroke="{INK}" stroke-width="5" transform="rotate(-18 55 175)"/>
  <ellipse cx="345" cy="175" rx="50" ry="26" fill="#8a5a35" stroke="{INK}" stroke-width="5" transform="rotate(18 345 175)"/>
  <path d="M75 150 C 70 330 120 380 200 380 C 280 380 330 330 325 150 C 300 95 100 95 75 150 Z" fill="#8a5a35" stroke="{INK}" stroke-width="6"/>
  <path d="M180 108 Q200 160 220 108 Q212 180 200 200 Q188 180 180 108 Z" fill="#f4ead6"/>
  {_eyes(135, 265, 190, 26, "#3a2414", 12)}
  <ellipse cx="200" cy="300" rx="100" ry="62" fill="#e8cfae" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="165" cy="300" rx="14" ry="20" fill="{INK}"/><ellipse cx="235" cy="300" rx="14" ry="20" fill="{INK}"/>
  <path d="M175 340 q25 14 50 0" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
""")

RABBIT = _wrap("rabbit", f"""
  <ellipse cx="140" cy="70" rx="38" ry="110" fill="#f6f1e7" stroke="{INK}" stroke-width="6" transform="rotate(-10 140 70)"/>
  <ellipse cx="140" cy="78" rx="18" ry="80" fill="#efb6b8" transform="rotate(-10 140 78)"/>
  <ellipse cx="260" cy="70" rx="38" ry="110" fill="#f6f1e7" stroke="{INK}" stroke-width="6" transform="rotate(10 260 70)"/>
  <ellipse cx="260" cy="78" rx="18" ry="80" fill="#efb6b8" transform="rotate(10 260 78)"/>
  <ellipse cx="200" cy="250" rx="150" ry="135" fill="#f6f1e7" stroke="{INK}" stroke-width="6"/>
  {_eyes(140, 260, 225, 26, "#c8323a", 12)}
  <path d="M186 272 Q200 262 214 272 Q206 286 200 287 Q194 286 186 272 Z" fill="#e58a8a" stroke="{INK}" stroke-width="4"/>
  <path d="M200 287 v14 M200 301 q-14 12 -28 4 M200 301 q14 12 28 4" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
  {_whiskers(285)}
  <ellipse cx="118" cy="275" rx="22" ry="12" fill="#f0a9ae" opacity=".7"/><ellipse cx="282" cy="275" rx="22" ry="12" fill="#f0a9ae" opacity=".7"/>
""")

DRAGON = _wrap("dragon", f"""
  <g fill="none" stroke="#d9a441" stroke-width="12" stroke-linecap="round">
    <path d="M130 120 C 110 70 120 40 95 15 M118 75 C 95 70 80 55 70 40"/>
    <path d="M270 120 C 290 70 280 40 305 15 M282 75 C 305 70 320 55 330 40"/>
  </g>
  <path d="M60 210 C 30 160 70 150 70 120 C 100 150 110 110 140 120 C 160 90 240 90 260 120 C 290 110 300 150 330 120 C 330 150 370 160 340 210 Z" fill="#c8321e" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="200" cy="245" rx="150" ry="135" fill="#3f8f7f" stroke="{INK}" stroke-width="6"/>
  <g fill="none" stroke="#2d6b5f" stroke-width="4"><path d="M120 160 q15 -14 30 0 q15 -14 30 0"/><path d="M220 160 q15 -14 30 0 q15 -14 30 0"/></g>
  <path d="M100 175 q40 -30 80 -6 M300 175 q-40 -30 -80 -6" fill="none" stroke="#c8321e" stroke-width="12" stroke-linecap="round"/>
  {_eyes(140, 260, 210, 32, "#f5d33a", 13)}
  <ellipse cx="200" cy="300" rx="95" ry="55" fill="#7cc0ad" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="170" cy="282" rx="10" ry="7" fill="{INK}"/><ellipse cx="230" cy="282" rx="10" ry="7" fill="{INK}"/>
  <path d="M150 318 q50 26 100 0" fill="none" stroke="{INK}" stroke-width="5"/>
  <path d="M162 322 l8 18 l8 -14 M222 322 l8 14 l8 -18" fill="#fff" stroke="{INK}" stroke-width="3"/>
  <g fill="none" stroke="#d9a441" stroke-width="6" stroke-linecap="round">
    <path d="M120 300 C 70 300 40 330 20 370"/><path d="M280 300 C 330 300 360 330 380 370"/>
  </g>
""")

SNAKE = _wrap("snake", f"""
  <ellipse cx="200" cy="350" rx="190" ry="55" fill="#6b9a4a" stroke="{INK}" stroke-width="6"/>
  <ellipse cx="200" cy="330" rx="140" ry="40" fill="#7fae5a" stroke="{INK}" stroke-width="5"/>
  <path d="M150 330 C 140 270 150 230 200 220 C 250 230 260 270 250 330 Z" fill="#6b9a4a" stroke="{INK}" stroke-width="6"/>
  <ellipse cx="200" cy="175" rx="125" ry="100" fill="#6b9a4a" stroke="{INK}" stroke-width="6"/>
  <g fill="#4d7a32"><path d="M200 95 l14 18 l-14 18 l-14 -18 Z"/><path d="M160 120 l12 15 l-12 15 l-12 -15 Z"/><path d="M240 120 l12 15 l-12 15 l-12 -15 Z"/></g>
  {_eyes(150, 250, 170, 28, "#f2c230", 0, slit=True)}
  <ellipse cx="185" cy="218" rx="5" ry="3" fill="{INK}"/><ellipse cx="215" cy="218" rx="5" ry="3" fill="{INK}"/>
  <path d="M150 240 q50 22 100 0" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  <path class="tongue" d="M200 250 v30 l-12 14 M200 280 l12 14" fill="none" stroke="#c8321e" stroke-width="6" stroke-linecap="round"/>
""")

HORSE = _wrap("horse", f"""
  <path d="M120 105 L 95 20 L 160 75 Z" fill="#a0522d" stroke="{INK}" stroke-width="5"/>
  <path d="M280 105 L 305 20 L 240 75 Z" fill="#a0522d" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="200" cy="225" rx="115" ry="165" fill="#a0522d" stroke="{INK}" stroke-width="6"/>
  <path d="M120 85 C 150 40 250 40 280 85 C 260 70 240 110 215 90 C 200 120 175 80 160 105 C 150 85 130 100 120 85 Z" fill="#3b2416"/>
  <path d="M188 110 Q200 140 212 110 Q210 200 200 230 Q190 200 188 110 Z" fill="#f4ead6"/>
  {_eyes(135, 265, 185, 26, "#3a2414", 13)}
  <ellipse cx="200" cy="320" rx="85" ry="58" fill="#d9a77f" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="170" cy="318" rx="11" ry="16" fill="{INK}"/><ellipse cx="230" cy="318" rx="11" ry="16" fill="{INK}"/>
  <path d="M175 352 q25 12 50 0" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
""")

SHEEP = _wrap("sheep", f"""
  <g fill="#f5efe2" stroke="{INK}" stroke-width="5">
    <circle cx="120" cy="105" r="45"/><circle cx="170" cy="75" r="48"/><circle cx="230" cy="75" r="48"/><circle cx="280" cy="105" r="45"/>
    <circle cx="80" cy="170" r="42"/><circle cx="320" cy="170" r="42"/><circle cx="70" cy="240" r="40"/><circle cx="330" cy="240" r="40"/>
  </g>
  <path d="M95 175 C 40 150 20 230 70 245 C 100 255 115 225 95 210" fill="none" stroke="#c9a46b" stroke-width="18" stroke-linecap="round"/>
  <path d="M305 175 C 360 150 380 230 330 245 C 300 255 285 225 305 210" fill="none" stroke="#c9a46b" stroke-width="18" stroke-linecap="round"/>
  <ellipse cx="200" cy="240" rx="115" ry="135" fill="#ece0cd" stroke="{INK}" stroke-width="6"/>
  <g fill="#f5efe2" stroke="{INK}" stroke-width="4"><circle cx="165" cy="118" r="26"/><circle cx="200" cy="108" r="28"/><circle cx="235" cy="118" r="26"/></g>
  {_eyes(155, 245, 215, 24, "#c9a46b", 10)}
  <path d="M186 290 Q200 280 214 290 Q206 302 200 303 Q194 302 186 290 Z" fill="#c98f8f" stroke="{INK}" stroke-width="4"/>
  <path d="M200 303 v12 M200 315 q-14 10 -26 2 M200 315 q14 10 26 2" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="140" cy="270" rx="18" ry="10" fill="#efb0ae" opacity=".7"/><ellipse cx="260" cy="270" rx="18" ry="10" fill="#efb0ae" opacity=".7"/>
""")

MONKEY = _wrap("monkey", f"""
  <circle cx="60" cy="205" r="55" fill="#8b5a3c" stroke="{INK}" stroke-width="6"/><circle cx="60" cy="205" r="32" fill="#f0c9a0"/>
  <circle cx="340" cy="205" r="55" fill="#8b5a3c" stroke="{INK}" stroke-width="6"/><circle cx="340" cy="205" r="32" fill="#f0c9a0"/>
  <ellipse cx="200" cy="225" rx="150" ry="150" fill="#8b5a3c" stroke="{INK}" stroke-width="6"/>
  <path d="M200 130 C 150 95 85 125 95 200 C 100 250 130 270 150 290 C 170 330 230 330 250 290 C 270 270 300 250 305 200 C 315 125 250 95 200 130 Z" fill="#f0c9a0" stroke="{INK}" stroke-width="5"/>
  {_eyes(150, 250, 200, 26, "#5a3a22", 13)}
  <ellipse cx="190" cy="262" rx="5" ry="7" fill="{INK}"/><ellipse cx="210" cy="262" rx="5" ry="7" fill="{INK}"/>
  <path d="M160 290 q40 30 80 0" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="130" cy="262" rx="16" ry="9" fill="#e79a8a" opacity=".7"/><ellipse cx="270" cy="262" rx="16" ry="9" fill="#e79a8a" opacity=".7"/>
""")

ROOSTER = _wrap("rooster", f"""
  <g fill="#d9381e" stroke="{INK}" stroke-width="5"><circle cx="160" cy="70" r="34"/><circle cx="205" cy="50" r="40"/><circle cx="250" cy="72" r="32"/></g>
  <g fill="#e0a526" stroke="{INK}" stroke-width="4"><path d="M60 260 C 40 200 80 160 110 170 C 80 200 80 240 100 280 Z"/><path d="M340 260 C 360 200 320 160 290 170 C 320 200 320 240 300 280 Z"/></g>
  <ellipse cx="200" cy="225" rx="135" ry="145" fill="#f6ead0" stroke="{INK}" stroke-width="6"/>
  <path d="M110 300 C 120 360 280 360 290 300 C 260 330 140 330 110 300 Z" fill="#e0a526"/>
  {_eyes(145, 255, 190, 25, "#f08a24", 11)}
  <path d="M168 225 L 232 225 L 200 275 Z" fill="#f2c230" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
  <path d="M175 246 L 225 246" stroke="{INK}" stroke-width="3"/>
  <path d="M185 275 C 175 320 225 320 215 275 Z" fill="#d9381e" stroke="{INK}" stroke-width="4"/>
""")

DOG = _wrap("dog", f"""
  <path d="M95 160 L 85 30 L 175 100 Z" fill="#d9a45a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M110 140 L 105 65 L 155 105 Z" fill="#f2dcb5"/>
  <path d="M305 160 L 315 30 L 225 100 Z" fill="#d9a45a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M290 140 L 295 65 L 245 105 Z" fill="#f2dcb5"/>
  <ellipse cx="200" cy="235" rx="150" ry="140" fill="#d9a45a" stroke="{INK}" stroke-width="6"/>
  <path d="M120 250 C 130 330 270 330 280 250 C 260 220 140 220 120 250 Z" fill="#f6ecd8"/>
  <path d="M180 120 Q200 150 220 120 Q215 190 200 215 Q185 190 180 120 Z" fill="#f6ecd8"/>
  {_eyes(140, 260, 200, 26, "#5a3a1a", 13)}
  <ellipse cx="200" cy="260" rx="26" ry="18" fill="{INK}"/>
  <path d="M200 278 v12 M200 290 q-22 16 -40 2 M200 290 q22 16 40 2" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  <path d="M188 300 q12 34 24 0 Z" fill="#e58a8a" stroke="{INK}" stroke-width="3"/>
""")

PIG = _wrap("pig", f"""
  <path d="M85 140 L 70 45 L 165 95 Z" fill="#f2a9a6" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M100 125 L 92 70 L 145 100 Z" fill="#e88b8b"/>
  <path d="M315 140 L 330 45 L 235 95 Z" fill="#f2a9a6" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M300 125 L 308 70 L 255 100 Z" fill="#e88b8b"/>
  <ellipse cx="200" cy="235" rx="160" ry="145" fill="#f2a9a6" stroke="{INK}" stroke-width="6"/>
  {_eyes(135, 265, 195, 22, "#3a2414", 11)}
  <ellipse cx="200" cy="275" rx="62" ry="44" fill="#e8898a" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="180" cy="275" rx="11" ry="17" fill="{INK}"/><ellipse cx="220" cy="275" rx="11" ry="17" fill="{INK}"/>
  <path d="M170 335 q30 16 60 0" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="110" cy="265" rx="22" ry="12" fill="#ec8f94" opacity=".8"/><ellipse cx="290" cy="265" rx="22" ry="12" fill="#ec8f94" opacity=".8"/>
""")

ANIMALS = {"子": RAT, "丑": OX, "寅": TIGER, "卯": RABBIT, "辰": DRAGON, "巳": SNAKE,
           "午": HORSE, "未": SHEEP, "申": MONKEY, "酉": ROOSTER, "戌": DOG, "亥": PIG}
ANIMAL_KO = {"子": "쥐", "丑": "소", "寅": "호랑이", "卯": "토끼", "辰": "용", "巳": "뱀",
             "午": "말", "未": "양", "申": "원숭이", "酉": "닭", "戌": "개", "亥": "돼지"}
