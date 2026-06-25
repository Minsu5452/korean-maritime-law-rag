"""임베더 비교 결과를 포맷하고 기준 모델을 선택한다."""

_METRICS = ["hit_rate@1", "hit_rate@5", "recall@10", "mrr"]


def pick_winner(results: dict[str, dict], metric: str = "hit_rate@1",
                strategy: str = "graph") -> str:
    """모델→run_eval 결과에서 주어진 전략·지표 기준 최고 성능 모델명을 반환한다."""
    return max(results, key=lambda m: results[m][strategy]["overall"].get(metric, 0.0))


def format_embedder_ablation(results: dict[str, dict], strategies: list[str]) -> str:
    """모델 × 전략 비교표(markdown). 각 셀은 overall 지표."""
    metrics = [m for m in _METRICS if _has_metric(results, m)]
    lines = ["| 모델 | 전략 | " + " | ".join(m.replace("hit_rate@", "hit@") for m in metrics) + " |",
             "|---|---|" + "---|" * len(metrics)]
    for model, report in results.items():
        for strategy in strategies:
            block = report.get(strategy)
            if not block:
                continue
            overall = block["overall"]
            cells = " | ".join(f"{overall.get(m, 0.0):.3f}" for m in metrics)
            lines.append(f"| {model} | {strategy} | {cells} |")
    return "\n".join(lines)


def _has_metric(results: dict[str, dict], metric: str) -> bool:
    for report in results.values():
        for block in report.values():
            if isinstance(block, dict) and metric in block.get("overall", {}):
                return True
    return False
