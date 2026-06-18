"""RAGAS 평가 어댑터.

build_ragas_rows는 순수 함수라 CI에서 결정적으로 테스트되고, run_ragas는 ragas를
지연 import해 별도 실행 환경에서 4지표(faithfulness·answer relevancy·
context precision·context recall)를 계산한다."""
import logging

logger = logging.getLogger(__name__)

RAGAS_METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]


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


def run_ragas(rows: list[dict], judge_model: str = "gpt-4o") -> dict[str, float]:
    """ragas로 4지표 계산. ragas/openai 미설치 또는 실패 시 빈 dict."""
    if not rows:
        return {}
    try:
        from datasets import Dataset
        from langchain_openai import ChatOpenAI
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        ds = Dataset.from_list([{
            "question": r["user_input"],
            "answer": r["response"],
            "contexts": r["retrieved_contexts"],
            "ground_truth": r["reference"],
        } for r in rows])
        result = evaluate(
            ds,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
            llm=ChatOpenAI(model=judge_model, temperature=0),
        )
        return {k: float(v) for k, v in result.to_pandas().mean(numeric_only=True).items()}
    except Exception as exc:  # noqa: BLE001 — 평가 보조기능, 실패해도 파이프라인 진행
        logger.warning("RAGAS 평가 실패(%s)", exc)
        return {}
