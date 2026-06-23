from korean_maritime_law_rag.evaluation.cost import Price, summarize, token_cost


def test_token_cost_known_rate():
    price = Price(input_per_1m=0.15, output_per_1m=0.60)  # gpt-4o-mini 예시 단가
    # (1000*0.15 + 500*0.60) / 1_000_000 = 450 / 1_000_000
    assert token_cost(1000, 500, price) == 0.00045


def test_token_cost_zero():
    price = Price(input_per_1m=0.15, output_per_1m=0.60)
    assert token_cost(0, 0, price) == 0.0


def test_summarize_per_query_means():
    price = Price(input_per_1m=0.15, output_per_1m=0.60)
    usages = [(1000, 500), (3000, 1500)]  # 질의 2건의 (입력, 출력) 토큰
    r = summarize(usages, price)
    assert r["n"] == 2
    assert r["mean_input"] == 2000.0
    assert r["mean_output"] == 1000.0
    # 질의당 비용: [0.00045, 0.00135] → 평균 0.0009
    assert r["mean_cost_usd"] == 0.0009
    assert r["total_cost_usd"] == 0.0018


def test_summarize_empty_is_zero():
    price = Price(input_per_1m=0.15, output_per_1m=0.60)
    assert summarize([], price) == {
        "n": 0,
        "mean_input": 0.0,
        "mean_output": 0.0,
        "mean_cost_usd": 0.0,
        "total_cost_usd": 0.0,
    }
