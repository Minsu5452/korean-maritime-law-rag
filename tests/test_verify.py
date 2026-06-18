from korean_maritime_law_rag.agent.state import GeneratedAnswer
from korean_maritime_law_rag.agent.verify import verify_citations


def test_valid_citation_passes():
    ans = GeneratedAnswer(answer="...", citations=["100::제5조"])
    v = verify_citations(ans, {"100::제5조", "100::제8조"})
    assert v.valid_citations == ["100::제5조"]
    assert v.invalid_citations == []
    assert v.low_confidence is False


def test_hallucinated_citation_is_stripped():
    ans = GeneratedAnswer(answer="...", citations=["999::제1조"])
    v = verify_citations(ans, {"100::제5조"})
    assert v.valid_citations == []
    assert v.invalid_citations == ["999::제1조"]
    assert v.low_confidence is True  # 유효 인용 0개


def test_mixed_citations():
    ans = GeneratedAnswer(answer="...", citations=["100::제5조", "999::제1조"])
    v = verify_citations(ans, {"100::제5조"})
    assert v.valid_citations == ["100::제5조"]
    assert v.invalid_citations == ["999::제1조"]
    assert v.low_confidence is False
