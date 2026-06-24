from collections.abc import Iterator
from typing import TypedDict

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from korean_maritime_law_rag.agent.classifier import classify
from korean_maritime_law_rag.agent.evidence import grade_evidence
from korean_maritime_law_rag.agent.generator import generate
from korean_maritime_law_rag.agent.router import route
from korean_maritime_law_rag.agent.state import (
    AgentResponse,
    CitedArticle,
    GeneratedAnswer,
    QueryType,
)
from korean_maritime_law_rag.agent.verify import verify_citations
from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.retrieval.citation import parse_citation

_REFUSAL = "제공된 해양 법령에서 근거를 찾지 못했습니다."

_NODE_LABELS = {
    "classify": "질문 유형 분류",
    "retrieve": "검색",
    "grade_evidence": "근거 충분성 평가",
    "generate": "답변 생성",
    "verify": "인용 검증",
    "refuse": "거절",
    "refuse_low_confidence": "저신뢰 거절",
}


class _State(TypedDict, total=False):
    query: str
    active_query: str
    query_type: QueryType
    strategy: str
    articles: list[Article]
    answer: str
    citations: list[str]
    invalid_citations: list[str]
    refused: bool
    low_confidence: bool
    evidence_sufficient: bool
    evidence_reason: str
    rewritten_query: str
    retry_retrieval: bool
    retrieval_attempts: int
    generation_attempts: int
    used_live_fallback: bool


