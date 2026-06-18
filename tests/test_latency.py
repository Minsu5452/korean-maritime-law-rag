from korean_maritime_law_rag.evaluation.latency import percentiles


def test_percentiles_summary():
    r = percentiles([float(x) for x in range(10, 101, 10)])  # 10..100
    assert r["n"] == 10
    assert r["max"] == 100.0
    assert r["mean"] == 55.0
    assert r["p50"] in (50.0, 60.0)   # nearest-rank
    assert r["p95"] >= 90.0


def test_percentiles_empty_is_zero():
    r = percentiles([])
    assert r == {"p50": 0.0, "p95": 0.0, "mean": 0.0, "max": 0.0, "n": 0}


def test_percentiles_single_sample():
    r = percentiles([42.0])
    assert r["p50"] == 42.0 and r["p95"] == 42.0 and r["max"] == 42.0 and r["n"] == 1
