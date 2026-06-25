from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from ranx import Qrels, Run, evaluate as ranx_evaluate

from korean_maritime_law_rag.agent.state import QueryType


class GoldItem(BaseModel):
    id: str
    question: str
    type: QueryType
    gold: list[str] = Field(default_factory=list)


def load_gold(path: Path) -> list[GoldItem]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [GoldItem(**item) for item in data]


def validate_gold(items: list[GoldItem], corpus_ids: set[str],
                  min_multihop_ratio: float = 0.25) -> list[str]:
    errors: list[str] = []
    ids = [g.id for g in items]
    if len(ids) != len(set(ids)):
        errors.append("중복된 id가 있음")
    for g in items:
        if g.type == "unanswerable":
            if g.gold:
                errors.append(f"{g.id}: unanswerable인데 gold가 비어있지 않음")
            continue
        if not g.gold:
            errors.append(f"{g.id}: gold가 비어 있음")
        if len(g.gold) != len(set(g.gold)):
            errors.append(f"{g.id}: gold에 중복 doc_id가 있음")
        for d in g.gold:
            if d not in corpus_ids:
                errors.append(f"{g.id}: 코퍼스에 없는 doc_id '{d}'")
    answerable = [g for g in items if g.type != "unanswerable"]
    if answerable:
        ratio = sum(1 for g in answerable if g.type == "multihop") / len(answerable)
        if ratio < min_multihop_ratio:
            errors.append(f"multihop 비율 {ratio:.0%} < {min_multihop_ratio:.0%} — 평가 구성 확인 필요")
    return errors


METRICS = ["hit_rate@1", "hit_rate@5", "recall@10", "mrr"]


def run_eval(retriever, gold: list[GoldItem], strategies: list[str], top_k: int = 10) -> dict:
    answerable = [g for g in gold if g.type != "unanswerable"]
    qrels = {g.id: {d: 1 for d in g.gold} for g in answerable}
    report: dict = {}
    for strategy in strategies:
        run = {}
        for g in answerable:
            results = retriever.search(g.question, strategy=strategy, top_k=top_k)
            run[g.id] = {r.doc_id: r.score for r in results}
        overall = ranx_evaluate(Qrels(qrels), Run(run), METRICS)
        by_type: dict = {}
        for qtype in sorted({g.type for g in answerable}):
            ids = [g.id for g in answerable if g.type == qtype]
            by_type[qtype] = ranx_evaluate(
                Qrels({i: qrels[i] for i in ids}), Run({i: run[i] for i in ids}), METRICS
            )
        report[strategy] = {"overall": overall, "by_type": by_type,
                            "n_questions": len(answerable)}
    return report


def to_markdown(report: dict) -> str:
    lines = ["| 전략 | 유형 | " + " | ".join(m.replace("hit_rate@", "hit@") for m in METRICS) + " |",
             "|---|---|" + "---|" * len(METRICS)]
    for strategy, data in report.items():
        rows = [("overall", data["overall"])] + sorted(data["by_type"].items())
        for label, metrics in rows:
            cells = " | ".join(f"{metrics[m]:.3f}" for m in METRICS)
            lines.append(f"| {strategy} | {label} | {cells} |")
    return "\n".join(lines)


def agent_metrics(records: list[dict]) -> dict:
    """에이전트 평가 지표. records: [{id, gold_type, pred_type, gold_docs, cited_docs, refused}].

    - classification_accuracy: pred_type == gold_type 비율
    - citation_hit_rate: answerable에서 gold_docs 중 하나라도 cited_docs에 있는 비율
    - refusal_accuracy: unanswerable에서 refused=True인 비율
    """
    total = len(records)
    correct_type = sum(1 for r in records if r["pred_type"] == r["gold_type"])
    answerable = [r for r in records if r["gold_type"] != "unanswerable"]
    unanswerable = [r for r in records if r["gold_type"] == "unanswerable"]
    cite_hits = sum(
        1 for r in answerable if set(r["gold_docs"]) & set(r["cited_docs"])
    )
    refusals = sum(1 for r in unanswerable if r["refused"])
    return {
        "classification_accuracy": correct_type / total if total else 0.0,
        "citation_hit_rate": cite_hits / len(answerable) if answerable else 0.0,
        "refusal_accuracy": refusals / len(unanswerable) if unanswerable else 0.0,
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
    }
