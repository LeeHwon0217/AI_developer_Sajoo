"""선택 사항: 규칙 기반 초안을 LLM 으로 다시 쓰기.

PROVIDERS 에 함수를 하나 추가하면 다른 LLM(예: Upstage Solar)도 붙일 수 있다.
각 함수는 (chart_dict, draft_dict, request_note) → 새 draft_dict 를 돌려주면 된다.
"""
from __future__ import annotations

import json

SYSTEM = """당신은 사주명리에 밝은 시니어 AI 개발자입니다.
주어진 사주 원국(계산 완료된 데이터)과 규칙 기반 초안을 바탕으로, 개발자 언어로 풀이를 다시 씁니다.

- 원국 데이터(간지, 오행 개수, 십성, 대운)는 바꾸지 말고 해석만 하세요.
- 오행은 기술 역량, 십성은 일하는 방식, 대운은 릴리즈 로드맵, 세운은 연간 릴리즈 노트로 비유합니다.
- 재미있되 단정적인 예언이나 건강·투자 조언은 하지 마세요.
- 초안과 같은 JSON 구조로, 한국어 존댓말로 답하세요."""


def _schema() -> dict:
    s = {"type": "string"}
    item = lambda *keys: {  # noqa: E731
        "type": "object", "additionalProperties": False, "required": list(keys),
        "properties": {k: ({"type": "integer"} if k == "year" else s) for k in keys},
    }
    return {
        "type": "object", "additionalProperties": False,
        "required": ["headline", "summary", "work_style", "strengths", "warnings",
                     "patches", "roadmap", "releases", "closing"],
        "properties": {
            "headline": s, "summary": s, "closing": s,
            "work_style": item("title", "body"),
            "strengths": {"type": "array", "items": s},
            "warnings": {"type": "array", "items": s},
            "patches": {"type": "array", "items": s},
            "roadmap": {"type": "array", "items": item("version", "pillar", "note")},
            "releases": {"type": "array", "items": item("year", "pillar", "note")},
        },
    }


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
