"""확장된 인용·위임 그래프에서 멀티홉 정답 체인 후보를 구조적으로 추출한다(D1).

출력(reports/gold_chain_candidates.json)을 토대로 사람이 자연스러운 질문을 직접 쓴다.
그래프 경로를 질문으로 자동생성하지 않는다(순환·편향 방지).
사용: python scripts/extract_gold_chains.py
"""
import json
from collections import Counter
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import filter_as_of, load_corpus
from korean_maritime_law_rag.evaluation.gold_chains import extract_chains
from korean_maritime_law_rag.indexing.graph import resolve_citation_edges


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    articles = filter_as_of(load_corpus(s.cache_dir), s.as_of)
    edges, _ = resolve_citation_edges(articles)
    by_id = {a.doc_id: a for a in articles}
    chains = extract_chains(articles, edges)

    payload = []
    for c in chains:
        anchor, gold = by_id.get(c.anchor), [by_id[g] for g in c.gold if g in by_id]
        if anchor is None or not gold:
            continue
        payload.append({
            "kind": c.kind, "hops": c.hops,
            "anchor": c.anchor, "anchor_law": anchor.law_name,
            "anchor_title": anchor.title, "anchor_text": anchor.text[:400],
            "gold": c.gold,
            "gold_law": [g.law_name for g in gold],
            "gold_title": [g.title for g in gold],
            "gold_text": [g.text[:400] for g in gold],
        })

    Path("reports").mkdir(exist_ok=True)
    Path("reports/gold_chain_candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = Counter(c["kind"] for c in payload)
    print(f"체인 후보 {len(payload)}개 추출 → reports/gold_chain_candidates.json  {dict(counts)}")


if __name__ == "__main__":
    main()
