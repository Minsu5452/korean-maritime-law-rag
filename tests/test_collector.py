import json
from pathlib import Path

import httpx
import pytest
import respx

from korean_maritime_law_rag.collectors.law_api import (
    LawApiClient,
    LawNotCurrentError,
    is_amended,
    subordinate_names,
)

FIXTURES = Path(__file__).parent / "fixtures"
SEARCH_FIXTURE = json.loads((FIXTURES / "lawsearch_sample.json").read_text(encoding="utf-8"))
SERVICE_FIXTURE = json.loads((FIXTURES / "lawservice_sample.json").read_text(encoding="utf-8"))


@respx.mock
def test_search_law_returns_current_entry():
    respx.get("https://www.law.go.kr/DRF/lawSearch.do").mock(
        return_value=httpx.Response(200, json=SEARCH_FIXTURE)
    )
    client = LawApiClient(oc="testoc")
    entry = client.search_law("해양경찰법")
    assert entry["현행연혁코드"] == "현행"
    assert "법령일련번호" in entry


@respx.mock
def test_search_law_raises_when_no_current():
    stale = {"LawSearch": {"law": [{"법령명한글": "해사안전법", "현행연혁코드": "연혁",
                                    "법령일련번호": "1", "법령ID": "1"}]}}
    respx.get("https://www.law.go.kr/DRF/lawSearch.do").mock(
        return_value=httpx.Response(200, json=stale)
    )
    client = LawApiClient(oc="testoc")
    with pytest.raises(LawNotCurrentError):
        client.search_law("해사안전법")


@respx.mock
def test_html_response_raises_clear_error():
    # 미등록 OC 키 시나리오: HTTP 200 + HTML
    respx.get("https://www.law.go.kr/DRF/lawSearch.do").mock(
        return_value=httpx.Response(200, text="<html><body>인증 실패</body></html>",
                                    headers={"content-type": "text/html; charset=utf-8"})
    )
    client = LawApiClient(oc="badkey")
    with pytest.raises(ValueError, match="OC 키"):
        client.search_law("해양경찰법")
    assert respx.calls.call_count == 1  # ValueError는 retry 대상 아님 — 1회 호출로 즉시 실패


@respx.mock
def test_collect_writes_cache(tmp_path: Path):
    respx.get("https://www.law.go.kr/DRF/lawSearch.do").mock(
        return_value=httpx.Response(200, json=SEARCH_FIXTURE)
    )
    respx.get("https://www.law.go.kr/DRF/lawService.do").mock(
        return_value=httpx.Response(200, json=SERVICE_FIXTURE)
    )
    client = LawApiClient(oc="testoc")
    paths = client.collect(["해양경찰법"], cache_dir=tmp_path)
    assert len(paths) == 1
    saved = json.loads(paths[0].read_text(encoding="utf-8"))
    assert "법령" in saved


def test_subordinate_names_appends_decree_and_rule():
    assert subordinate_names("선박안전법") == ["선박안전법 시행령", "선박안전법 시행규칙"]


def test_is_amended_detects_new_promulgation_number():
    cached = {"법령": {"기본정보": {"공포번호": "20727"}}}
    assert is_amended(cached, {"공포번호": "21000"}) is True
    assert is_amended(cached, {"공포번호": "20727"}) is False
    assert is_amended(cached, {}) is False  # 최신 정보 없으면 보수적으로 변경 아님


@respx.mock
def test_collect_skips_laws_without_current_version(tmp_path: Path):
    # 없는 시행규칙처럼 현행 법령이 없으면 스킵하고 나머지를 계속 수집한다
    respx.get("https://www.law.go.kr/DRF/lawSearch.do").mock(
        side_effect=[
            httpx.Response(200, json=SEARCH_FIXTURE),                # 해양경찰법 → 현행 있음
            httpx.Response(200, json={"LawSearch": {"law": []}}),    # 없는 법 → 현행 없음
        ]
    )
    respx.get("https://www.law.go.kr/DRF/lawService.do").mock(
        return_value=httpx.Response(200, json=SERVICE_FIXTURE)
    )
    client = LawApiClient(oc="testoc")
    paths = client.collect(["해양경찰법", "없는법 시행규칙"], cache_dir=tmp_path)
    assert len(paths) == 1  # 둘째는 스킵
