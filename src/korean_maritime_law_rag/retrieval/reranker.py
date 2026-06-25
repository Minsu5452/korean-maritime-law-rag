from typing import Any, Protocol

from korean_maritime_law_rag.models import Article


class Reranker(Protocol):
    def rerank(self, query: str, candidates: list[tuple[str, float]],
               meta: dict[str, Article], top_k: int) -> list[tuple[str, float]]: ...


class NoopReranker:
    def rerank(self, query, candidates, meta, top_k):
        return candidates[:top_k]


class CrossEncoderReranker:
    """bge-reranker. lazy import — extra 'ml' 필요. configs의 rerank=true일 때만 생성.

    device 기본 cpu — 대형 cross-encoder를 MPS에 올리면 임베딩과 공유 메모리가 충돌해
    OOM이 나기 쉽다(결정적·안전 우선). 필요시 'mps'/'cuda'로 지정.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", device: str = "cpu",
                 model: Any | None = None):
        if model is None:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(model_name, device=device)
        self._model: Any = model

    def rerank(self, query, candidates, meta, top_k):
        # 상위 후보만 재정렬(표준·메모리·속도). 그래프 확장이 meta(as-of 필터) 밖의
        # doc_id를 올릴 수 있으므로 meta에 있는 후보만 점수화한다(KeyError 방지).
        pool = [(d, s) for d, s in candidates[: max(30, top_k)] if d in meta]
        if not pool:
            return candidates[:top_k]
        scores = self._model.predict([(query, meta[d].text) for d, _ in pool])
        ranked = sorted(zip([d for d, _ in pool], scores), key=lambda x: x[1], reverse=True)
        return [(d, float(s)) for d, s in ranked[:top_k]]
