from korean_maritime_law_rag.retrieval.fusion import rrf


def test_rrf_rewards_docs_in_both_rankings():
    scores = rrf([["a", "b", "c"], ["b", "a", "d"]], k=60)
    assert scores["a"] > scores["c"]
    assert scores["b"] > scores["d"]


def test_rrf_standard_formula():
    scores = rrf([["a"]], k=60)
    assert abs(scores["a"] - 1 / 61) < 1e-9


def test_rrf_empty():
    assert rrf([]) == {}
