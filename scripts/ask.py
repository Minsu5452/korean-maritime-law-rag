"""사용: OPENAI_API_KEY=<키> uv run python scripts/ask.py "질문" [--top-k 5]
사전 조건: make up && make index (v1 인덱스 필요)"""
import argparse
from pathlib import Path

from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.bootstrap import build_live_fallback, build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.llm import get_chat_model
from korean_maritime_law_rag.observability import build_langfuse_callbacks


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()

    s = load_settings(Path("configs/demo.yaml"))
    agent = Agent(build_retriever(s), get_chat_model(s), top_k=args.top_k,
                  live_fallback=build_live_fallback(s),
                  callbacks=build_langfuse_callbacks(s))
    resp = agent.answer(args.query)

    flags = (
        f"[유형] {resp.query_type}  [전략] {resp.strategy}  [거절] {resp.refused}  "
        f"[검색시도] {resp.retrieval_attempts}  [생성시도] {resp.generation_attempts}"
    )
    if resp.low_confidence:
        flags += "  [저신뢰: 유효 인용 없음]"
    print(flags)
    if resp.rewritten_query:
        print(f"[재작성 검색어] {resp.rewritten_query}")
    if resp.evidence_reason:
        print(f"[근거 평가] {resp.evidence_reason}")
    print(f"\n{resp.answer}\n")
    if resp.citations:
        print("근거 조문:")
        for c in resp.citations:
            print(f"  - {c}")


if __name__ == "__main__":
    main()
