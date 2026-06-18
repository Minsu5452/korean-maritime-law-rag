from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.agent.state import EvidenceGrade, GeneratedAnswer, QueryTypeResult
from korean_maritime_law_rag.llm import FakeChatModel
from korean_maritime_law_rag.models import Article, SearchResult


class StubRetriever:
    """Retriever 시그니처 더블: search() + meta."""

    def __init__(self, articles: list[Article] | list[list[Article]]):
        if articles and isinstance(articles[0], list):
            self._responses = list(articles)
            all_articles = [article for response in self._responses for article in response]
        else:
            self._responses = None
            all_articles = articles
        self.meta = {a.doc_id: a for a in all_articles}
        self.last_strategy: str | None = None
        self.calls: list[tuple[str, str, int]] = []

    def search(self, query, strategy, top_k):
        self.last_strategy = strategy
        self.calls.append((query, strategy, top_k))
        articles = self._responses.pop(0) if self._responses is not None else list(self.meta.values())
        return [SearchResult(doc_id=a.doc_id, score=1.0) for a in articles[:top_k]]


def _corpus():
    return [
        Article(law_id="100", law_name="테스트선박법", article_no="제83조",
                title="벌칙", text="제7조를 위반한 자는 3년 이하의 징역."),
        Article(law_id="100", law_name="테스트선박법", article_no="제7조",
                title="건조검사", text="선박을 건조하려는 자는 건조검사를 받아야 한다."),
    ]


def test_answerable_flow_routes_and_verifies():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="multihop"),
        EvidenceGrade(sufficient=True, reason="처벌 조문과 의무 조문이 함께 검색됨"),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조", "999::없음"]),
    ])
    resp = Agent(retriever, model, top_k=5).answer("건조검사 위반 처벌은?")
    assert resp.query_type == "multihop"
    assert resp.strategy == "graph"            # multihop → graph
    assert retriever.last_strategy == "graph"
    assert resp.citations == ["100::제83조"]    # 환각 인용 999 제거됨
    assert resp.refused is False


def test_unanswerable_is_refused_without_retrieval():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[QueryTypeResult(query_type="unanswerable")])
    resp = Agent(retriever, model, top_k=5).answer("소득세 계산법은?")
    assert resp.refused is True
    assert resp.citations == []
    assert retriever.last_strategy is None      # 검색 호출 안 됨


def test_all_hallucinated_citations_marks_low_confidence():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="single"),
        EvidenceGrade(sufficient=True, reason="관련 조문 검색됨"),
        GeneratedAnswer(answer="아마도...", citations=["999::없음"]),
    ])
    resp = Agent(retriever, model, top_k=5, max_generation_attempts=1).answer("q")
    assert resp.citations == []          # 환각 전부 제거
    assert resp.low_confidence is True   # 유효 인용 0개 → 저신뢰
    assert resp.refused is False         # 거절은 아님(답변은 냄)
    assert resp.invalid_citations == ["999::없음"]


def test_valid_citation_is_not_low_confidence():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="multihop"),
        EvidenceGrade(sufficient=True, reason="처벌 조문 검색됨"),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조"]),
    ])
    resp = Agent(retriever, model, top_k=5).answer("처벌은?")
    assert resp.low_confidence is False


def test_weak_evidence_rewrites_query_and_retrieves_again():
    articles = _corpus()
    retriever = StubRetriever([[], articles])
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="multihop"),
        EvidenceGrade(
            sufficient=False,
            reason="처벌 조문이 검색되지 않음",
            rewritten_query="건조검사 위반 벌칙 테스트선박법 제83조",
        ),
        EvidenceGrade(sufficient=True, reason="재검색에서 벌칙 조문 검색됨"),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조"]),
    ])
    resp = Agent(retriever, model, top_k=5).answer("건조검사 위반 처벌은?")
    assert retriever.calls == [
        ("건조검사 위반 처벌은?", "graph", 5),
        ("건조검사 위반 벌칙 테스트선박법 제83조", "graph", 5),
    ]
    assert resp.retrieval_attempts == 2
    assert resp.rewritten_query == "건조검사 위반 벌칙 테스트선박법 제83조"
    assert resp.evidence_sufficient is True
    assert resp.citations == ["100::제83조"]


