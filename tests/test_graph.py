import pytest
from neo4j import GraphDatabase

from korean_maritime_law_rag.indexing.graph import GraphStore

pytestmark = pytest.mark.integration


@pytest.fixture()
def store(small_corpus):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "marinerag"))
    s = GraphStore(driver)
    s.build(small_corpus)
    yield s
    driver.close()


def test_build_creates_edges_and_resolves_external(store):
    stats = store.stats()
    assert stats["articles"] == 5
    assert stats["edges"] >= 3  # 제8조→제5조, 제98조→제5조, 항만법제2조→선박법제5조(외부)


def test_implements_edge_links_decree_to_parent_statute(store):
    # 시행령 제3조의 '법 제5조' 약식 참조 → IMPLEMENTS 엣지로 상위 법률 제5조와 연결
    expanded = {doc_id for _, doc_id, _ in store.expand(["300::제3조"], hops=1)}
    assert "100::제5조" in expanded


def test_expand_finds_citing_articles_reverse_direction(store):
    # 제5조에서 출발하면 제5조를 인용하는 벌칙(제98조)이 1홉으로 나와야 한다
    expanded = store.expand(["100::제5조"], hops=1)
    found = {doc_id for _, doc_id, _ in expanded}
    assert "100::제98조" in found
    assert "100::제8조" in found


def test_expand_reports_hop_distance(store):
    expanded = {doc_id: h for _, doc_id, h in store.expand(["200::제2조"], hops=2)}
    assert expanded["100::제5조"] == 1   # 직접 준용
    assert expanded["100::제98조"] == 2  # 제5조 거쳐 2홉


def test_find_article_by_law_name(store):
    assert store.find_article("테스트선박법", "제5조") == "100::제5조"
    assert store.find_article("없는법", "제1조") is None


def test_upsert_articles_idempotent_no_dupes(store, small_corpus):
    # 같은 코퍼스를 재업서트해도 노드·엣지 수가 늘지 않는다(멱등, 전역삭제 없음)
    before = store.stats()
    store.upsert_articles(small_corpus)
    after = store.stats()
    assert after["articles"] == before["articles"]
    assert after["edges"] == before["edges"]


def test_delete_law_removes_only_that_law(store):
    store.delete_law("300")  # 시행령만 제거
    assert store.find_article("테스트선박법 시행령", "제3조") is None
    assert store.find_article("테스트선박법", "제5조") == "100::제5조"


def test_build_count_matches_graph_after_duplicate_refs(store, small_corpus):
    # 같은 참조가 중복 추출돼도 반환 카운트는 그래프 실제 엣지 수와 일치한다
    arts = [a.model_copy(deep=True) for a in small_corpus]
    arts[1].cross_refs = arts[1].cross_refs * 2  # 제8조→제5조 참조를 인위적으로 중복
    stats = store.build(arts)
    assert stats["edges"] == store.stats()["edges"]
