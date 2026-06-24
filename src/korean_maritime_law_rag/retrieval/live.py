"""로컬 인덱스에 없는 조문을 law.go.kr에서 질의 시점에 조회한다."""
import logging

from korean_maritime_law_rag.collectors.law_api import LawApiClient, LawNotCurrentError
from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.parsing.article_parser import parse_law

logger = logging.getLogger(__name__)


class LiveLawFallback:
    """로컬 코퍼스에 없는 조문을 law.go.kr에서 질의 시점에 가져온다(네트워크 의존, 캐시 미스 전용)."""

    def __init__(self, client: LawApiClient):
        self._client = client

    def fetch_article(self, law_name: str, article_no: str) -> Article | None:
        try:
            entry = self._client.search_law(law_name)
        except LawNotCurrentError:
            logger.info("실시간 법령 조회: '%s' 현행 없음", law_name)
            return None
        mst = entry.get("법령일련번호")
        if not mst:
            logger.info("실시간 법령 조회: '%s' 일련번호 없음", law_name)
            return None
        raw = self._client.fetch_law(mst)
        for art in parse_law(raw):
            if art.article_no == article_no:
                return art
        logger.info("실시간 법령 조회: '%s %s' 조문 없음", law_name, article_no)
        return None


def verify_consistency(local: Article, live: Article) -> bool:
    """로컬 캐시 조문과 라이브 원문이 같은지(본문 텍스트 일치) 확인한다."""
    return local.text.strip() == live.text.strip()
