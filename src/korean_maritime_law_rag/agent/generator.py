from typing import Literal, cast

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, create_model

from korean_maritime_law_rag.agent.state import GeneratedAnswer
from korean_maritime_law_rag.models import Article

_SYSTEM = """당신은 한국 해양 법령 상담 보조자다. 아래 제공된 조문에만 근거해 한국어로 답한다.
규칙:
- 제공된 조문에 근거가 없으면 추측하지 말고 "근거를 찾지 못했습니다"라고 답한다.
- citations에는 실제로 답변의 근거가 된 조문의 doc_id만 넣는다(제공된 조문의 doc_id 그대로)."""


def _format_context(articles: list[Article]) -> str:
    return "\n\n".join(
        f"[{a.doc_id}] {a.law_name} {a.article_no}({a.title}): {a.text}" for a in articles
    )


def generate(query: str, articles: list[Article], model: BaseChatModel) -> GeneratedAnswer:
    # citations를 검색된 doc_id로 제약(Literal enum) → LLM의 doc_id 절단·날조를 구조적으로 차단.
    # verify는 방어선으로 유지(가짜 LLM의 잘못된 인용 제거를 테스트가 계속 검증).
    doc_ids = [a.doc_id for a in articles]
    schema: type[BaseModel] = GeneratedAnswer
    if doc_ids:
        schema = create_model(
            "ConstrainedAnswer",
            answer=(str, ...),
            citations=(list[Literal[tuple(doc_ids)]], ...),  # type: ignore[misc]
        )
    structured = model.with_structured_output(schema)
    human = f"조문:\n{_format_context(articles)}\n\n질문: {query}"
    out = cast(GeneratedAnswer, structured.invoke([("system", _SYSTEM), ("human", human)]))
    return GeneratedAnswer(answer=out.answer, citations=list(out.citations))
