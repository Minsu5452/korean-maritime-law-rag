from pathlib import Path

from korean_maritime_law_rag.corpus import filter_as_of, link_parents, load_corpus
from korean_maritime_law_rag.models import Article


def _art(no: str, enforce: str | None) -> Article:
    return Article(law_id="1", law_name="선박안전법", article_no=no, text="t", enforce_date=enforce)

CACHE = Path("data/cache/raw")


def test_load_corpus_from_bundled_cache():
    articles = load_corpus(CACHE)
    assert len(articles) > 100
    assert len({a.doc_id for a in articles}) == len(articles)  # doc_id 유일


def test_link_parents_resolves_decree_to_statute():
    arts = [
        Article(law_id="100", law_name="선박안전법", law_type="법률", article_no="제5조", text="t"),
        Article(law_id="200", law_name="선박안전법 시행령", law_type="시행령",
                article_no="제3조", text="t"),
        Article(law_id="300", law_name="선박안전법 시행규칙", law_type="시행규칙",
                article_no="제2조", text="t"),
    ]
    link_parents(arts)
    assert arts[1].parent_law_id == "100"
    assert arts[2].parent_law_id == "100"
    assert arts[0].parent_law_id is None  # 법률 자신은 부모 없음


def test_link_parents_leaves_unmatched_as_none():
    arts = [
        Article(law_id="200", law_name="고아법 시행령", law_type="시행령",
                article_no="제1조", text="t"),
    ]
    link_parents(arts)
    assert arts[0].parent_law_id is None


def test_filter_as_of_excludes_not_yet_in_force():
    arts = [_art("제1조", "20200101"), _art("제2조", "20990101"), _art("제3조", None)]
    kept = {a.article_no for a in filter_as_of(arts, as_of="20250101")}
    assert kept == {"제1조", "제3조"}  # 미래 시행 제2조 제외, 날짜 없는 제3조는 포함


def test_filter_as_of_includes_exact_date_boundary():
    arts = [_art("제1조", "20250101")]
    assert len(filter_as_of(arts, as_of="20250101")) == 1  # 시행일 당일은 현행


def test_filter_as_of_defaults_to_today():
    arts = [_art("제1조", "20200101"), _art("제2조", "29990101")]
    kept = {a.article_no for a in filter_as_of(arts, as_of=None)}
    assert kept == {"제1조"}  # 기본 오늘 기준 → 먼 미래 제2조 제외
