from typing import cast

from langchain_core.language_models import BaseChatModel

from korean_maritime_law_rag.agent.state import QueryType, QueryTypeResult

_SYSTEM = """당신은 한국 해양·수산 법령 질의를 다음 4개 유형 중 하나로 분류한다.
- single: 한 조문만으로 답해지는 사실 질문
- definition: 용어의 정의를 묻는 질문
- multihop: 인용·준용을 따라가야 답이 나오는 질문(예: 위반 시 처벌, 준용되는 규정)
- unanswerable: 해양수산부·해양경찰청 소관 법령(선박안전·어선·수산업·양식·항만·항만운송·해운·선원·해양환경·해사안전·수상구조·해양경찰·해양사고심판 등) 범위를 벗어나 형법·세법·출입국·공정거래·식품위생 등 다른 법으로 답해야 하는 질문
질문만 보고 가장 적합한 하나를 고른다.
참고: 「선박안전법」 제8조처럼 법령명과 조문번호를 직접 지목하는 질문은 정규식으로 별도 라우팅되므로 여기서 따로 분류하지 않는다."""


def classify(query: str, model: BaseChatModel) -> QueryType:
    structured = model.with_structured_output(QueryTypeResult)
    result = cast(QueryTypeResult, structured.invoke([("system", _SYSTEM), ("human", query)]))
    return result.query_type
