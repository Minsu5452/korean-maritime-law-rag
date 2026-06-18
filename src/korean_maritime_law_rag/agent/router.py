from korean_maritime_law_rag.agent.state import QueryType

# 유형별 검색 전략(reports/embedder_ablation.md·significance.md 기준):
#   single     hybrid (vector와 hit@1 동률 — BM25 lexical 신호 보강)
#   definition vector (정의 조문은 의미 매칭이 가장 강함)
#   multihop   graph  (인용·위임 이웃 확장 — recall@10 최고; 리랭킹 결합 시 hit@1도 vector와 동급)
# 「법」 제N조처럼 정확 조문을 지목하는 질의는 분류 대신 parse_citation 정규식으로
# graph(정확 인용 pinning)에 라우팅한다(agent/graph.py). 그래서 여기 citation 유형은 없다.
_ROUTING: dict[str, str] = {
    "single": "hybrid",
    "definition": "vector",
    "multihop": "graph",
}


def route(query_type: QueryType) -> str:
    """질문 유형 → 검색 전략. unanswerable은 호출 전에 거절로 분기되므로 여기 없음."""
    if query_type not in _ROUTING:
        raise ValueError(f"route()가 처리할 수 없는 유형: {query_type!r}")
    return _ROUTING[query_type]
