# AI 개발자가 봐주는 사주

만세력으로 사주 원국을 계산하고, 쉬운 우리말로 풀이한 20장짜리 결과 페이지를 GitHub Pages 에 올린다.
풀이는 개발 용어 없이 평범한 사주 풀이처럼 쓴다. 모든 장에 해석의 근거 글자를 단다.

## 신청 한 건 처리하기

```bash
# 1. 계산 + 규칙 기반 초안 → readings/<slug>.json
py -3.12 -m saju new --name 닉네임 --birth "1995-03-02 14:30" --gender M --note "이직 고민"

# 2. readings/<slug>.json 의 "reading" 부분을 직접 다듬는다 (chart 는 건드리지 않기)

# 3. 정적 사이트 생성 → docs/
py -3.12 -m saju build

# 4. 올리기
git add . && git commit -m "사주: 닉네임" && git push
```

결과 주소: `https://<깃허브아이디>.github.io/<레포>/<slug>/` 를 신청자에게 보내준다.

- 음력 생일이면 `--lunar` 를 붙인다 (윤달이면 `--leap` 도). 양력으로 바꿔서 계산한다.
- 시간을 모르면 `--birth 1995-03-02` 처럼 날짜만 넣는다 (시주 없이 세 기둥).
- 서울이 아닌 곳에서 태어났으면 `--lon 129.0` (부산) 처럼 경도를 넣는다.
- `--llm anthropic` 을 주면 초안을 Claude 가 다시 쓴다 (`pip install anthropic`, `ANTHROPIC_API_KEY` 필요).
  다른 LLM 은 `saju/llm.py` 의 `PROVIDERS` 에 함수 하나를 추가하면 된다.

## 계산 기준

| 항목 | 기준 |
|---|---|
| 년주 | 입춘(태양 황경 315°) 기준 |
| 월주 | 12절 기준, 황경 직접 계산 (오차 약 10분 이내) |
| 일주 | 23시(子시)부터 다음 날 |
| 시주 | 출생지 경도로 지방시 보정 (서울 약 -32분) |
| 서머타임 | 1987·1988년 자동 보정 (그 외 연도는 미적용) |
| 대운 | 양남음녀 순행 / 음남양녀 역행, 절입까지 일수 ÷ 3 |

절입 시각 15분 이내에 태어난 경우 `new` 가 경고를 띄운다. 다른 만세력과 대조해 볼 것.

## GitHub Pages 설정 (처음 한 번)

1. GitHub 에 레포를 만들고 이 폴더를 push
2. 레포 Settings → Pages → Source: `Deploy from a branch`, Branch: `main` / `/docs`
3. `site.json` 의 `apply_url` 에 신청 폼(구글 폼 등) 주소를 넣고 다시 build

## 개인정보

결과 페이지는 공개 URL 이다. 그래서

- 이름 대신 닉네임을 쓰고, 주소는 추측하기 어려운 랜덤 slug 를 쓴다.
- 결과 페이지에는 `noindex` 를 넣어 검색엔진 노출을 막고, 첫 화면에도 목록을 띄우지 않는다.
- 하지만 레포가 public 이면 `readings/*.json`(생년월일 포함)도 누구나 볼 수 있다.
  신경 쓰이면 `readings/` 를 `.gitignore` 에 넣고 `docs/` 만 올린다.

## 테스트

```bash
py -3.12 -m pytest tests
```
