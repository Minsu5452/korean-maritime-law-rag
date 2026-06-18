from korean_maritime_law_rag.indexing.embedder import FakeEmbedder


def test_fake_embedder_deterministic_and_normalized():
    e = FakeEmbedder()
    v1, v2 = e.encode(["선박 검사", "선박 검사"])
    assert v1 == v2
    assert abs(sum(x * x for x in v1) - 1.0) < 1e-6


def test_fake_embedder_similarity_orders_correctly():
    e = FakeEmbedder()
    base, similar, different = e.encode(["선박 검사 기준", "선박 검사", "항만 화물 하역"])

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    assert dot(base, similar) > dot(base, different)


def test_fake_embedder_encode_queries_matches_encode():
    e = FakeEmbedder()
    assert e.encode_queries(["선박 검사"]) == e.encode(["선박 검사"])
