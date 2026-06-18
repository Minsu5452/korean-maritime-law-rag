from pathlib import Path

import pytest

from korean_maritime_law_rag.indexing.embedding_cache import EmbeddingCache, load_embedding_cache
from korean_maritime_law_rag.indexing.vector import VectorIndex
from korean_maritime_law_rag.models import Article


class CountingEmbedder:
    dim = 2

    def __init__(self) -> None:
        self.calls = 0

    def encode(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return [[1.0, 0.0] for _ in texts]

    def encode_queries(self, texts: list[str]) -> list[list[float]]:
        return self.encode(texts)


def _articles() -> list[Article]:
    return [
        Article(law_id="100", law_name="테스트법", article_no="제1조", title="목적", text="목적"),
        Article(law_id="100", law_name="테스트법", article_no="제2조", title="정의", text="정의"),
    ]


def test_embedding_cache_round_trip(tmp_path: Path):
    path = tmp_path / "embeddings.npz"
    cache = EmbeddingCache(
        doc_ids=["100::제1조", "100::제2조"],
        vectors=[[1.0, 0.0], [0.0, 1.0]],
    )
    cache.save(path)

    loaded = load_embedding_cache(path)

    assert loaded.doc_ids == ["100::제1조", "100::제2조"]
    assert loaded.vectors_for_articles(_articles()) == [[1.0, 0.0], [0.0, 1.0]]


def test_embedding_cache_rejects_missing_doc_id():
    cache = EmbeddingCache(doc_ids=["100::제1조"], vectors=[[1.0, 0.0]])

    with pytest.raises(ValueError, match="임베딩 캐시에 없는 문서"):
        cache.vectors_for_articles(_articles())


def test_vector_build_uses_precomputed_document_vectors():
    embedder = CountingEmbedder()
    idx = VectorIndex(embedder=embedder)

    idx.build(_articles(), vectors=[[1.0, 0.0], [0.0, 1.0]])

    assert embedder.calls == 0
    assert idx.search("정의", top_k=1)[0][0] in {"100::제1조", "100::제2조"}
    assert embedder.calls == 1
