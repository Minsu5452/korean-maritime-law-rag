from typing import Any

from korean_maritime_law_rag.indexing.lexical import Bm25Index
from korean_maritime_law_rag.indexing.vector import VectorIndex
from korean_maritime_law_rag.models import Article, SearchResult
from korean_maritime_law_rag.retrieval.citation import parse_citation
from korean_maritime_law_rag.retrieval.fusion import rrf
from korean_maritime_law_rag.retrieval.reranker import NoopReranker, Reranker

STRATEGIES = ("vector", "hybrid", "graph")


class Retriever:
    def __init__(self, bm25: Bm25Index, vector: VectorIndex, graph: Any = None,
                 articles: list[Article] | None = None, reranker: Reranker | None = None,
                 rrf_k: int = 60, graph_hops: int = 1, seed_size: int = 5):
        self.bm25 = bm25
        self.vector = vector
        self.graph = graph
        self.meta = {a.doc_id: a for a in (articles or [])}
        self.reranker = reranker or NoopReranker()
        self.rrf_k = rrf_k
        self.graph_hops = graph_hops
        self.seed_size = seed_size

    def search(self, query: str, strategy: str = "graph", top_k: int = 10) -> list[SearchResult]:
        if strategy not in STRATEGIES:
            raise ValueError(f"strategy must be one of {STRATEGIES}")
        pool = top_k * 3
        if strategy == "vector":
            scores = {d: s for d, s in self.vector.search(query, pool) if s > 0.0}
        elif strategy == "hybrid":
            scores = self._hybrid(query, pool)
        else:
            scores = self._graph(query, pool)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        ranked = self.reranker.rerank(query, ranked, self.meta, top_k)
        return [self._result(d, s) for d, s in ranked[:top_k]]

    def _hybrid(self, query: str, pool: int) -> dict[str, float]:
        vec_ids = [d for d, s in self.vector.search(query, pool) if s > 0.0]
        bm_ids = [d for d, _ in self.bm25.search(query, pool)]
        return rrf([vec_ids, bm_ids], k=self.rrf_k)

    def _graph(self, query: str, pool: int) -> dict[str, float]:
        vec_ids = [d for d, s in self.vector.search(query, pool) if s > 0.0]
        bm_ids = [d for d, _ in self.bm25.search(query, pool)]
        hybrid_scores = rrf([vec_ids, bm_ids], k=self.rrf_k)
        seeds = sorted(hybrid_scores, key=lambda d: hybrid_scores[d], reverse=True)[: self.seed_size]

        exact = None
        if (cite := parse_citation(query)) and self.graph is not None:
            exact = self.graph.find_article(*cite)
            if exact and exact not in seeds:
                seeds = [exact] + seeds[:-1]

        rankings = [vec_ids, bm_ids]
        if self.graph is not None and seeds:
            expansion = self._expansion_ranking(seeds, hybrid_scores)
            if expansion:
                rankings.append(expansion)
        scores = rrf(rankings, k=self.rrf_k)

        if exact:
            scores[exact] = max(scores.values(), default=0.0) + 1.0  # 최상위 고정
        return scores

    def _expansion_ranking(self, seeds: list[str], seed_scores: dict[str, float]) -> list[str]:
        """그래프 확장 후보를 세 번째 RRF 랭킹으로 정렬한다.

        핵심: 확장 후보가 vec/bm25 랭킹에도 있으면 RRF가 점수를 가산 스택하므로,
        '텍스트 신호 약함 + 그래프 연결'인 멀티홉 정답이 경계를 넘을 수 있다
        (곱셈형 decay는 구조적으로 불가능했음 — architecture.md 설계 이터레이션 참조).
        """
        best: dict[str, tuple[int, float]] = {}  # doc_id -> (hops, seed_score)
        for seed, doc_id, hops in self.graph.expand(seeds, hops=self.graph_hops):
            cand = (hops, seed_scores.get(seed, 0.0))
            cur = best.get(doc_id)
            if cur is None or cand[0] < cur[0] or (cand[0] == cur[0] and cand[1] > cur[1]):
                best[doc_id] = cand
        return sorted(best, key=lambda d: (best[d][0], -best[d][1], d))

    def _result(self, doc_id: str, score: float) -> SearchResult:
        a = self.meta.get(doc_id)
        return SearchResult(
            doc_id=doc_id, score=score,
            law_name=a.law_name if a else "", article_no=a.article_no if a else "",
            snippet=(a.text[:120] if a else ""),
        )
