"""검색 전략 비교: vector vs hybrid vs graph. 사전 조건: make up && make index"""
import json
from pathlib import Path

from korean_maritime_law_rag.bootstrap import build_retriever
from korean_maritime_law_rag.evaluation.harness import load_gold, run_eval, to_markdown


def main() -> None:
    retriever = build_retriever()
    gold = load_gold(Path("tests/qa_pairs.yaml"))
    report = run_eval(retriever, gold, strategies=["vector", "hybrid", "graph"], top_k=10)

    out = Path("reports")
    out.mkdir(exist_ok=True)
    (out / "retrieval_eval.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = "# 검색 전략 비교\n\n" + to_markdown(report) + "\n"
    (out / "ablation.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
