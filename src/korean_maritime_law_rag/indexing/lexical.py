from kiwipiepy import Kiwi
from rank_bm25 import BM25Okapi

from korean_maritime_law_rag.models import Article

_KEEP_TAGS = ("N", "V", "M", "SL", "SN", "XR")


class Bm25Index:
    def __init__(self) -> None:
        self._kiwi = Kiwi()
        self._doc_ids: list[str] = []
        self._bm25: BM25Okapi | None = None

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state["_kiwi"] = None  # Kiwi는 pickle 불가 — 역직렬화 시 재생성
        return state

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self._kiwi = Kiwi()

    def _tokenize(self, text: str) -> list[str]:
        return [t.form for t in self._kiwi.tokenize(text) if t.tag.startswith(_KEEP_TAGS)]

    def build(self, articles: list[Article]) -> None:
        self._doc_ids = [a.doc_id for a in articles]
        corpus = [
            self._tokenize(f"{a.law_name} {a.article_no} {a.title} {a.text}") for a in articles
        ]
        self._bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        assert self._bm25 is not None, "build() 먼저 호출"
        scores = self._bm25.get_scores(self._tokenize(query))
        ranked = sorted(zip(self._doc_ids, scores), key=lambda x: x[1], reverse=True)
        return [(d, float(s)) for d, s in ranked[:top_k] if s > 0]
