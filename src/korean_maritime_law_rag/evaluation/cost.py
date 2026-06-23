"""토큰 사용량과 단가로 질의당 비용을 추정한다. 외부 의존 없는 순수 함수.

단가(Price)는 코드에 박지 않고 호출 측에서 주입한다. 공개 단가는 바뀌므로,
측정 결과에는 사용한 단가를 함께 남겨 재현·정정이 가능하게 한다.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """1M 토큰당 USD 단가(입력/출력 분리)."""

    input_per_1m: float
    output_per_1m: float


def token_cost(input_tokens: int, output_tokens: int, price: Price) -> float:
    """입력·출력 토큰 수와 단가로 USD 비용을 계산한다."""
    return (input_tokens * price.input_per_1m + output_tokens * price.output_per_1m) / 1_000_000


def summarize(usages: list[tuple[int, int]], price: Price) -> dict[str, float]:
    """질의별 (입력, 출력) 토큰 목록 → 질의당 평균 토큰·비용과 합계. 빈 입력은 0."""
    n = len(usages)
    if n == 0:
        return {
            "n": 0,
            "mean_input": 0.0,
            "mean_output": 0.0,
            "mean_cost_usd": 0.0,
            "total_cost_usd": 0.0,
        }
    total_cost = sum(token_cost(i, o, price) for i, o in usages)
    return {
        "n": n,
        "mean_input": sum(i for i, _ in usages) / n,
        "mean_output": sum(o for _, o in usages) / n,
        "mean_cost_usd": total_cost / n,
        "total_cost_usd": total_cost,
    }
