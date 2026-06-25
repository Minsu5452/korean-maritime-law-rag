"""Langfuse(자체 호스팅) 모니터링 연결. 비활성/키 없음/미설치 시 안전하게 빈 콜백 반환."""
import logging
from typing import Any

from korean_maritime_law_rag.config import Settings

logger = logging.getLogger(__name__)


def build_langfuse_callbacks(settings: Settings) -> list[Any]:
    """langfuse_enabled이고 키가 있으면 LangChain용 Langfuse CallbackHandler 리스트를 만든다.

    자체 호스팅 인스턴스가 안 떠 있거나 langfuse 미설치여도 평가가 멈추지 않도록
    실패 시 빈 리스트를 반환한다(모니터링은 평가의 선택 기능)."""
    if not settings.langfuse_enabled:
        return []
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        logger.warning("langfuse_enabled이지만 키가 없어 비활성화 — MLR_LANGFUSE_*_KEY 확인")
        return []
    try:
        from langfuse.callback import CallbackHandler

        return [CallbackHandler(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )]
    except Exception as exc:  # 미설치·연결 실패 — 평가 진행 우선
        logger.warning("Langfuse 콜백 생성 실패(%s) — 모니터링 없이 진행", exc)
        return []
