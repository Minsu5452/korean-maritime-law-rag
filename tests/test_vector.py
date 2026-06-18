from korean_maritime_law_rag.indexing.embedder import FakeEmbedder
from korean_maritime_law_rag.indexing.vector import VectorIndex, make_qdrant_client
from korean_maritime_law_rag.models import Article


def test_vector_search_returns_semantically_close(small_corpus):
    idx = VectorIndex(embedder=FakeEmbedder())  # client 미지정 → :memory:
    idx.build(small_corpus)
    results = idx.search("선박소유자는 검사를 받아야 한다", top_k=2)
    assert results[0][0] == "100::제5조"
    assert all(isinstance(s, float) for _, s in results)


def test_make_qdrant_client_none_uses_in_memory(small_corpus):
    idx = VectorIndex(embedder=FakeEmbedder(), client=make_qdrant_client(None))

    idx.build(small_corpus)
    results = idx.search("항만 시설", top_k=1)

    assert len(results) == 1
    assert results[0][0] in {article.doc_id for article in small_corpus}


class RecordingClient:
    def __init__(self) -> None:
        self.upsert_sizes: list[int] = []

    def collection_exists(self, _collection: str) -> bool:
        return False

    def create_collection(self, *_args, **_kwargs) -> None:
        pass

    def upsert(self, _collection: str, points) -> None:
        self.upsert_sizes.append(len(points))


def test_vector_build_upserts_points_in_batches():
    articles = [
        Article(law_id="100", law_name="테스트법", article_no=f"제{i}조", title="", text=str(i))
        for i in range(5)
    ]
    client = RecordingClient()
    idx = VectorIndex(embedder=FakeEmbedder(), client=client, upsert_batch_size=2)

    idx.build(articles)

    assert client.upsert_sizes == [2, 2, 1]


def test_vector_upsert_is_idempotent():
    idx = VectorIndex(embedder=FakeEmbedder())
    arts = [Article(law_id="1", law_name="선박안전법", article_no="제1조", text="선박 검사")]
    idx.build(arts)
    n1 = idx.client.count(idx.collection).count
    idx.upsert(arts)  # 동일 문서 재업서트 — 중복 생성 금지
    assert n1 == 1
    assert idx.client.count(idx.collection).count == 1


def test_vector_upsert_updates_existing_doc_in_place():
    idx = VectorIndex(embedder=FakeEmbedder())
    idx.build([Article(law_id="1", law_name="L", article_no="제1조", text="옛 내용")])
    idx.upsert([Article(law_id="1", law_name="L", article_no="제1조", text="새 내용 항만 시설")])
    assert idx.client.count(idx.collection).count == 1


def test_vector_delete_by_law_removes_only_that_law():
    idx = VectorIndex(embedder=FakeEmbedder())
    idx.build([
        Article(law_id="1", law_name="선박안전법", article_no="제1조", text="선박 검사"),
        Article(law_id="2", law_name="항만법", article_no="제1조", text="항만 시설"),
    ])
    idx.delete_by_law("1")
    remaining = {d for d, _ in idx.search("선박 항만 시설 검사", top_k=10)}
    assert "2::제1조" in remaining
    assert "1::제1조" not in remaining
