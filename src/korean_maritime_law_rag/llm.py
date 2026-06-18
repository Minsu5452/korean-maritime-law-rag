from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from korean_maritime_law_rag.config import Settings


def get_chat_model(settings: Settings) -> BaseChatModel:
    """config 문자열 → 에이전트 ChatModel. init_chat_model만 사용(provider SDK 직접 래핑 금지)."""
    kwargs: dict[str, Any] = {"temperature": settings.llm_temperature}
    if settings.llm_reasoning_effort:  # reasoning_effort를 지원하는 모델에서만 사용
        kwargs["reasoning_effort"] = settings.llm_reasoning_effort
    return init_chat_model(settings.llm_model, **kwargs)


def get_judge_model(settings: Settings) -> BaseChatModel:
    """근거성 평가용 ChatModel(시스템 모델과 분리해 자기평가 편향 방지)."""
    return init_chat_model(settings.judge_model, temperature=settings.llm_temperature)


class _FakeStructured:
    def __init__(self, outputs: list[BaseModel]) -> None:
        self._outputs = outputs

    def invoke(self, _prompt: Any) -> BaseModel:
        assert self._outputs, "FakeChatModel: 준비된 structured 출력이 없음"
        return self._outputs.pop(0)


class FakeChatModel:
    """테스트용 결정적 가짜 LLM. with_structured_output(schema).invoke() 만 지원.

    실제 LLM 호출 없이 분류·생성을 결정적으로 테스트한다(FakeEmbedder와 같은 역할).
    structured_outputs는 호출 순서대로 소비된다(예: [분류결과, 생성결과]).
    """

    def __init__(self, structured_outputs: list[BaseModel] | None = None) -> None:
        self._structured_outputs = list(structured_outputs or [])

    def with_structured_output(self, _schema: type[BaseModel]) -> _FakeStructured:
        return _FakeStructured(self._structured_outputs)
