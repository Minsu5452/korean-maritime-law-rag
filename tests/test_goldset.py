from collections import Counter
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.evaluation.harness import GoldItem, load_gold, validate_gold
from korean_maritime_law_rag.indexing.graph import resolve_citation_edges

GOLD = Path("tests/qa_pairs.yaml")
CFG = Path("configs/demo.yaml")


def _items():
    return [
        GoldItem(id="q1", question="A?", type="single", gold=["100::제5조"]),
        GoldItem(id="q2", question="B?", type="multihop", gold=["100::제98조"]),
        GoldItem(id="q3", question="C?", type="unanswerable", gold=[]),
    ]


def test_valid_gold_passes():
    corpus = {"100::제5조", "100::제98조"}
    assert validate_gold(_items(), corpus, min_multihop_ratio=0.2) == []


def test_unknown_doc_id_fails():
    errors = validate_gold(_items(), corpus_ids={"100::제5조"}, min_multihop_ratio=0.0)
    assert any("q2" in e for e in errors)


def test_multihop_ratio_enforced():
    errors = validate_gold(_items(), {"100::제5조", "100::제98조"}, min_multihop_ratio=0.9)
    assert any("multihop" in e for e in errors)


def test_unanswerable_must_have_empty_gold():
    bad = [GoldItem(id="q4", question="D?", type="unanswerable", gold=["100::제5조"])]
    errors = validate_gold(bad, {"100::제5조"}, min_multihop_ratio=0.0)
    assert any("q4" in e for e in errors)


def test_duplicate_doc_id_in_gold_fails():
    bad = [GoldItem(id="q5", question="E?", type="single", gold=["100::제5조", "100::제5조"])]
    errors = validate_gold(bad, {"100::제5조"}, min_multihop_ratio=0.0)
    assert any("q5" in e for e in errors)


def test_goldset_type_distribution():
    """동결된 분포 — 회귀 방지."""
    counts = Counter(g.type for g in load_gold(GOLD))
    assert counts["single"] == 29
    assert counts["definition"] == 8
    assert counts["multihop"] == 117
    assert counts["unanswerable"] == 26


def test_multihop_golds_are_connected_in_citation_graph():
    """멀티홉 gold는 인용·위임 그래프에서 무방향 차수>=1이어야 한다(고립된 정답 없음)."""
    articles = load_corpus(load_settings(CFG).cache_dir)
    edges, _ = resolve_citation_edges(articles)
    connected = {e["src"] for e in edges} | {e["dst"] for e in edges}
    offenders = [(g.id, d) for g in load_gold(GOLD) if g.type == "multihop"
                 for d in g.gold if d not in connected]
    assert not offenders, f"인용 그래프에 고립된 멀티홉 gold: {offenders}"
