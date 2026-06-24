"""RAGAS 평가 입력 어댑터.

build_ragas_rows는 평가 레코드를 RAGAS 입력 스키마로 변환하는 순수 함수다.
실제 채점은 의존성 충돌을 피해 격리한 venv의 scripts/ragas_score.py에서 수행한다."""


def build_ragas_rows(records: list[dict]) -> list[dict]:
    """평가 레코드를 RAGAS 입력 스키마로 변환한다. contexts가 빈 항목은 제외한다.

    record: {question, answer, contexts: list[str], reference: str}
    row:    {user_input, response, retrieved_contexts, reference}
    """
    rows: list[dict] = []
    for r in records:
        contexts = r.get("contexts") or []
        if not contexts:
            continue
        rows.append({
            "user_input": r["question"],
            "response": r["answer"],
            "retrieved_contexts": list(contexts),
            "reference": r.get("reference", ""),
        })
    return rows
