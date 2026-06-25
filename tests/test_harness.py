from korean_maritime_law_rag.evaluation.harness import GoldItem, run_eval, to_markdown
from korean_maritime_law_rag.models import SearchResult


class StubRetriever:
    """q1은 정답을 1위로, q2는 정답을 못 찾는 가짜 검색기."""

    def search(self, query, strategy="graph", top_k=10):
        if "벌칙" in query:
            return [SearchResult(doc_id="100::제98조", score=0.9)]
        return [SearchResult(doc_id="100::제1조", score=0.5)]


GOLD = [
    GoldItem(id="q1", question="벌칙은?", type="multihop", gold=["100::제98조"]),
    GoldItem(id="q2", question="목적은?", type="single", gold=["100::제5조"]),
    GoldItem(id="q3", question="세금은?", type="unanswerable", gold=[]),
]


def test_run_eval_computes_metrics_per_strategy_and_type():
    report = run_eval(StubRetriever(), GOLD, strategies=["graph"], top_k=10)
    overall = report["graph"]["overall"]
    assert abs(overall["hit_rate@1"] - 0.5) < 1e-9   # q1 적중, q2 실패 (q3 제외)
    assert report["graph"]["by_type"]["multihop"]["hit_rate@1"] == 1.0
    assert report["graph"]["by_type"]["single"]["hit_rate@1"] == 0.0
    assert report["graph"]["n_questions"] == 2       # unanswerable 제외


def test_to_markdown_renders_table():
    report = run_eval(StubRetriever(), GOLD, strategies=["graph"], top_k=10)
    md = to_markdown(report)
    assert "| graph |" in md and "hit@1" in md


def test_gold_item_gold_uses_default_factory():
    assert GoldItem.model_fields["gold"].default_factory is list
