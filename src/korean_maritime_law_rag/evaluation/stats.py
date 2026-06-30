"""검색 평가용 통계 함수. 외부 의존 없이 표준 라이브러리만 사용해 단위 테스트가 쉽다."""
from math import comb, sqrt


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """이항 비율 k/n의 Wilson score 신뢰구간(기본 95%)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def mcnemar_p(b: int, c: int) -> float:
    """짝지은 이항 양측 정확검정. b, c는 두 전략의 불일치쌍 수(한쪽만 맞춘 횟수)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / (2 ** n))


def mcnemar_from_pairs(a_correct: list[bool], b_correct: list[bool]) -> dict:
    """두 전략의 문항별 정오(불리언) 리스트에서 불일치쌍과 McNemar p값을 계산한다.

    b = a만 맞은 수(a 우세), c = b만 맞은 수(b 우세). 반환: {b, c, p}.
    """
    if len(a_correct) != len(b_correct):
        raise ValueError("두 리스트 길이가 다르다")
    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    c = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)
    return {"b": b, "c": c, "p": mcnemar_p(b, c)}
