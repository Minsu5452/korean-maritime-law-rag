from pathlib import Path

import numpy as np
from pydantic import BaseModel

from korean_maritime_law_rag.models import Article


class EmbeddingCache(BaseModel):
    doc_ids: list[str]
    vectors: list[list[float]]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            doc_ids=np.array(self.doc_ids, dtype=object),
            vectors=np.array(self.vectors, dtype=np.float32),
        )

    def vectors_for_articles(self, articles: list[Article]) -> list[list[float]]:
        by_doc_id = {doc_id: vector for doc_id, vector in zip(self.doc_ids, self.vectors)}
        missing = [article.doc_id for article in articles if article.doc_id not in by_doc_id]
        if missing:
            sample = ", ".join(missing[:5])
            raise ValueError(f"임베딩 캐시에 없는 문서 {len(missing)}개: {sample}")
        return [by_doc_id[article.doc_id] for article in articles]


def load_embedding_cache(path: Path) -> EmbeddingCache:
    data = np.load(path, allow_pickle=True)
    return EmbeddingCache(
        doc_ids=[str(doc_id) for doc_id in data["doc_ids"].tolist()],
        vectors=data["vectors"].astype(np.float32).tolist(),
    )
