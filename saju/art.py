"""인트로 장면에 쓰는 민화풍 SVG 조각들.

각 조각은 따로 absolute 배치되어 화면 비율이 바뀌어도 잘리지 않는다.
애니메이션은 style.css 의 클래스 이름으로 건다.
"""

# 일월오봉도: 해, 달, 다섯 봉우리, 물결
SCENE = """<svg class="scene" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
  <defs>
    <linearGradient id="g-peak" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3f8f7f"/><stop offset="1" stop-color="#1f4f4a"/>
    </linearGradient>
    <linearGradient id="g-peak2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5ea48d"/><stop offset="1" stop-color="#2b6559"/>
    </linearGradient>
    <pattern id="p-wave" width="60" height="30" patternUnits="userSpaceOnUse">
      <rect width="60" height="30" fill="#1f4e79"/>
      <g fill="none" stroke="#e9eef2" stroke-width="2.2">
        <circle cx="30" cy="30" r="27"/><circle cx="30" cy="30" r="18"/><circle cx="30" cy="30" r="9"/>
        <circle cx="0" cy="15" r="27"/><circle cx="0" cy="15" r="18"/><circle cx="0" cy="15" r="9"/>
        <circle cx="60" cy="15" r="27"/><circle cx="60" cy="15" r="18"/><circle cx="60" cy="15" r="9"/>
      </g>
    </pattern>
  </defs>

  <g class="sun"><circle cx="1260" cy="210" r="92" fill="#d9381e"/><circle cx="1260" cy="210" r="112" fill="none" stroke="#d9381e" stroke-opacity=".25" stroke-width="10"/></g>
  <g class="moon"><circle cx="340" cy="190" r="70" fill="#fbf7ec" stroke="#c9b98f" stroke-width="4"/></g>

  <g class="peaks">
    <path class="pk pk1" d="M-80 900 C -20 760 70 650 150 640 C 230 650 320 760 380 900 Z" fill="url(#g-peak2)"/>
    <path class="pk pk5" d="M1220 900 C 1280 760 1370 650 1450 640 C 1530 650 1620 760 1680 900 Z" fill="url(#g-peak2)"/>
    <path class="pk pk2" d="M230 900 C 290 700 380 545 460 535 C 540 545 630 700 690 900 Z" fill="url(#g-peak)"/>
    <path class="pk pk4" d="M910 900 C 970 700 1060 545 1140 535 C 1220 545 1310 700 1370 900 Z" fill="url(#g-peak)"/>
    <path class="pk pk3" d="M560 900 C 620 620 710 370 800 355 C 890 370 980 620 1040 900 Z" fill="url(#g-peak)"/>
    <g fill="none" stroke="#e8f0da" stroke-opacity=".45" stroke-width="5" stroke-linecap="round">
      <path class="pk pk3" d="M800 380 C 770 470 740 560 715 700"/><path class="pk pk3" d="M800 380 C 830 470 860 560 885 700"/>
      <path class="pk pk2" d="M460 560 C 440 620 420 690 405 780"/><path class="pk pk4" d="M1140 560 C 1160 620 1180 690 1195 780"/>
    </g>
  </g>

  <g class="waves"><rect x="-120" y="805" width="1840" height="100" fill="url(#p-wave)"/></g>
</svg>"""

