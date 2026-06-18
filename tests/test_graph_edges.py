"""resolve_citation_edges 순수 단위테스트 (Neo4j 불필요)."""
from korean_maritime_law_rag.indexing.graph import resolve_citation_edges
from korean_maritime_law_rag.models import Article, CrossRef


def test_internal_citation_resolves_within_same_law():
    arts = [
        Article(law_id="100", law_name="선박안전법", article_no="제8조", text="제5조에 따라",
                cross_refs=[CrossRef(ref_type="internal", target_article="제5조")]),
        Article(law_id="100", law_name="선박안전법", article_no="제5조", text="..."),
    ]
    edges, _ = resolve_citation_edges(arts)
    assert {"src": "100::제8조", "dst": "100::제5조", "rel": "CITES"} in edges


def test_decree_implements_parent_law_article():
    arts = [
        Article(law_id="100", law_name="선박안전법", law_type="법률",
                article_no="제5조", text="제5조(건조검사) ..."),
        Article(law_id="200", law_name="선박안전법 시행령", law_type="시행령",
                parent_law_id="100", article_no="제3조",
                text="제3조 법 제5조에 따른 건조검사의 세부기준은 다음과 같다"),
    ]
    edges, _ = resolve_citation_edges(arts)
    assert {"src": "200::제3조", "dst": "100::제5조", "rel": "IMPLEMENTS"} in edges


def test_statute_self_reference_not_implements():
    arts = [
        Article(law_id="100", law_name="선박안전법", law_type="법률",
                article_no="제5조", text="이 법 제3조에 따라"),
        Article(law_id="100", law_name="선박안전법", law_type="법률",
                article_no="제3조", text="..."),
    ]
    edges, _ = resolve_citation_edges(arts)
    assert all(e["rel"] != "IMPLEMENTS" for e in edges)


def test_implements_skips_when_parent_article_missing():
    arts = [
        Article(law_id="200", law_name="선박안전법 시행령", law_type="시행령",
                parent_law_id="100", article_no="제3조", text="법 제999조에 따라"),
    ]
    edges, _ = resolve_citation_edges(arts)
    assert edges == []
