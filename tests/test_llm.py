import pytest
from pydantic import BaseModel

from korean_maritime_law_rag.llm import FakeChatModel, get_chat_model


class _Out(BaseModel):
    value: str


def test_fake_chat_model_returns_scripted_structured_output():
    model = FakeChatModel(structured_outputs=[_Out(value="a"), _Out(value="b")])
    assert model.with_structured_output(_Out).invoke("ignored").value == "a"
    assert model.with_structured_output(_Out).invoke("ignored").value == "b"


def test_fake_chat_model_raises_when_exhausted():
    model = FakeChatModel(structured_outputs=[])
    with pytest.raises(AssertionError):
        model.with_structured_output(_Out).invoke("x")


def test_get_chat_model_builds_from_settings(monkeypatch):
    from korean_maritime_law_rag.config import load_settings

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-used")
    model = get_chat_model(load_settings(None))
    assert model is not None  # 생성만 확인(네트워크 호출 없음)
