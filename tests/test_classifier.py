from korean_maritime_law_rag.agent.classifier import classify
from korean_maritime_law_rag.agent.state import QueryTypeResult
from korean_maritime_law_rag.llm import FakeChatModel


def test_classify_returns_query_type():
    model = FakeChatModel(structured_outputs=[QueryTypeResult(query_type="multihop")])
    assert classify("선박검사를 안 받으면 처벌은?", model) == "multihop"


def test_classify_unanswerable():
    model = FakeChatModel(structured_outputs=[QueryTypeResult(query_type="unanswerable")])
    assert classify("소득세는 어떻게 계산하나요?", model) == "unanswerable"
