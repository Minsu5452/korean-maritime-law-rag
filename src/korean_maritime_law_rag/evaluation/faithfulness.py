"""답변 faithfulness(groundedness) 평가.

generator는 인용 doc_id를 검색 결과 enum으로 구조적으로 제약하지만, 그것만으로는
답변 '본문'이 해당 조문 내용을 정확히 말하는지는 보장하지 못한다. 여기서는 평가 모델이
답변의 사실 주장이 인용 조문 텍스트로 뒷받침되는지를 판정해 그 공백을 측정한다.
평가 모델은 BaseChatModel.with_structured_output을 쓰므로 CI에서 FakeChatModel로 결정적 테스트가 된다.
"""
from typing import cast

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

_JUDGE_SYSTEM = """당신은 한국 해양·수산 법령 RAG 답변의 faithfulness(groundedness) 평가자다.
주어진 답변의 모든 사실 주장이 '근거 조문' 텍스트 안에서 직접 확인되는지 판단한다.
- 근거 조문에 없는 사실·수치·요건·조문번호를 답변이 주장하면 grounded=false로 보고,
  뒷받침되지 않는 주장을 unsupported_claims에 짧게 적는다.
- 외부 법률 지식이나 일반 상식으로 보충된 주장도 근거 조문에 없으면 unsupported로 본다.
- 답변이 "근거를 찾지 못했습니다"류의 거절이면 환각이 없으므로 grounded=true로 본다.
근거 조문에 적힌 범위에서만 엄격하게 판정한다."""


class FaithfulnessVerdict(BaseModel):
    grounded: bool
    unsupported_claims: list[str] = Field(default_factory=list)
    reason: str = ""


def judge_faithfulness(answer: str, cited_context: str, model: BaseChatModel) -> FaithfulnessVerdict:
    """답변이 인용 조문 텍스트로 뒷받침되는지 평가 모델로 판정."""
    structured = model.with_structured_output(FaithfulnessVerdict)
    human = f"근거 조문:\n{cited_context}\n\n답변:\n{answer}"
    return cast(FaithfulnessVerdict, structured.invoke([("system", _JUDGE_SYSTEM), ("human", human)]))


def faithfulness_metrics(verdicts: list[FaithfulnessVerdict]) -> dict:
    """faithfulness_rate: grounded=true 비율. ungrounded: 근거 없는 주장이 잡힌 답변 수."""
    n = len(verdicts)
    grounded = sum(1 for v in verdicts if v.grounded)
    return {
        "faithfulness_rate": grounded / n if n else 0.0,
        "n": n,
        "grounded": grounded,
        "ungrounded": n - grounded,
    }
