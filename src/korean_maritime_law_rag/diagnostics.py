from pathlib import Path

from pydantic import BaseModel

from korean_maritime_law_rag.config import Settings


class DiagnosticCheck(BaseModel):
    name: str
    ok: bool
    detail: str


def _check_raw_cache(cache_dir: Path) -> DiagnosticCheck:
    if not cache_dir.exists():
        return DiagnosticCheck(name="raw_cache", ok=False, detail=f"{cache_dir} not found")
    count = len(list(cache_dir.glob("*.json")))
    if count == 0:
        return DiagnosticCheck(name="raw_cache", ok=False, detail=f"{cache_dir} has no JSON files")
    return DiagnosticCheck(name="raw_cache", ok=True, detail=f"{count} raw law files")


def _check_file(name: str, path: Path) -> DiagnosticCheck:
    if not path.exists():
        return DiagnosticCheck(name=name, ok=False, detail=f"{path} not found")
    if path.stat().st_size == 0:
        return DiagnosticCheck(name=name, ok=False, detail=f"{path} is empty")
    return DiagnosticCheck(name=name, ok=True, detail=str(path))


def check_local_artifacts(
    settings: Settings,
    bm25_path: Path = Path("data/bm25.pkl"),
) -> list[DiagnosticCheck]:
    qdrant_detail = settings.qdrant_url or "in-memory Qdrant"
    embedding_cache = (
        DiagnosticCheck(name="embedding_cache", ok=True, detail="disabled")
        if settings.embedding_cache is None
        else _check_file("embedding_cache", settings.embedding_cache)
    )
    return [
        _check_raw_cache(settings.cache_dir),
        _check_file("bm25", bm25_path),
        embedding_cache,
        DiagnosticCheck(name="qdrant_config", ok=True, detail=qdrant_detail),
        DiagnosticCheck(name="neo4j_config", ok=bool(settings.neo4j_uri), detail=settings.neo4j_uri),
    ]
