from korean_maritime_law_rag.config import Settings
from korean_maritime_law_rag.observability import build_langfuse_callbacks


def test_langfuse_disabled_returns_no_callbacks():
    # 비활성(기본)이면 langfuse import 없이 빈 콜백 리스트
    assert build_langfuse_callbacks(Settings(langfuse_enabled=False)) == []


def test_langfuse_enabled_without_keys_returns_no_callbacks():
    # 키가 없으면 활성이라도 안전하게 빈 리스트(자체 호스팅 미구동 시 평가 중단 방지)
    s = Settings(langfuse_enabled=True, langfuse_public_key="", langfuse_secret_key="")
    assert build_langfuse_callbacks(s) == []
