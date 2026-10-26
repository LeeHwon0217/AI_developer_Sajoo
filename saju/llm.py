"""선택 사항: 규칙 기반 초안을 LLM 으로 다시 쓰기.

PROVIDERS 에 함수를 하나 추가하면 다른 LLM(예: Upstage Solar)도 붙일 수 있다.
각 함수는 (chart_dict, draft_dict, request_note) → 새 draft_dict 를 돌려주면 된다.
"""
from __future__ import annotations

import json

SYSTEM = """당신은 사주명리에 밝은 시니어 AI 개발자입니다.
주어진 사주 원국(계산 완료된 데이터)과 규칙 기반 초안을 바탕으로, 개발자 언어로 풀이를 다시 씁니다.

- 원국 데이터(간지, 오행 개수, 십성, 대운)는 바꾸지 말고 해석만 하세요.
- 섹션 key·hanja·nav 와 순서는 그대로 두고 내용만 풍성하게 씁니다. 명식 설명은 짧게, 성격·직업·돈·연애·결혼·자녀는 자세하게.
- 모든 섹션의 evidence 에는 그 해석이 나온 글자·십성·연도를 적습니다. 근거 없는 주장은 쓰지 마세요.
- 재미있되 단정적인 예언이나 건강·투자 조언은 하지 마세요.
- 초안과 같은 JSON 구조로, 한국어 존댓말로 답하세요."""


def _schema() -> dict:
    s, arr = {"type": "string"}, lambda item: {"type": "array", "items": item}

    def obj(**props):
        return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}

    section = obj(
        key=s, hanja=s, nav=s, title=s, sub=s, lead=s,
        paras=arr(s),
        cards=arr(obj(title=s, body=s, badge=s)),
        stats=arr(obj(label=s, value=s, sub=s)),
        bars=arr(obj(label=s, value={"type": "integer"}, note=s)),
        timeline=arr(obj(when=s, title=s, body=s, now={"type": "boolean"})),
        chips=arr(s),
        evidence=arr(s),
    )
    return obj(headline=s, sections=arr(section), closing=s)


def _anthropic(chart: dict, draft: dict, note: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    user = (
        f"## 원국\n```json\n{json.dumps(chart, ensure_ascii=False, indent=1)}\n```\n\n"
        f"## 규칙 기반 초안\n```json\n{json.dumps(draft, ensure_ascii=False, indent=1)}\n```\n\n"
        f"## 신청자 메모\n{note or '(없음)'}"
    )
    resp = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": _schema()}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("LLM 이 요청을 거절했습니다. 규칙 기반 초안을 그대로 쓰세요.")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


PROVIDERS = {"anthropic": _anthropic}


def rewrite(provider: str, chart: dict, draft: dict, note: str = "") -> dict:
    if provider not in PROVIDERS:
        raise SystemExit(f"알 수 없는 LLM: {provider} (가능: {', '.join(PROVIDERS)})")
    return PROVIDERS[provider](chart, draft, note)
