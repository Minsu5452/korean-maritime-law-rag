"""사용: uv run python scripts/search.py "질문" [--strategy graph] [--top-k 5]"""
import argparse

from korean_maritime_law_rag.bootstrap import build_retriever


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--strategy", default="graph", choices=["vector", "hybrid", "graph"])
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()

    for i, r in enumerate(build_retriever().search(args.query, args.strategy, args.top_k), 1):
        print(f"{i}. [{r.score:.4f}] {r.law_name} {r.article_no} — {r.snippet[:80]}")


if __name__ == "__main__":
    main()