CLOUD = """<svg class="cloud {cls}" viewBox="-10 -30 220 90" aria-hidden="true">
  <path d="M0 40 C -12 8 30 -14 52 8 C 62 -24 112 -24 122 8 C 142 -8 178 10 166 40 Z" fill="#fffaf0" stroke="#b99a6b" stroke-width="3"/>
  <path d="M166 40 c 26 0 36 -26 15 -31 c -11 -2 -15 9 -6 11" fill="none" stroke="#b99a6b" stroke-width="3" stroke-linecap="round"/>
  <path d="M30 40 c -2 -12 10 -18 18 -10" fill="none" stroke="#b99a6b" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""

# 단정학. 왼쪽을 보고 난다.
CRANE = """<svg class="crane {cls}" viewBox="-210 -170 380 210" aria-hidden="true">
  <g class="wing-far"><path d="M-10 0 C 0 50 50 85 110 95 C 80 60 60 30 30 5 Z" fill="#ece6d8" stroke="#3a3a3a" stroke-width="2"/></g>
  <path d="M58 6 L150 14 M58 10 L148 22" stroke="#3a3a3a" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="0" cy="0" rx="70" ry="22" fill="#fffdf7" stroke="#3a3a3a" stroke-width="2"/>
  <path d="M52 -6 Q 88 -2 74 16 Q 62 10 48 9 Z" fill="#1d1d1d"/>
  <path d="M-55 -8 C -90 -22 -112 -32 -150 -30" fill="none" stroke="#1d1d1d" stroke-width="10" stroke-linecap="round"/>
  <circle cx="-153" cy="-30" r="9" fill="#fffdf7" stroke="#3a3a3a" stroke-width="1.5"/>
  <circle cx="-154" cy="-36" r="5" fill="#d9381e"/>
  <path d="M-160 -30 L-204 -23 L-160 -25 Z" fill="#c9a44a"/>
  <g class="wing-near">
    <path d="M-25 -10 C -12 -90 58 -140 122 -152 C 92 -102 70 -60 38 -12 Z" fill="#fffdf7" stroke="#3a3a3a" stroke-width="2"/>
    <path d="M122 -152 C 104 -128 92 -110 82 -96 L 74 -84 C 90 -112 104 -134 122 -152 Z M82 -96 C 96 -104 110 -126 122 -152" fill="#1d1d1d" stroke="#1d1d1d" stroke-width="7" stroke-linejoin="round"/>
  </g>
</svg>"""

# 소나무와 까치 (호작도의 왼쪽 절반)
PINE = """<svg class="pine" viewBox="0 0 520 620" aria-hidden="true">
  <path d="M90 640 C 120 520 60 420 140 320 C 190 255 175 205 230 160" fill="none" stroke="#5a3d24" stroke-width="34" stroke-linecap="round"/>
  <path d="M135 330 C 220 300 300 300 400 255" fill="none" stroke="#5a3d24" stroke-width="15" stroke-linecap="round"/>
  <path d="M190 230 C 250 210 300 175 340 130" fill="none" stroke="#5a3d24" stroke-width="11" stroke-linecap="round"/>
  <g fill="none" stroke="#7a5836" stroke-width="3" stroke-linecap="round">
    <path d="M100 560 q 14 -8 22 0"/><path d="M95 480 q 14 -8 22 0"/><path d="M118 400 q 14 -8 22 0"/>
  </g>
  <g class="needles">
    <ellipse cx="410" cy="245" rx="92" ry="30" fill="#2e5b3a"/><ellipse cx="410" cy="236" rx="78" ry="18" fill="#3f7a4d"/>
    <ellipse cx="240" cy="150" rx="90" ry="30" fill="#2e5b3a"/><ellipse cx="240" cy="141" rx="76" ry="18" fill="#3f7a4d"/>
    <ellipse cx="350" cy="120" rx="70" ry="24" fill="#2e5b3a"/><ellipse cx="350" cy="113" rx="58" ry="14" fill="#3f7a4d"/>
    <ellipse cx="120" cy="300" rx="80" ry="26" fill="#2e5b3a"/><ellipse cx="120" cy="292" rx="66" ry="15" fill="#3f7a4d"/>
  </g>
  <g class="magpie">
    <path d="M300 262 L 252 300 L 262 302 L 306 270 Z" fill="#1d2433"/>
    <ellipse cx="320" cy="252" rx="30" ry="18" fill="#1d2433"/>
    <ellipse cx="324" cy="258" rx="18" ry="10" fill="#fbf7ec"/>
    <path d="M300 246 q 20 -12 38 -4 q -18 4 -30 14 Z" fill="#2f5d8a"/>
    <circle cx="350" cy="238" r="13" fill="#1d2433"/>
    <circle cx="354" cy="235" r="3" fill="#fbf7ec"/>
    <path d="M362 238 L 376 241 L 362 243 Z" fill="#1d2433"/>
    <path d="M316 268 l -3 12 M326 268 l 2 12" stroke="#1d2433" stroke-width="3" stroke-linecap="round"/>
  </g>
