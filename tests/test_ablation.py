from korean_maritime_law_rag.evaluation.ablation import format_embedder_ablation, pick_winner


def _result(hit1: float) -> dict:
    block = {"overall": {"hit_rate@1": hit1, "recall@10": 0.9, "mrr": 0.7},
             "by_type": {}, "n_questions": 10}
    return {"vector": block, "hybrid": block, "graph": block}


RESULTS = {
    "KURE-v1": _result(0.55),
    "BGE-M3": _result(0.62),
    "e5-large": _result(0.48),
}


def test_pick_winner_returns_best_model_for_metric():
    assert pick_winner(RESULTS, metric="hit_rate@1", strategy="graph") == "BGE-M3"


def test_format_embedder_ablation_lists_all_models():
    md = format_embedder_ablation(RESULTS, strategies=["vector", "graph"])
    assert "KURE-v1" in md and "BGE-M3" in md and "e5-large" in md
    assert "hit@1" in md
