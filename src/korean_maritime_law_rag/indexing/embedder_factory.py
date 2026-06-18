"""임베더 비교 실험용 팩토리: 모델명으로 적절한 임베더를 만든다."""
from dataclasses import dataclass

from korean_maritime_law_rag.indexing.embedder import (
    Embedder,
    OpenAIEmbedder,
    SentenceTransformerEmbedder,
)


@dataclass(frozen=True)
class EmbedderSpec:
    kind: str  # "st" | "openai"
    query_prefix: str = ""
    passage_prefix: str = ""


_SPECS: dict[str, EmbedderSpec] = {
    "nlpai-lab/KURE-v1": EmbedderSpec("st"),
    "BAAI/bge-m3": EmbedderSpec("st"),
    "intfloat/multilingual-e5-large": EmbedderSpec("st", "query: ", "passage: "),
    "text-embedding-3-large": EmbedderSpec("openai"),
}


def resolve_spec(model_name: str) -> EmbedderSpec:
    """모델명(또는 'openai:...' 형태)에서 임베더 사양을 결정한다."""
    name = model_name.split(":", 1)[-1]
    if name in _SPECS:
        return _SPECS[name]
    if "e5" in name.lower():  # e5 계열은 query/passage 프리픽스 필요
        return EmbedderSpec("st", "query: ", "passage: ")
    if name.startswith("text-embedding-"):
        return EmbedderSpec("openai")
    return EmbedderSpec("st")  # 알 수 없는 ST 모델 — 프리픽스 없음


def make_embedder(model_name: str, device: str = "cpu", batch_size: int = 32,
                  client: object | None = None) -> Embedder:
    spec = resolve_spec(model_name)
    if spec.kind == "openai":
        return OpenAIEmbedder(model=model_name.split(":", 1)[-1], client=client)
    return SentenceTransformerEmbedder(
        model_name, device=device, batch_size=batch_size,
        query_prefix=spec.query_prefix, passage_prefix=spec.passage_prefix,
    )
