import numpy as np

from korean_maritime_law_rag.indexing.embedder import OpenAIEmbedder, SentenceTransformerEmbedder
from korean_maritime_law_rag.indexing.embedder_factory import make_embedder, resolve_spec


class _FakeST:
    """SentenceTransformer 대역 — 다운로드 없이 프리픽스 적용을 검증한다."""

    def __init__(self) -> None:
        self.seen: list[list[str]] = []

    def get_sentence_embedding_dimension(self) -> int:
        return 4

    def encode(self, texts, normalize_embeddings=True, batch_size=32):
        self.seen.append(list(texts))
        return np.array([[float(len(t))] * 4 for t in texts])


def test_resolve_spec_e5_uses_query_passage_prefixes():
    spec = resolve_spec("intfloat/multilingual-e5-large")
    assert spec.kind == "st"
    assert spec.query_prefix == "query: "
    assert spec.passage_prefix == "passage: "


def test_resolve_spec_kure_and_bge_no_prefix():
    for name in ("nlpai-lab/KURE-v1", "BAAI/bge-m3"):
        spec = resolve_spec(name)
        assert spec.kind == "st"
        assert spec.query_prefix == "" and spec.passage_prefix == ""


def test_resolve_spec_openai_handles_prefix_form():
    assert resolve_spec("text-embedding-3-large").kind == "openai"
    assert resolve_spec("openai:text-embedding-3-large").kind == "openai"


def test_st_embedder_applies_passage_and_query_prefixes():
    fake = _FakeST()
    emb = SentenceTransformerEmbedder("intfloat/multilingual-e5-large",
                                      query_prefix="query: ", passage_prefix="passage: ",
                                      model=fake)
    emb.encode(["조문 본문"])
    emb.encode_queries(["질문"])
    assert fake.seen[0] == ["passage: 조문 본문"]
    assert fake.seen[1] == ["query: 질문"]
    assert emb.dim == 4


class _FakeOpenAI:
    class _Emb:
        def __init__(self, vec):
            self.embedding = vec

    class _Resp:
        def __init__(self, data):
            self.data = data

    def __init__(self):
        self.batches: list[list[str]] = []
        self.embeddings = self  # client.embeddings.create(...)

    def create(self, model, input):
        self.batches.append(list(input))
        return _FakeOpenAI._Resp([_FakeOpenAI._Emb([0.1] * 8) for _ in input])


def test_openai_embedder_batches_and_returns_vectors():
    client = _FakeOpenAI()
    emb = OpenAIEmbedder(model="text-embedding-3-large", client=client, batch_size=2, dim=8)
    vecs = emb.encode(["a", "b", "c"])
    assert len(vecs) == 3
    assert all(len(v) == 8 for v in vecs)
    assert client.batches == [["a", "b"], ["c"]]  # 배치 분할


def test_make_embedder_routes_to_openai_without_network():
    client = _FakeOpenAI()
    emb = make_embedder("text-embedding-3-large", client=client)
    assert isinstance(emb, OpenAIEmbedder)
