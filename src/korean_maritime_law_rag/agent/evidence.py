from typing import cast

from langchain_core.language_models import BaseChatModel

from korean_maritime_law_rag.agent.state import EvidenceGrade, QueryType
from korean_maritime_law_rag.models import Article

_SYSTEM = """당신은 한국 해양 법령 RAG의 evidence grader다.
역할:
- 검색된 조문만 보고 원 질문에 답할 근거가 충분한지 판단한다.
- sufficient는 검색 조문 안에서 답변과 인용을 만들 수 있을 때만 true다.
- 근거가 부족하면 rewritten_query에 재검색용 한국어 검색어를 제안한다.
- rewritten_query는 원 질문의 의도를 유지하되 법령명, 조문번호, 벌칙, 정의, 준용 같은 검색 단서를 보강한다.
- 검색된 조문 밖의 법률 지식으로 충분하다고 판단하지 않는다."""


def _format_articles(articles: list[Article]) -> str:
    if not articles:
        return "(검색된 조문 없음)"
    return "\n\n".join(
        f"[{a.doc_id}] {a.law_name} {a.article_no}({a.title}): {a.text[:900]}"
        for a in articles
    )


def grade_evidence(
    query: str,
    search_query: str,
    query_type: QueryType,
    articles: list[Article],
    model: BaseChatModel,
) -> EvidenceGrade:
    structured = model.with_structured_output(EvidenceGrade)
    human = (
        f"원 질문: {query}\n"
        f"현재 검색어: {search_query}\n"
        f"질문 유형: {query_type}\n\n"
        f"검색된 조문:\n{_format_articles(articles)}"
    )
    return cast(EvidenceGrade, structured.invoke([("system", _SYSTEM), ("human", human)]))
