import hashlib
import math
from typing import Any, Protocol


class Embedder(Protocol):
    dim: int

    def encode(self, texts: list[str]) -> list[list[float]]: ...

    def encode_queries(self, texts: list[str]) -> list[list[float]]: ...


def _stable_hash(tok: str) -> int:
    """PYTHONHASHSEED에 무관한 결정적 해시 (hashlib.md5 사용)."""
    return int(hashlib.md5(tok.encode()).hexdigest(), 16)


class FakeEmbedder:
    """테스트용 임베더 (프로세스 간 결정적 — hashlib 기반 bag-of-words). 모델 다운로드 없음."""

    dim = 64

    def encode(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            v = [0.0] * self.dim
            for tok in text.split():
                v[_stable_hash(tok) % self.dim] += 1.0
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out

    def encode_queries(self, texts: list[str]) -> list[list[float]]:
        return self.encode(texts)


class SentenceTransformerEmbedder:
    """sentence-transformers 계열 임베더(KURE-v1·BGE-M3·multilingual-e5 등).

    e5처럼 query/passage 프리픽스가 필요한 모델은 prefix 인자로 지정한다.
    model 인자로 모델 객체를 주입하면 다운로드 없이 단위테스트 가능(ml extra lazy import)."""

    def __init__(self, model_name: str = "nlpai-lab/KURE-v1", device: str = "cpu",
                 batch_size: int = 32, query_prefix: str = "", passage_prefix: str = "",
                 model: Any | None = None):
        if model is None:
            from sentence_transformers import SentenceTransformer

            if device == "auto":
                import torch

                device = "mps" if torch.backends.mps.is_available() else "cpu"
            model = SentenceTransformer(model_name, device=device)
        self._model: Any = model
        self.dim: int = self._model.get_sentence_embedding_dimension() or 1024
        self._batch_size = batch_size
        self._query_prefix = query_prefix
        self._passage_prefix = passage_prefix
        self._cache: dict[tuple[str, ...], list[list[float]]] = {}

    def _encode(self, texts: list[str]) -> list[list[float]]:
        # 임베딩 캐시: 평가는 같은 텍스트를 전략마다 재임베딩하므로 중복 제거(결정적이라 결과 불변).
        key = tuple(texts)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        out: list[list[float]] = self._model.encode(
            texts, normalize_embeddings=True, batch_size=self._batch_size
        ).tolist()
        if len(self._cache) < 8192:  # 서빙 시 무한증가 방지 상한
            self._cache[key] = out
        return out

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._encode([self._passage_prefix + t for t in texts])

    def encode_queries(self, texts: list[str]) -> list[list[float]]:
        return self._encode([self._query_prefix + t for t in texts])


class KureEmbedder(SentenceTransformerEmbedder):
    """KURE-v1 기본값 하위호환 래퍼."""

    def __init__(self, model_name: str = "nlpai-lab/KURE-v1",
                 device: str = "cpu", batch_size: int = 32):
        super().__init__(model_name, device=device, batch_size=batch_size)


class OpenAIEmbedder:
    """OpenAI 임베딩 API(text-embedding-3-large 등). client 주입 시 네트워크 없이 테스트 가능."""

    def __init__(self, model: str = "text-embedding-3-large", client: Any | None = None,
                 batch_size: int = 256, dim: int = 3072):
        self.model = model
        self._client: Any = client
        self._batch_size = batch_size
        self.dim = dim

    def _ensure(self) -> None:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()

    def encode(self, texts: list[str]) -> list[list[float]]:
        self._ensure()
        out: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            resp = self._client.embeddings.create(model=self.model, input=batch)
            out.extend(list(d.embedding) for d in resp.data)
        return out

    def encode_queries(self, texts: list[str]) -> list[list[float]]:
        return self.encode(texts)
