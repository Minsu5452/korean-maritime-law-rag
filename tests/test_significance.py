from korean_maritime_law_rag.evaluation.stats import mcnemar_from_pairs, mcnemar_p, wilson


def test_mcnemar_from_pairs_counts_discordant_and_computes_p():
    # a가 맞고 b가 틀린 경우(b_wins) 3개, 반대(c_wins) 1개
    a = [True, True, True, False, True]
    b = [False, False, False, False, True]
    r = mcnemar_from_pairs(a, b)
    assert r["b"] == 3 and r["c"] == 0  # a만 맞은 3개, b만 맞은 0개
    assert r["p"] == mcnemar_p(3, 0)


def test_mcnemar_from_pairs_requires_equal_length():
    import pytest
    with pytest.raises(ValueError):
        mcnemar_from_pairs([True], [True, False])


def test_mcnemar_no_discordant_pairs_is_one():
    assert mcnemar_p(0, 0) == 1.0


def test_mcnemar_symmetric_is_not_significant():
    assert mcnemar_p(5, 5) > 0.05


def test_mcnemar_extreme_split_is_significant():
    assert mcnemar_p(10, 0) < 0.05


def test_mcnemar_matches_reported_multihop_value():
    # 짝지은 정확검정 예시: 한 전략만 맞춘 문항 수가 14개, 9개인 경우
    assert abs(mcnemar_p(14, 9) - 0.4049) < 1e-4


def test_mcnemar_is_symmetric_in_args():
    assert mcnemar_p(14, 9) == mcnemar_p(9, 14)


def test_wilson_zero_n_is_degenerate():
    assert wilson(0, 0) == (0.0, 0.0)


def test_wilson_interval_contains_point_estimate():
    lo, hi = wilson(23, 29)  # 0.793
    assert lo < 23 / 29 < hi
    assert 0.0 <= lo <= hi <= 1.0


def test_wilson_all_success_caps_at_one():
    lo, hi = wilson(8, 8)
    assert hi == 1.0
    assert lo < 1.0
