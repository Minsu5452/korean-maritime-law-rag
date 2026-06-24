"""검색 전략별 hit@1, Wilson CI, 멀티홉 McNemar 비교를 생성한다.

사전 조건: make up && make index. 출력: reports/significance.md
"""
from collections import Counter
from pathlib import Path

from korean_maritime_law_rag.agent.router import route
from korean_maritime_law_rag.bootstrap import build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.evaluation.harness import load_gold
from korean_maritime_law_rag.evaluation.stats import mcnemar_p, wilson


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    retriever = build_retriever(s)
    gold = load_gold(Path("tests/qa_pairs.yaml"))
    answerable = [g for g in gold if g.type != "unanswerable"]
    types = ("single", "definition", "multihop")

    def hit(g, strat: str) -> int:
        r = retriever.search(g.question, strat, top_k=s.top_k)
        return int(bool(r) and r[0].doc_id in set(g.gold))

    H = {st: {g.id: hit(g, st) for g in answerable} for st in ("vector", "hybrid", "graph")}
    oracle = {g.id: hit(g, route(g.type)) for g in answerable}

    counts = Counter(g.type for g in answerable)
    order = {"multihop": 0, "single": 1, "definition": 2}
    type_summary = ", ".join(f"{t} {c}" for t, c in sorted(counts.items(), key=lambda kv: order.get(kv[0], 9)))
    lines = ["# 검색 전략 통계 요약", "",
             "이 표는 `scripts/significance.py`로 생성한 마지막 저장 결과입니다. hit@1은 검색 인덱스 빌드에 따라",
             "문항 단위로 1건 정도 달라질 수 있어, 임베더 비교표(`reports/embedder_ablation.md`)와 정확히 맞추려면",
             "두 리포트를 같은 인덱스에서 함께 재생성해야 합니다(`make up && make index`).", "",
             f"정답 조문이 있는 질문은 n={len(answerable)}입니다({type_summary}).", "",
             "| 전략/라우팅 | 유형 | hit@1 | 95% Wilson CI |", "|---|---|---|---|"]

    def add_rows(name: str, hits: dict) -> None:
        groups = [("overall", answerable)] + [(t, [g for g in answerable if g.type == t]) for t in types]
        for label, subset in groups:
            k = sum(hits[g.id] for g in subset)
            n = len(subset)
            lo, hi = wilson(k, n)
            lines.append(f"| {name} | {label} | {k}/{n}={k / n:.3f} | [{lo:.3f}, {hi:.3f}] |")

    for st in ("vector", "hybrid", "graph"):
        add_rows(st, H[st])
    add_rows("oracle 라우팅", oracle)

    mh = [g for g in answerable if g.type == "multihop"]
    lines += ["", f"## 멀티홉(n={len(mh)}) McNemar 비교"]
    for name in ("vector", "hybrid"):
        b = sum(1 for g in mh if H["graph"][g.id] and not H[name][g.id])
        c = sum(1 for g in mh if H[name][g.id] and not H["graph"][g.id])
        sig = "p < 0.05" if mcnemar_p(b, c) < 0.05 else "p >= 0.05"
        lines.append(
            f"- graph vs {name}: graph만 맞춘 문항 b={b}, {name}만 맞춘 문항 c={c}, "
            f"p={mcnemar_p(b, c):.4f} ({sig})"
        )

    out = "\n".join(lines) + "\n"
    Path("reports").mkdir(exist_ok=True)
    Path("reports/significance.md").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
