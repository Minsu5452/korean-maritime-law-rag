from pathlib import Path

from korean_maritime_law_rag.config import Settings
from korean_maritime_law_rag.diagnostics import check_local_artifacts


def test_check_local_artifacts_reports_cache_and_bm25_status(tmp_path: Path):
    cache = tmp_path / "cache"
    settings = Settings(cache_dir=cache, qdrant_url=None, embedding_cache=tmp_path / "missing.npz")

    checks = check_local_artifacts(settings, bm25_path=tmp_path / "missing.pkl")

    by_name = {check.name: check for check in checks}
    assert by_name["raw_cache"].ok is False
    assert "not found" in by_name["raw_cache"].detail
    assert by_name["bm25"].ok is False
    assert by_name["embedding_cache"].ok is False
    assert by_name["qdrant_config"].ok is True


def test_check_local_artifacts_accepts_existing_cache_and_bm25(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "law.json").write_text('{"법령": {"조문": {"조문단위": []}}}', encoding="utf-8")
    bm25 = tmp_path / "bm25.pkl"
    bm25.write_bytes(b"index")
    embedding_cache = tmp_path / "embeddings.npz"
    embedding_cache.write_bytes(b"vectors")

    settings = Settings(
        cache_dir=cache,
        qdrant_url="http://localhost:6333",
        embedding_cache=embedding_cache,
    )
    checks = check_local_artifacts(settings, bm25_path=bm25)

    assert all(check.ok for check in checks)


def test_check_local_artifacts_treats_disabled_embedding_cache_as_ok(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "law.json").write_text("{}", encoding="utf-8")
    bm25 = tmp_path / "bm25.pkl"
    bm25.write_bytes(b"index")

    settings = Settings(cache_dir=cache, embedding_cache=None)
    checks = check_local_artifacts(settings, bm25_path=bm25)

    by_name = {check.name: check for check in checks}
    assert by_name["embedding_cache"].ok is True
    assert by_name["embedding_cache"].detail == "disabled"
