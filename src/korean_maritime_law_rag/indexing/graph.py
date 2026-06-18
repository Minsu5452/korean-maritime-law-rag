import logging

from neo4j import Driver

from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.parsing.crossref import extract_parent_refs

logger = logging.getLogger(__name__)

REL_TYPES = ("CITES", "APPLIES", "IMPLEMENTS")


def resolve_citation_edges(articles: list[Article]) -> tuple[list[dict], int]:
    """cross_refs를 코퍼스 내 (src,dst,rel) 엣지로 해소. 코퍼스 밖 참조는 unresolved로 카운트.

    - 인용/준용 → CITES / APPLIES
    - 시행령·시행규칙 조문의 '법 제N조' 약식 참조 → 상위 법률 조문으로 IMPLEMENTS

    GraphStore와 골드셋 구조 검증이 같은 해소 로직을 사용한다.
    반환: (고유 엣지 목록, 미해결 외부참조 수).
    """
    law_by_name = {a.law_name: a.law_id for a in articles}
    doc_ids = {a.doc_id for a in articles}
    edges, unresolved = [], 0
    for a in articles:
        for ref in a.cross_refs:
            if ref.ref_type == "internal":
                target_law_id = a.law_id
            elif ref.target_law in law_by_name:
                target_law_id = law_by_name[ref.target_law]
            else:
                unresolved += 1  # 코퍼스 밖 법령 참조
                continue
            target = f"{target_law_id}::{ref.target_article}"
            if target in doc_ids and target != a.doc_id:
                rel_type = "CITES" if ref.rel == "cite" else "APPLIES"
                edges.append({"src": a.doc_id, "dst": target, "rel": rel_type})
        # 위임 엣지: 하위법령 조문이 상위 법률 조문을 약식('법 제N조')으로 가리킬 때
        if a.law_type in ("시행령", "시행규칙") and a.parent_law_id:
            for art_no in extract_parent_refs(a.text):
                target = f"{a.parent_law_id}::{art_no}"
                if target in doc_ids and target != a.doc_id:
                    edges.append({"src": a.doc_id, "dst": target, "rel": "IMPLEMENTS"})
    unique = {(e["src"], e["dst"], e["rel"]) for e in edges}
    return [{"src": s, "dst": d, "rel": r} for s, d, r in unique], unresolved


class GraphStore:
    """법령 지식그래프. (:Law)-[:HAS_ARTICLE]->(:Article), (:Article)-[:CITES|APPLIES]->(:Article)"""

    _NODE_FIELDS = frozenset({
        "law_id", "law_name", "doc_id", "article_no", "title",
        "law_type", "unit_kind", "enforce_date", "parent_law_id",
    })
    _MERGE_NODES = (
        "UNWIND $rows AS r "
        "MERGE (l:Law {law_id: r.law_id}) SET l.name = r.law_name, l.law_type = r.law_type "
        "MERGE (a:Article {doc_id: r.doc_id}) "
        "SET a.law_id = r.law_id, a.article_no = r.article_no, a.title = r.title, "
        "a.law_type = r.law_type, a.unit_kind = r.unit_kind, "
        "a.enforce_date = r.enforce_date, a.parent_law_id = r.parent_law_id "
        "MERGE (l)-[:HAS_ARTICLE]->(a)"
    )

    def __init__(self, driver: Driver):
        self.driver = driver

    def _write(self, session, articles: list[Article], edges: list[dict]) -> None:
        """노드·엣지를 MERGE로 멱등하게 기록한다(전역 삭제 없음)."""
        session.run("CREATE CONSTRAINT article_id IF NOT EXISTS "
                    "FOR (a:Article) REQUIRE a.doc_id IS UNIQUE")
        session.run(self._MERGE_NODES,
                    rows=[a.model_dump(include=set(self._NODE_FIELDS)) for a in articles])
        for rel in REL_TYPES:
            session.run(
                f"UNWIND $rows AS r MATCH (s:Article {{doc_id: r.src}}) "
                f"MATCH (d:Article {{doc_id: r.dst}}) MERGE (s)-[:{rel}]->(d)",
                rows=[e for e in edges if e["rel"] == rel],
            )

    def build(self, articles: list[Article]) -> dict:
        """전체 재구축 — 기존 노드를 모두 지우고 새로 만든다(초기 구축용)."""
        edges, unresolved = resolve_citation_edges(articles)
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")
            self._write(s, articles, edges)
        logger.info("그래프 구축: %d 조문, %d 엣지, 미해결 외부참조 %d", len(articles), len(edges), unresolved)
        return {"articles": len(articles), "edges": len(edges), "unresolved": unresolved}

    def upsert_articles(self, articles: list[Article], edges: list[dict] | None = None) -> dict:
        """증분 업서트(멱등) — 전역 삭제 없이 노드·엣지를 MERGE한다.

        교차법령 엣지까지 정확히 반영하려면 edges에 전체 코퍼스 기준 엣지를 넘긴다.
        생략하면 articles 부분집합 안에서만 엣지를 해소한다.
        """
        if edges is None:
            edges, _ = resolve_citation_edges(articles)
        with self.driver.session() as s:
            self._write(s, articles, edges)
        return self.stats()

    def delete_law(self, law_id: str) -> None:
        """한 법령의 Law·Article 노드와 연결 관계를 제거한다(개정 재동기화용)."""
        with self.driver.session() as s:
            s.run(
                "MATCH (a:Article {law_id: $lid}) DETACH DELETE a", lid=law_id
            )
            s.run("MATCH (l:Law {law_id: $lid}) DETACH DELETE l", lid=law_id)

    def stats(self) -> dict:
        with self.driver.session() as s:
            arts = s.run("MATCH (a:Article) RETURN count(a) AS c").single()
            edges = s.run("MATCH (:Article)-[r:CITES|APPLIES|IMPLEMENTS]->(:Article) "
                          "RETURN count(r) AS c").single()
        return {"articles": arts["c"] if arts else 0, "edges": edges["c"] if edges else 0}

    def expand(self, seed_doc_ids: list[str], hops: int = 2) -> list[tuple[str, str, int]]:
        query = (
            "UNWIND $seeds AS sid MATCH (a:Article {doc_id: sid}) "
            f"MATCH p = (a)-[:CITES|APPLIES|IMPLEMENTS*1..{int(hops)}]-(b:Article) "
            "WHERE b.doc_id <> sid "
            "RETURN sid AS seed, b.doc_id AS doc_id, min(length(p)) AS hops"
        )
        with self.driver.session() as s:
            return [(r["seed"], r["doc_id"], r["hops"]) for r in s.run(query, seeds=seed_doc_ids)]

    def find_article(self, law_name: str, article_no: str) -> str | None:
        with self.driver.session() as s:
            rec = s.run(
                "MATCH (l:Law {name: $name})-[:HAS_ARTICLE]->(a:Article {article_no: $no}) "
                "RETURN a.doc_id AS doc_id",
                name=law_name, no=article_no,
            ).single()
        return rec["doc_id"] if rec else None
