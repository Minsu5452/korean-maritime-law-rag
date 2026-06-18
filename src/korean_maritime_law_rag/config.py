import os
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """프로젝트 전역 설정. 환경변수(MLR_*)가 yaml보다 우선한다."""

    law_oc: str = ""  # 국가법령정보 OC 키 — env MLR_LAW_OC로만 주입, 커밋 금지
    cache_dir: Path = Path("data/cache/raw")
    bm25_path: Path = Path("data/bm25.pkl")
    qdrant_url: str | None = None
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "marinerag"
    embedding_model: str = "nlpai-lab/KURE-v1"
    embedding_device: str = "cpu"  # cpu|mps|auto. 인덱싱은 cpu 권장(MPS OOM 이력), 평가는 mps로 가속
    embedding_cache: Path | None = Path("data/embeddings/kure-v1-articles.npz")
    rerank: bool = False
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "cpu"  # cpu|mps|cuda. 대형 cross-encoder라 기본 cpu(MPS OOM 회피)
    top_k: int = 10
    rrf_k: int = 60
    graph_hops: int = 1
    as_of: str | None = None  # YYYYMMDD 시점 현행 필터. None=오늘. 연혁 time-travel은 후순위
    enable_law_api_fallback: bool = False  # 로컬 미스 시 law.go.kr 실시간 조회(OC 키 필요)
    langfuse_enabled: bool = False  # 관측성. 키는 env MLR_LANGFUSE_*로 주입
    langfuse_host: str = "http://localhost:3000"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    llm_model: str = "openai:gpt-4o-mini"  # 에이전트(평가 대상). 키는 env OPENAI_API_KEY로만
    judge_model: str = "openai:gpt-4o"     # 근거성·RAGAS 평가 모델. 시스템 모델과 분리
    llm_temperature: float = 0.0
    llm_reasoning_effort: str = ""         # 지원 모델에서만 전달. 빈값=모델 기본

    model_config = SettingsConfigDict(env_prefix="MLR_")


def load_settings(path: Path | None) -> Settings:
    data: dict = {}
    if path is not None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    env_keys = {k.upper() for k in os.environ}
    data = {k: v for k, v in data.items() if f"MLR_{k.upper()}" not in env_keys}
    return Settings(**data)
