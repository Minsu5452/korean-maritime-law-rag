"""지연 분포 요약(p50/p95 등). 외부 의존 없는 순수 함수."""


def percentiles(samples_ms: list[float]) -> dict[str, float]:
    """지연 표본(ms) → {p50, p95, mean, max, n}. nearest-rank 백분위. 빈 입력은 0."""
    if not samples_ms:
        return {"p50": 0.0, "p95": 0.0, "mean": 0.0, "max": 0.0, "n": 0}
    s = sorted(samples_ms)

    def pct(p: float) -> float:
        idx = min(len(s) - 1, round((p / 100) * (len(s) - 1)))
        return s[idx]

    return {
        "p50": pct(50),
        "p95": pct(95),
        "mean": sum(s) / len(s),
        "max": s[-1],
        "n": len(s),
    }
