from korean_maritime_law_rag.collectors.law_api import LawNotCurrentError
from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.retrieval.live import LiveLawFallback, verify_consistency

RAW = {"법령": {
    "기본정보": {"법령ID": "100", "법령명_한글": "선박안전법", "법종구분": {"content": "법률"}},
    "조문": {"조문단위": [{
        "조문여부": "조문", "조문번호": "5", "조문제목": "검사",
        "조문내용": "제5조(검사) 선박은 검사를 받아야 한다.",
    }]},
}}


class _FakeClient:
    def __init__(self, raw: dict, found: bool = True):
        self._raw, self._found = raw, found
        self.fetched = False

    def search_law(self, name: str) -> dict:
        if not self._found:
            raise LawNotCurrentError(name)
        return {"법령일련번호": "1", "법령ID": "100"}

    def fetch_law(self, mst: str) -> dict:
        self.fetched = True
        return self._raw


def test_live_fallback_fetches_named_article():
    fb = LiveLawFallback(_FakeClient(RAW))
    art = fb.fetch_article("선박안전법", "제5조")
    assert art is not None
    assert art.article_no == "제5조"
    assert "검사" in art.text


def test_live_fallback_returns_none_when_article_absent():
    fb = LiveLawFallback(_FakeClient(RAW))
    assert fb.fetch_article("선박안전법", "제999조") is None


def test_live_fallback_returns_none_when_law_not_current():
    client = _FakeClient(RAW, found=False)
    fb = LiveLawFallback(client)
    assert fb.fetch_article("폐지법", "제1조") is None
    assert client.fetched is False  # 검색 단계에서 차단 — 불필요한 fetch 없음


def test_verify_consistency_detects_match_and_mismatch():
    local = Article(law_id="100", law_name="선박안전법", article_no="제5조",
                    text="선박은 검사를 받아야 한다.")
    same = Article(law_id="100", law_name="선박안전법", article_no="제5조",
                   text="선박은 검사를 받아야 한다.")
    diff = Article(law_id="100", law_name="선박안전법", article_no="제5조",
                   text="선박은 검사를 면제받는다.")
    assert verify_consistency(local, same) is True
    assert verify_consistency(local, diff) is False
