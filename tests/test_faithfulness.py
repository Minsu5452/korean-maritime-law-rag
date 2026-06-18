from korean_maritime_law_rag.evaluation.faithfulness import (
    FaithfulnessVerdict,
    faithfulness_metrics,
    judge_faithfulness,
)
from korean_maritime_law_rag.llm import FakeChatModel


def test_judge_returns_grounded_verdict():
    model = FakeChatModel(structured_outputs=[
        FaithfulnessVerdict(grounded=True, reason="조문에 명시됨")])
    v = judge_faithfulness("3년 이하의 징역.", "[100::제83조] ... 3년 이하의 징역", model)
    assert v.grounded is True


def test_judge_flags_unsupported_claim():
    model = FakeChatModel(structured_outputs=[
        FaithfulnessVerdict(grounded=False, unsupported_claims=["5천만원 벌금"])])
    v = judge_faithfulness("5천만원 벌금.", "[100::제83조] ... 3년 이하의 징역", model)
    assert v.grounded is False
    assert v.unsupported_claims == ["5천만원 벌금"]


def test_metrics_aggregate():
    verdicts = [
        FaithfulnessVerdict(grounded=True),
        FaithfulnessVerdict(grounded=True),
        FaithfulnessVerdict(grounded=False, unsupported_claims=["x"]),
    ]
    m = faithfulness_metrics(verdicts)
    assert (m["n"], m["grounded"], m["ungrounded"]) == (3, 2, 1)
    assert abs(m["faithfulness_rate"] - 2 / 3) < 1e-9


def test_metrics_empty_is_zero():
    assert faithfulness_metrics([])["faithfulness_rate"] == 0.0
