import pytest

from korean_maritime_law_rag.indexing.embedder import FakeEmbedder
from korean_maritime_law_rag.indexing.lexical import Bm25Index
from korean_maritime_law_rag.indexing.vector import VectorIndex
from korean_maritime_law_rag.retrieval.retriever import Retriever


class InMemoryGraph:
    """GraphStore와 같은 시그니처의 테스트 더블 (small_corpus의 엣지 반영)."""

    EDGES = {  # doc_id → 인접 doc_id (양방향으로 조회)
        "100::제5조": ["100::제8조", "100::제98조", "200::제2조"],
        "100::제8조": ["100::제5조"],
        "100::제98조": ["100::제5조"],
        "200::제2조": ["100::제5조"],
    }

    def expand(self, seed_doc_ids, hops=2):
        out = []
        for sid in seed_doc_ids:
            frontier, seen = {sid}, {sid}
            for h in range(1, hops + 1):
                frontier = {n for f in frontier for n in self.EDGES.get(f, [])} - seen
                out += [(sid, n, h) for n in frontier]
                seen |= frontier
        return out

    def find_article(self, law_name, article_no):
        table = {("테스트선박법", "제5조"): "100::제5조", ("테스트선박법", "제98조"): "100::제98조"}
        return table.get((law_name, article_no))


@pytest.fixture()
def retriever(small_corpus):
    bm25 = Bm25Index()
    bm25.build(small_corpus)
    vec = VectorIndex(embedder=FakeEmbedder())
    vec.build(small_corpus)
    # 기본 설정은 1홉이지만, 이 픽스처는 다홉 확장 정렬을 확인하려고 2홉을 명시한다.
    return Retriever(bm25=bm25, vector=vec, graph=InMemoryGraph(), articles=small_corpus,
                     graph_hops=2)


def test_vector_strategy_returns_results(retriever):
    results = retriever.search("선박소유자는 검사를 받아야 한다", strategy="vector", top_k=3)
    assert results[0].doc_id == "100::제5조"


def test_hybrid_beats_on_article_number(retriever):
    results = retriever.search("테스트선박법 제98조", strategy="hybrid", top_k=3)
    assert results[0].doc_id == "100::제98조"


def test_graph_strategy_surfaces_multihop_answer(retriever):
    # "제5조 위반 처벌" — 답은 제5조가 아니라 제5조를 인용하는 벌칙 제98조.
    # 벡터/BM25는 제5조를 먼저 찾고, 그래프 확장이 제98조를 끌어올려야 한다
    results = retriever.search("검사를 받지 않으면 어떤 처벌을 받나", strategy="graph", top_k=4)
    doc_ids = [r.doc_id for r in results]
    assert "100::제98조" in doc_ids


def test_graph_strategy_pins_exact_citation(retriever):
    results = retriever.search("「테스트선박법」 제5조 내용이 뭐야", strategy="graph", top_k=3)
    assert results[0].doc_id == "100::제5조"


def test_unknown_strategy_raises(retriever):
    with pytest.raises(ValueError):
        retriever.search("질문", strategy="nope")


def test_expansion_ranking_orders_by_hops_then_seed_strength(retriever):
    # 시드: 제8조(강 0.05)·제98조(약 0.01). 기대 순서:
    # 1) 제5조 — 1홉 (두 시드 모두의 이웃, 강한 시드 점수 채택)
    # 2) 제98조, 3) 제2조 — 2홉·강시드(제8조) 경유, 동률이라 doc_id 사전순
    # 4) 제8조 — 2홉·약시드(제98조) 경유로만 도달
    ranking = retriever._expansion_ranking(
        ["100::제8조", "100::제98조"], {"100::제8조": 0.05, "100::제98조": 0.01}
    )
    assert ranking == ["100::제5조", "100::제98조", "200::제2조", "100::제8조"]


def test_graph_improves_rank_of_graph_connected_doc(retriever):
    # 멀티홉 질의: 제98조는 본문이 질의와 직접 겹쳐 hybrid 1위 — 확장이 필요 없는 문서.
    # graph 전략의 효과는 허브 문서(모든 조문이 인용하는 제5조)에서 나타난다:
    # 최강 시드(제98조)의 1홉 이웃이라 확장 랭킹 1위 → RRF 가산 스택으로 hybrid 2위 → graph 1위.
    # 직접 정답(제98조)은 2위 유지 — 확장이 텍스트 정답을 묻어버리지 않는다.
    q = "검사를 받지 않으면 어떤 처벌을 받나"
    hybrid_ids = [r.doc_id for r in retriever.search(q, strategy="hybrid", top_k=4)]
    graph_ids = [r.doc_id for r in retriever.search(q, strategy="graph", top_k=4)]
    assert hybrid_ids[:2] == ["100::제98조", "100::제5조"]
    assert graph_ids[:2] == ["100::제5조", "100::제98조"]
    assert graph_ids.index("100::제5조") < hybrid_ids.index("100::제5조")  # 그래프 연결 문서 승격
