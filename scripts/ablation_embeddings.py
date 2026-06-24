"""임베더와 검색 전략 조합을 비교하고 reranker 효과를 측정한다.

사용: OPENAI_API_KEY=... python scripts/ablation_embeddings.py
출력: reports/embedder_ablation.md, reports/embedder_ablation.json
"""
import json
import logging
import re
from pathlib import Path

from neo4j import GraphDatabase

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import filter_as_of, load_corpus
from korean_maritime_law_rag.evaluation.ablation import format_embedder_ablation, pick_winner
from korean_maritime_law_rag.evaluation.harness import load_gold, run_eval, to_markdown
from korean_maritime_law_rag.indexing.embedder_factory import make_embedder
from korean_maritime_law_rag.indexing.graph import GraphStore
from korean_maritime_law_rag.indexing.lexical import Bm25Index
from korean_maritime_law_rag.indexing.vector import VectorIndex, make_qdrant_client
from korean_maritime_law_rag.retrieval.reranker import CrossEncoderReranker, NoopReranker
from korean_maritime_law_rag.retrieval.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ablation")

MODELS = [
    "nlpai-lab/KURE-v1",
    "BAAI/bge-m3",
    "intfloat/multilingual-e5-large",
    "text-embedding-3-large",
]
STRATEGIES = ["vector", "hybrid", "graph"]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _get_or_build_index(s, model: str, articles: list) -> VectorIndex:
    """모델별 Qdrant 컬렉션을 재사용(이미 임베딩됨)하거나 새로 빌드한다(재실행 비용 절감)."""
    coll = f"abl_{_slug(model)}"
    client = make_qdrant_client(s.qdrant_url)
    vindex = VectorIndex(make_embedder(model, device=s.embedding_device),
                         client=client, collection=coll)
    if client.collection_exists(coll) and client.count(coll).count == len(articles):
        logger.info("기존 컬렉션 재사용: %s", coll)
    else:
        vindex.build(articles)
    return vindex


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    articles = filter_as_of(load_corpus(s.cache_dir), s.as_of)
    gold = load_gold(Path("tests/qa_pairs.yaml"))

    bm25 = Bm25Index()
    bm25.build(articles)
    driver = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password))
    graph = GraphStore(driver)

    results: dict[str, dict] = {}
    try:
        for model in MODELS:
            logger.info("=== 임베딩·평가: %s ===", model)
            try:
                vindex = _get_or_build_index(s, model, articles)
                retr = Retriever(bm25=bm25, vector=vindex, graph=graph, articles=articles,
                                 reranker=NoopReranker(), rrf_k=s.rrf_k, graph_hops=s.graph_hops)
                results[model] = run_eval(retr, gold, STRATEGIES, top_k=s.top_k)
            except Exception as exc:  # noqa: BLE001 — 한 모델 실패가 나머지를 막지 않게
                logger.warning("모델 %s 평가 실패: %s", model, exc)

        if not results:
            raise SystemExit("모든 임베더 평가 실패")
        winner = pick_winner(results, metric="hit_rate@1", strategy="vector")
        logger.info("vector hit@1이 가장 높은 모델: %s", winner)

        # vector hit@1 기준 모델로 reranker on/off 비교
        vindex = _get_or_build_index(s, winner, articles)
        rerank_results = {}
        for label, rr in [("rerank=off", NoopReranker()),
                          ("rerank=on", CrossEncoderReranker(s.reranker_model,
                                                             device=s.reranker_device))]:
            retr = Retriever(bm25=bm25, vector=vindex, graph=graph, articles=articles,
                             reranker=rr, rrf_k=s.rrf_k, graph_hops=s.graph_hops)
            rerank_results[label] = run_eval(retr, gold, STRATEGIES, top_k=s.top_k)
    finally:
        driver.close()

    table = format_embedder_ablation(results, STRATEGIES)
    out = [f"# 임베더·검색 전략 비교 ({len(articles)} 조문, gold {len(gold)})", "",
           f"## 임베더 {len(results)}종 × 전략 (reranker off)", "", table, "",
           f"**vector hit@1이 가장 높은 모델: {winner}**", "",
           f"## {winner} reranker on/off", ""]
    for label, rep in rerank_results.items():
        out += [f"### {label}", "", to_markdown(rep), ""]
    Path("reports/embedder_ablation.md").write_text("\n".join(out), encoding="utf-8")
    Path("reports/embedder_ablation.json").write_text(
        json.dumps({"ablation": results, "winner": winner, "rerank": rerank_results},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"완료 → reports/embedder_ablation.md (기준 모델 {winner})")


if __name__ == "__main__":
    main()
