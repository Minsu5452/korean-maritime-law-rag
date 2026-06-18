import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from korean_maritime_law_rag.indexing.embedder import Embedder
from korean_maritime_law_rag.models import Article


def make_qdrant_client(url: str | None = None) -> QdrantClient:
    """Create a Qdrant client from config.

    qdrant-client treats ``url=None`` as a remote client with library defaults, not
    as local memory. The project config uses None to mean "no external service".
    """
    return QdrantClient(url=url) if url else QdrantClient(":memory:")


def _point_id(doc_id: str) -> str:
    """doc_id에서 결정적 포인트 ID(UUID5) 생성 — 증분 upsert가 멱등이 되도록."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, doc_id))


class VectorIndex:
    def __init__(self, embedder: Embedder, client: QdrantClient | None = None,
                 collection: str = "articles", upsert_batch_size: int = 256):
        self.embedder = embedder
        self.client = client or QdrantClient(":memory:")
        self.collection = collection
        self.upsert_batch_size = upsert_batch_size

    def _create_collection(self) -> None:
        self.client.create_collection(
            self.collection,
            vectors_config=VectorParams(size=self.embedder.dim, distance=Distance.COSINE),
        )

    def _resolve_vectors(
        self, articles: list[Article], vectors: list[list[float]] | None
    ) -> list[list[float]]:
        if vectors is None:
            vectors = self.embedder.encode([f"{a.article_no} {a.title}\n{a.text}" for a in articles])
        if len(vectors) != len(articles):
            raise ValueError(f"expected {len(articles)} vectors, got {len(vectors)}")
        return vectors

    def _upsert_points(self, articles: list[Article], vectors: list[list[float]]) -> None:
        points = [
            PointStruct(id=_point_id(a.doc_id), vector=vec,
                        payload={"doc_id": a.doc_id, "law_id": a.law_id})
            for a, vec in zip(articles, vectors)
        ]
        for start in range(0, len(points), self.upsert_batch_size):
            self.client.upsert(self.collection, points=points[start:start + self.upsert_batch_size])

    def build(self, articles: list[Article], vectors: list[list[float]] | None = None) -> None:
        """전체 재구축 — 컬렉션을 삭제하고 새로 만든다(초기 인덱싱용)."""
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        self._create_collection()
        self._upsert_points(articles, self._resolve_vectors(articles, vectors))

    def upsert(self, articles: list[Article], vectors: list[list[float]] | None = None) -> None:
        """증분 업서트(멱등) — 컬렉션이 없으면 만들고, 있으면 doc_id 기준으로 갱신한다."""
        if not self.client.collection_exists(self.collection):
            self._create_collection()
        self._upsert_points(articles, self._resolve_vectors(articles, vectors))

    def delete_by_law(self, law_id: str) -> None:
        """한 법령의 모든 포인트를 제거한다(개정 재동기화용)."""
        self.client.delete(
            self.collection,
            points_selector=Filter(must=[FieldCondition(key="law_id",
                                                        match=MatchValue(value=law_id))]),
        )

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        qvec = self.embedder.encode_queries([query])[0]
        hits = self.client.query_points(self.collection, query=qvec, limit=top_k).points
        return [(h.payload["doc_id"], float(h.score)) for h in hits if h.payload]
