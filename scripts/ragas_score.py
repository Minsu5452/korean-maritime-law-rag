"""격리 venv에서 reports/ragas_rows.json을 읽어 RAGAS 지표를 계산한다.

ragas 0.2가 에이전트 측 langchain 스택과 충돌해 별도 venv에서 실행한다(프로젝트 import 없음).
사용: 격리한 venv에서 `OPENAI_API_KEY=... python scripts/ragas_score.py [judge_model]`
"""
import json
import sys
from pathlib import Path

from datasets import Dataset
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

judge = sys.argv[1] if len(sys.argv) > 1 else "gpt-4o"
rows = json.loads(Path("reports/ragas_rows.json").read_text(encoding="utf-8"))
ds = Dataset.from_list([{
    "question": r["user_input"], "answer": r["response"],
    "contexts": r["retrieved_contexts"], "ground_truth": r["reference"],
} for r in rows])

result = evaluate(
    ds,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=ChatOpenAI(model=judge, temperature=0),
)
metrics = {k: float(v) for k, v in result.to_pandas().mean(numeric_only=True).items()}

out = Path("reports")
(out / "ragas_eval.json").write_text(
    json.dumps({"metrics": metrics, "judge": judge, "n": len(rows)}, ensure_ascii=False, indent=2),
    encoding="utf-8")
lines = [f"# RAGAS 평가 (judge={judge}, n={len(rows)})", "", "| 지표 | 값 |", "|---|---|"]
lines += [f"| {k} | {v:.3f} |" for k, v in metrics.items()]
(out / "ragas_eval.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
