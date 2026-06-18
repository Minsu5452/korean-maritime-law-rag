import pytest

from korean_maritime_law_rag.agent.router import route


def test_routes_by_type():
    assert route("single") == "hybrid"
    assert route("definition") == "vector"
    assert route("multihop") == "graph"


def test_unanswerable_is_not_routable():
    # unanswerable은 검색 전에 거절로 분기되므로 route()는 처리하지 않는다
    with pytest.raises(ValueError):
        route("unanswerable")
