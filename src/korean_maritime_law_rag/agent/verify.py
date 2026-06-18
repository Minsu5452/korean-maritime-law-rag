from korean_maritime_law_rag.agent.state import GeneratedAnswer, VerifiedAnswer


def verify_citations(answer: GeneratedAnswer, retrieved_ids: set[str]) -> VerifiedAnswer:
    """인용 doc_id가 실제 검색 결과에 있는지 확인. 없으면 환각으로 분류·제거."""
    valid = [c for c in answer.citations if c in retrieved_ids]
    invalid = [c for c in answer.citations if c not in retrieved_ids]
    return VerifiedAnswer(
        answer=answer.answer,
        valid_citations=valid,
        invalid_citations=invalid,
        low_confidence=len(valid) == 0,
    )
