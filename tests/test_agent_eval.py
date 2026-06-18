from korean_maritime_law_rag.evaluation.harness import agent_metrics


def _records():
    # gold_type/pred_type, gold_docs, cited_docs, refused
    return [
        {"id": "q1", "gold_type": "multihop", "pred_type": "multihop",
         "gold_docs": ["100::제83조"], "cited_docs": ["100::제83조"], "refused": False},
        {"id": "q2", "gold_type": "single", "pred_type": "multihop",
         "gold_docs": ["100::제5조"], "cited_docs": [], "refused": False},
        {"id": "q3", "gold_type": "unanswerable", "pred_type": "unanswerable",
         "gold_docs": [], "cited_docs": [], "refused": True},
    ]


def test_agent_metrics():
    m = agent_metrics(_records())
    # 분류 정확도: q1·q3 맞고 q2 틀림 = 2/3
    assert abs(m["classification_accuracy"] - 2 / 3) < 1e-9
    # 인용 정확도(answerable q1·q2): q1 적중, q2 실패 = 1/2
    assert abs(m["citation_hit_rate"] - 0.5) < 1e-9
    # 거절 정확도(unanswerable q3): 1/1
    assert m["refusal_accuracy"] == 1.0
    assert m["n_answerable"] == 2
    assert m["n_unanswerable"] == 1