</svg>"""

# 까치호랑이 얼굴. 아래에서 고개를 내민다.
TIGER = """<svg class="tiger" viewBox="0 0 400 380" aria-hidden="true">
  <g class="tiger-body">
    <circle cx="95" cy="80" r="44" fill="#e8892b" stroke="#2b1a0c" stroke-width="5"/>
    <circle cx="95" cy="84" r="24" fill="#f6dcb8"/>
    <circle cx="305" cy="80" r="44" fill="#e8892b" stroke="#2b1a0c" stroke-width="5"/>
    <circle cx="305" cy="84" r="24" fill="#f6dcb8"/>
    <ellipse cx="200" cy="215" rx="175" ry="160" fill="#e8892b" stroke="#2b1a0c" stroke-width="6"/>
    <g fill="none" stroke="#2b1a0c" stroke-width="12" stroke-linecap="round">
      <path d="M200 62 v 46"/><path d="M164 70 q 12 28 0 52"/><path d="M236 70 q -12 28 0 52"/>
      <path d="M30 180 q 40 4 58 30"/><path d="M28 225 q 42 -2 54 24"/><path d="M40 270 q 36 -6 50 14"/>
      <path d="M370 180 q -40 4 -58 30"/><path d="M372 225 q -42 -2 -54 24"/><path d="M360 270 q -36 -6 -50 14"/>
    </g>
    <ellipse cx="152" cy="280" rx="66" ry="50" fill="#fbf3e4"/>
    <ellipse cx="248" cy="280" rx="66" ry="50" fill="#fbf3e4"/>
    <g class="eyes">
      <circle cx="135" cy="185" r="38" fill="#f5d33a" stroke="#2b1a0c" stroke-width="6"/>
      <circle cx="265" cy="185" r="38" fill="#f5d33a" stroke="#2b1a0c" stroke-width="6"/>
      <circle class="pupil" cx="140" cy="188" r="17" fill="#2b1a0c"/>
      <circle class="pupil" cx="260" cy="188" r="17" fill="#2b1a0c"/>
      <circle cx="146" cy="181" r="6" fill="#fff"/><circle cx="266" cy="181" r="6" fill="#fff"/>
    </g>
    <path d="M110 140 q 25 -16 50 -4 M240 136 q 25 -12 50 4" fill="none" stroke="#fbf3e4" stroke-width="9" stroke-linecap="round"/>
    <path d="M174 248 Q 200 232 226 248 Q 214 274 200 276 Q 186 274 174 248 Z" fill="#c2453a" stroke="#2b1a0c" stroke-width="4"/>
    <path d="M200 276 q 0 22 -32 28 M200 276 q 0 22 32 28" fill="none" stroke="#2b1a0c" stroke-width="5" stroke-linecap="round"/>
    <g stroke="#2b1a0c" stroke-width="3" stroke-linecap="round">
      <path d="M120 280 l -70 -10"/><path d="M120 292 l -72 8"/><path d="M280 280 l 70 -10"/><path d="M280 292 l 72 8"/>
    </g>
    <g fill="#2b1a0c"><circle cx="140" cy="270" r="3.5"/><circle cx="130" cy="285" r="3.5"/><circle cx="260" cy="270" r="3.5"/><circle cx="270" cy="285" r="3.5"/></g>
  </g>
</svg>"""


def intro_layers() -> str:
    clouds = "".join(CLOUD.format(cls=f"c{i}") for i in range(1, 6))
    cranes = CRANE.format(cls="cr1") + CRANE.format(cls="cr2")
    return SCENE + clouds + cranes + PINE + TIGER
