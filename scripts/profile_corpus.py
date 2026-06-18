"""코퍼스 범위와 citation graph 규모 리포트를 생성한다."""
import json
from collections import Counter
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.corpus import load_corpus
from korean_maritime_law_rag.indexing.graph import resolve_citation_edges


def main() -> None:
    settings = load_settings(Path("configs/demo.yaml"))
    articles = load_corpus(settings.cache_dir)
    edges, unresolved = resolve_citation_edges(articles)

    by_law = Counter(article.law_name for article in articles)
    by_rel = Counter(edge["rel"] for edge in edges)
    by_type = Counter(a.law_type for a in articles)
    by_unit = Counter(a.unit_kind for a in articles)
    stats = {
        "law_count": len(by_law),
        "article_count": len(articles),
        "edge_count": len(edges),
        "cites": by_rel.get("CITES", 0),
        "applies": by_rel.get("APPLIES", 0),
        "implements": by_rel.get("IMPLEMENTS", 0),
        "unresolved_external_refs": unresolved,
        "by_law_type": dict(by_type),
        "by_unit_kind": dict(by_unit),
        "laws": dict(sorted(by_law.items())),
    }

    out = Path("reports")
    out.mkdir(exist_ok=True)
    (out / "corpus_profile.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rows = "\n".join(f"| {name} | {count} |" for name, count in sorted(by_law.items()))
    type_rows = "\n".join(f"| {k} | {v} |" for k, v in sorted(by_type.items()))
    md = (
        f"# 코퍼스 프로파일\n\n"
        "## 요약\n\n"
        "| 지표 | 값 |\n"
        "|---|---:|\n"
        f"| 법령 문서 수 | {stats['law_count']} |\n"
        f"| 조문·별표 수 | {stats['article_count']} |\n"
        f"| 그래프 엣지 수 | {stats['edge_count']} |\n"
        f"| CITES 엣지 | {stats['cites']} |\n"
        f"| APPLIES(준용) 엣지 | {stats['applies']} |\n"
        f"| IMPLEMENTS(위임) 엣지 | {stats['implements']} |\n"
        f"| 미해결 외부 참조 | {stats['unresolved_external_refs']} |\n"
        f"| 별표 단위 | {by_unit.get('별표', 0)} |\n\n"
        "## 법령 종류별 단위 수\n\n"
        "| 종류 | 수 |\n|---|---:|\n"
        f"{type_rows}\n\n"
        "## 법령별 단위 수\n\n"
        "| 법령 | 단위 수 |\n"
        "|---|---:|\n"
        f"{rows}\n"
    )
    (out / "corpus_profile.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