class Agent:
    """근거 평가와 검증 재시도를 갖춘 LangGraph RAG 에이전트."""

    def __init__(
        self,
        retriever,
        model: BaseChatModel,
        top_k: int = 5,
        max_retrieval_attempts: int = 2,
        max_generation_attempts: int = 2,
        live_fallback=None,
        callbacks=None,
    ):
        self._retriever = retriever
        self._model = model
        self._top_k = top_k
        self._max_retrieval_attempts = max(1, max_retrieval_attempts)
        self._max_generation_attempts = max(1, max_generation_attempts)
        self._live_fallback = live_fallback
        self._callbacks = callbacks or []
        self._graph = self._build()

    def _config(self) -> dict | None:
        # LangGraph가 콜백을 중첩 LLM 호출까지 전파한다(Langfuse 추적).
        return {"callbacks": self._callbacks} if self._callbacks else None

    def _build(self):
        g = StateGraph(_State)
        g.add_node("classify", self._classify)
        g.add_node("retrieve", self._retrieve)
        g.add_node("grade_evidence", self._grade_evidence)
        g.add_node("generate", self._generate)
        g.add_node("verify", self._verify)
        g.add_node("refuse", self._refuse)
        g.add_node("refuse_low_confidence", self._refuse_low_confidence)
        g.add_edge(START, "classify")
        g.add_conditional_edges("classify", self._branch,
                                {"answer": "retrieve", "refuse": "refuse"})
        g.add_edge("retrieve", "grade_evidence")
        g.add_conditional_edges(
            "grade_evidence",
            self._after_grade,
            {
                "generate": "generate",
                "retry_retrieval": "retrieve",
                "refuse": "refuse_low_confidence",
            },
        )
        g.add_edge("generate", "verify")
        g.add_conditional_edges(
            "verify",
            self._after_verify,
            {"regenerate": "generate", "done": END},
        )
        g.add_edge("refuse", END)
        g.add_edge("refuse_low_confidence", END)
        return g.compile()

    def _classify(self, state: _State) -> dict:
        return {"query_type": classify(state["query"], self._model), "active_query": state["query"]}

    def _branch(self, state: _State) -> str:
        return "refuse" if state["query_type"] == "unanswerable" else "answer"

    def _retrieve(self, state: _State) -> dict:
        search_query = state.get("active_query", state["query"])
        # 「법」 제N조처럼 정확 조문을 지목하면 분류와 무관하게 graph(정확 인용 pinning)로 라우팅.
        # 결정적 정규식으로 충분히 잡히는 신호라, 이를 위해 별도 LLM 분류 클래스를 두지 않는다.
        strategy = "graph" if parse_citation(search_query) else route(state["query_type"])
        results = self._retriever.search(search_query, strategy, self._top_k)
        articles = [self._retriever.meta[r.doc_id] for r in results
                    if r.doc_id in self._retriever.meta]
        used_live = state.get("used_live_fallback", False)
        # 로컬 인덱스에 없고 특정 조문을 지목한 질문이면 law.go.kr를 한 번 조회한다.
        if not articles and self._live_fallback is not None and (cite := parse_citation(search_query)):
            live = self._live_fallback.fetch_article(*cite)
            if live is not None:
                articles = [live]
                used_live = True
        return {
            "strategy": strategy,
            "articles": articles,
            "retry_retrieval": False,
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1,
            "used_live_fallback": used_live,
        }

    def _grade_evidence(self, state: _State) -> dict:
        grade = grade_evidence(
            query=state["query"],
            search_query=state.get("active_query", state["query"]),
            query_type=state["query_type"],
            articles=state.get("articles", []),
            model=self._model,
        )
        current_query = state.get("active_query", state["query"]).strip()
        rewritten = (grade.rewritten_query or "").strip()
        should_retry = (
            not grade.sufficient
            and bool(rewritten)
            and rewritten != current_query
            and state.get("retrieval_attempts", 0) < self._max_retrieval_attempts
        )
        updates: dict = {
            "evidence_sufficient": grade.sufficient,
            "evidence_reason": grade.reason,
            "retry_retrieval": should_retry,
        }
        if rewritten:
            updates["rewritten_query"] = rewritten
        if should_retry:
            updates["active_query"] = rewritten
        return updates

    def _after_grade(self, state: _State) -> str:
        if state.get("evidence_sufficient", False):
            return "generate"
        if state.get("retry_retrieval", False):
            return "retry_retrieval"
        return "refuse"

    def _generate(self, state: _State) -> dict:
        gen = generate(state["query"], state["articles"], self._model)
        return {
            "answer": gen.answer,
            "citations": gen.citations,
            "generation_attempts": state.get("generation_attempts", 0) + 1,
        }

    def _verify(self, state: _State) -> dict:
        retrieved = {a.doc_id for a in state["articles"]}
        v = verify_citations(
            GeneratedAnswer(answer=state["answer"], citations=state["citations"]), retrieved
        )
        invalid = [*state.get("invalid_citations", []), *v.invalid_citations]
        return {
            "answer": v.answer,
            "citations": v.valid_citations,
            "invalid_citations": invalid,
            "low_confidence": v.low_confidence,
        }

    def _after_verify(self, state: _State) -> str:
        if (
            state.get("low_confidence", False)
            and state.get("generation_attempts", 0) < self._max_generation_attempts
            and state.get("articles")
        ):
            return "regenerate"
        return "done"

    def _refuse(self, _state: _State) -> dict:
        return {
            "strategy": "none",
            "answer": _REFUSAL,
            "citations": [],
            "invalid_citations": [],
            "refused": True,
            "low_confidence": False,
        }

    def _refuse_low_confidence(self, state: _State) -> dict:
        return {
            "strategy": state.get("strategy", "none"),
            "answer": _REFUSAL,
            "citations": [],
            "refused": True,
            "low_confidence": True,
            "evidence_sufficient": False,
        }

    def answer(self, query: str) -> AgentResponse:
        return self._to_response(self._graph.invoke({"query": query}, config=self._config()))

    def stream(self, query: str) -> Iterator[dict]:
        """LangGraph 노드 실행을 순서대로 흘려보낸다(SSE 스트리밍용).

        각 노드가 끝날 때 진행 이벤트(step/label/현재 query_type·strategy)를 내고,
        마지막에 완성된 AgentResponse를 step='final'로 내보낸다. 재검색·재생성
        사이클에서는 retrieve/generate가 두 번 흐르므로 진행 상황이 그대로 드러난다.
        """
        final: dict = {}
        for update in self._graph.stream({"query": query}, stream_mode="updates",
                                         config=self._config()):
            for node, delta in update.items():
                if delta:
                    final.update(delta)
                yield {
                    "step": node,
                    "label": _NODE_LABELS.get(node, node),
                    "query_type": final.get("query_type"),
                    "strategy": final.get("strategy"),
                }
        yield {"step": "final", "response": self._to_response(final).model_dump()}

    def _to_response(self, final: dict) -> AgentResponse:
        citations = final.get("citations", [])
        meta = getattr(self._retriever, "meta", {})
        evidence = [
            CitedArticle(doc_id=doc_id, law_name=a.law_name, article_no=a.article_no,
                         law_type=a.law_type, title=a.title, text=a.text)
            for doc_id in citations
            if (a := meta.get(doc_id)) is not None
        ]
        return AgentResponse(
            answer=final["answer"],
            citations=citations,
            evidence=evidence,
            invalid_citations=final.get("invalid_citations", []),
            query_type=final["query_type"],
            strategy=final.get("strategy", "none"),
            refused=final.get("refused", False),
            low_confidence=final.get("low_confidence", False),
            evidence_sufficient=final.get("evidence_sufficient"),
            evidence_reason=final.get("evidence_reason", ""),
            rewritten_query=final.get("rewritten_query"),
            retrieval_attempts=final.get("retrieval_attempts", 0),
            generation_attempts=final.get("generation_attempts", 0),
            used_live_fallback=final.get("used_live_fallback", False),
        )
