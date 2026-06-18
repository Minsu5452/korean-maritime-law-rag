"""Encode article embeddings to an NPZ cache.

Usage:
  MLR_EMBEDDING_DEVICE=cuda uv run python scripts/embed_corpus.py
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.indexing.embedding_cache import EmbeddingCache
from korean_maritime_law_rag.indexing.embedder import KureEmbedder


def main() -> None:
    settings = load_settings(Path("configs/demo.yaml"))
    if not settings.embedding_cache:
        raise SystemExit("MLR_EMBEDDING_CACHE must be set")

    articles = load_corpus(settings.cache_dir)
    texts = [f"{article.article_no} {article.title}\n{article.text}" for article in articles]
    embedder = KureEmbedder(settings.embedding_model, device=settings.embedding_device)

    started = time.perf_counter()
    vectors = embedder.encode(texts)
    elapsed = time.perf_counter() - started

    cache = EmbeddingCache(doc_ids=[article.doc_id for article in articles], vectors=vectors)
    cache.save(settings.embedding_cache)

    meta = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "embedding_model": settings.embedding_model,
        "embedding_device": settings.embedding_device,
        "embedding_dim": embedder.dim,
        "article_count": len(articles),
        "elapsed_seconds": round(elapsed, 3),
        "output": str(settings.embedding_cache),
    }
    meta_path = settings.embedding_cache.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
