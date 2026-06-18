import pickle
from pathlib import Path

from neo4j import GraphDatabase

from korean_maritime_law_rag.collectors.law_api import LawApiClient
from korean_maritime_law_rag.config import Settings, load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.indexing.embedder import Embedder
from korean_maritime_law_rag.indexing.embedder_factory import make_embedder
from korean_maritime_law_rag.indexing.graph import GraphStore
from korean_maritime_law_rag.indexing.vector import VectorIndex, make_qdrant_client
from korean_maritime_law_rag.retrieval.live import LiveLawFallback
from korean_maritime_law_rag.retrieval.reranker import CrossEncoderReranker, NoopReranker
from korean_maritime_law_rag.retrieval.retriever import Retriever


def build_embedder(settings: Settings) -> Embedder:
    """설정의 embedding_model에 맞는 임베더를 만든다(KURE·BGE-M3·e5·OpenAI)."""
    return make_embedder(settings.embedding_model, device=settings.embedding_device)


def build_live_fallback(settings: Settings) -> LiveLawFallback | None:
    """설정에서 실시간 법령 조회가 켜져 있고 OC 키가 있으면 조회기를 만든다."""
    if not (settings.enable_law_api_fallback and settings.law_oc):
        return None
    return LiveLawFallback(LawApiClient(oc=settings.law_oc))


def build_retriever(settings: Settings | None = None) -> Retriever:
    s = settings or load_settings(Path("configs/demo.yaml"))
    articles = load_corpus(s.cache_dir)
    bm25 = pickle.loads(s.bm25_path.read_bytes())
    vector = VectorIndex(build_embedder(s), make_qdrant_client(s.qdrant_url))
    graph = GraphStore(GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password)))
    reranker = (CrossEncoderReranker(s.reranker_model, device=s.reranker_device)
                if s.rerank else NoopReranker())
    return Retriever(bm25=bm25, vector=vector, graph=graph, articles=articles,
                     reranker=reranker, rrf_k=s.rrf_k, graph_hops=s.graph_hops)
