from korean_maritime_law_rag.indexing.lexical import Bm25Index


def test_exact_article_number_match(small_corpus):
    idx = Bm25Index()
    idx.build(small_corpus)
    results = idx.search("테스트선박법 제98조", top_k=2)
    assert results[0][0] == "100::제98조"


def test_keyword_match(small_corpus):
    idx = Bm25Index()
    idx.build(small_corpus)
    top = [doc_id for doc_id, _ in idx.search("항만 시설", top_k=2)]
    assert "200::제2조" in top


def test_scores_descending(small_corpus):
    idx = Bm25Index()
    idx.build(small_corpus)
    scores = [s for _, s in idx.search("검사", top_k=4)]
    assert scores == sorted(scores, reverse=True)


def test_index_pickle_roundtrip(small_corpus):
    import pickle

    idx = Bm25Index()
    idx.build(small_corpus)
    restored = pickle.loads(pickle.dumps(idx))
    assert restored.search("검사", top_k=2) == idx.search("검사", top_k=2)