def test_insufficient_evidence_after_retry_budget_refuses():
    retriever = StubRetriever([[], []])
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="single"),
        EvidenceGrade(sufficient=False, reason="해양 법령 근거 없음", rewritten_query="해양 법령 q"),
        EvidenceGrade(sufficient=False, reason="재검색 후에도 근거 없음"),
    ])
    resp = Agent(retriever, model, top_k=5, max_retrieval_attempts=2).answer("q")
    assert resp.refused is True
    assert resp.low_confidence is True
    assert resp.citations == []
    assert resp.retrieval_attempts == 2
    assert resp.evidence_sufficient is False
    assert "근거를 찾지 못했습니다" in resp.answer


def test_stream_emits_node_progress_then_final():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="multihop"),
        EvidenceGrade(sufficient=True, reason="처벌 조문 검색됨"),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조"]),
    ])
    events = list(Agent(retriever, model, top_k=5).stream("건조검사 위반 처벌은?"))
    steps = [e["step"] for e in events]
    assert steps[0] == "classify"
    assert {"retrieve", "generate", "verify"} <= set(steps)
    assert steps[-1] == "final"
    final = events[-1]["response"]
    assert final["query_type"] == "multihop"
    assert final["strategy"] == "graph"
    assert final["citations"] == ["100::제83조"]


class _StubFallback:
    def __init__(self, article: Article | None):
        self._article = article
        self.calls: list[tuple[str, str]] = []

    def fetch_article(self, law_name: str, article_no: str) -> Article | None:
        self.calls.append((law_name, article_no))
        return self._article


def test_live_fallback_used_when_local_miss_and_citation_named():
    retriever = StubRetriever([[]])  # 로컬은 빈 결과(미스)
    live_art = Article(law_id="900", law_name="외부법", article_no="제5조", text="외부법 제5조 본문")
    fb = _StubFallback(live_art)
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="single"),
        EvidenceGrade(sufficient=True, reason="라이브 조문으로 충분"),
        GeneratedAnswer(answer="외부법 제5조 내용입니다.", citations=["900::제5조"]),
    ])
    resp = Agent(retriever, model, top_k=5, live_fallback=fb).answer("「외부법」 제5조는?")
    assert fb.calls == [("외부법", "제5조")]
    assert resp.used_live_fallback is True
    assert resp.citations == ["900::제5조"]


def test_live_fallback_not_triggered_when_local_hits():
    retriever = StubRetriever(_corpus())  # 로컬 히트 있음
    fb = _StubFallback(Article(law_id="900", law_name="외부법", article_no="제5조", text="x"))
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="multihop"),
        EvidenceGrade(sufficient=True, reason="로컬 조문 충분"),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조"]),
    ])
    resp = Agent(retriever, model, top_k=5, live_fallback=fb).answer("「테스트선박법」 제83조는?")
    assert fb.calls == []  # 로컬에서 찾았으므로 실시간 조회를 호출하지 않음
    assert resp.used_live_fallback is False


def test_invalid_citation_triggers_one_regeneration():
    retriever = StubRetriever(_corpus())
    model = FakeChatModel(structured_outputs=[
        QueryTypeResult(query_type="single"),
        EvidenceGrade(sufficient=True, reason="관련 조문 검색됨"),
        GeneratedAnswer(answer="처벌됩니다.", citations=["999::없음"]),
        GeneratedAnswer(answer="3년 이하의 징역.", citations=["100::제83조"]),
    ])
    resp = Agent(retriever, model, top_k=5, max_generation_attempts=2).answer("처벌은?")
    assert resp.generation_attempts == 2
    assert resp.invalid_citations == ["999::없음"]
    assert resp.citations == ["100::제83조"]
    assert resp.low_confidence is False
