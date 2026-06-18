"""사용: uv run python scripts/validate_gold.py"""
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.evaluation.harness import load_gold, validate_gold


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    corpus_ids = {a.doc_id for a in load_corpus(s.cache_dir)}
    items = load_gold(Path("tests/qa_pairs.yaml"))
    errors = validate_gold(items, corpus_ids)
    if errors:
        raise SystemExit("\n".join(["gold set 검증 실패:"] + errors))
    by_type: dict = {}
    for g in items:
        by_type[g.type] = by_type.get(g.type, 0) + 1
    print(f"OK: {len(items)}문항 {by_type}")


if __name__ == "__main__":
    main()
