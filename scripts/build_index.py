"""캐시 → 파싱 → BM25/Qdrant/Neo4j 인덱스 구축. 사전 조건: make up"""
import logging
import pickle
from pathlib import Path

from neo4j import GraphDatabase

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.indexing.embedding_cache import load_embedding_cache
from korean_maritime_law_rag.indexing.embedder_factory import make_embedder
from korean_maritime_law_rag.indexing.graph import GraphStore
from korean_maritime_law_rag.indexing.lexical import Bm25Index
from korean_maritime_law_rag.indexing.vector import VectorIndex, make_qdrant_client

logging.basicConfig(level=logging.INFO, format="%(message)s")


class _PrecomputedEmbedder:
    def __init__(self, dim: int):
        self.dim = dim

    def encode(self, _texts: list[str]) -> list[list[float]]:
        raise RuntimeError("precomputed document vectors were expected")


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    articles = load_corpus(s.cache_dir)
    print(f"코퍼스: {len(articles)} 조문")

    bm25 = Bm25Index()
    bm25.build(articles)
    s.bm25_path.write_bytes(pickle.dumps(bm25))

    vectors = None
    if s.embedding_cache and s.embedding_cache.exists():
        cache = load_embedding_cache(s.embedding_cache)
        vectors = cache.vectors_for_articles(articles)
        embedder = _PrecomputedEmbedder(dim=len(vectors[0]) if vectors else 0)
        print(f"임베딩 캐시 사용: {s.embedding_cache}")
    else:
        embedder = make_embedder(s.embedding_model, device=s.embedding_device)
    vec = VectorIndex(embedder, make_qdrant_client(s.qdrant_url))
    vec.build(articles, vectors=vectors)

    driver = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))
    stats = GraphStore(driver).build(articles)
    driver.close()
    print(f"그래프: {stats}")


if __name__ == "__main__":
    main()
