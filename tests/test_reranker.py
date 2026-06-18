from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.retrieval.reranker import CrossEncoderReranker, NoopReranker


class _FakeCE:
    """CrossEncoder 대역 — 본문 길이를 점수로(다운로드 없이 재정렬 로직 검증)."""

    def predict(self, pairs):
        return [float(len(text)) for _, text in pairs]


def _meta():
    return {
        "1::제1조": Article(law_id="1", law_name="L", article_no="제1조", text="짧음"),
        "1::제2조": Article(law_id="1", law_name="L", article_no="제2조", text="아주 긴 본문입니다 정렬용"),
    }


def test_noop_reranker_truncates():
    out = NoopReranker().rerank("q", [("a", 1.0), ("b", 0.5)], {}, top_k=1)
    assert out == [("a", 1.0)]


def test_crossencoder_skips_candidates_missing_from_meta():
    rr = CrossEncoderReranker(model=_FakeCE())
    out = rr.rerank("q", [("1::제2조", 1.0), ("9::없음", 0.9), ("1::제1조", 0.8)], _meta(), top_k=2)
    ids = [d for d, _ in out]
    assert "9::없음" not in ids          # meta에 없는 그래프 확장 후보는 스킵(KeyError 방지)
    assert ids[0] == "1::제2조"           # 긴 본문이 상위로 재정렬


def test_crossencoder_all_missing_returns_passthrough():
    rr = CrossEncoderReranker(model=_FakeCE())
    out = rr.rerank("q", [("9::x", 0.9), ("8::y", 0.8)], _meta(), top_k=1)
    assert out == [("9::x", 0.9)]        # 전부 meta 밖이면 원순서 top_k로 폴백
