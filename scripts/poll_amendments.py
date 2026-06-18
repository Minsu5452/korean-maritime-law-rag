"""최근 개정된 법령을 감지해 바뀐 법령만 재수집하고(선택) 인덱스를 증분 동기화한다.

사용:
  MLR_LAW_OC=<키> python scripts/poll_amendments.py            # 변경 감지 + 재수집만
  MLR_LAW_OC=<키> python scripts/poll_amendments.py --reindex  # + Qdrant/Neo4j 증분 upsert

cron 등록 가능. 전체 삭제·재구축 없이 공포번호가 바뀐 법령만 처리한다.
"""
import argparse
import json
import logging
from pathlib import Path

import yaml

from korean_maritime_law_rag.collectors.law_api import (
    LawApiClient,
    LawNotCurrentError,
    is_amended,
    subordinate_names,
)
from korean_maritime_law_rag.config import load_settings

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)  # 요청 URL(OC 키 포함) 로그 노출 방지
logger = logging.getLogger("poll")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reindex", action="store_true", help="변경분을 Qdrant/Neo4j에 증분 반영")
    args = parser.parse_args()

    settings = load_settings(Path("configs/demo.yaml"))
    if not settings.law_oc:
        raise SystemExit("MLR_LAW_OC 환경변수에 OC 키를 설정하세요")

    base = yaml.safe_load(Path("configs/laws.yaml").read_text(encoding="utf-8"))["laws"]
    names: list[str] = []
    for law in base:
        names += [law, *subordinate_names(law)]

    client = LawApiClient(oc=settings.law_oc)
    changed_law_ids: list[str] = []
    for name in names:
        try:
            entry = client.search_law(name)
        except LawNotCurrentError:
            continue
        cache_path = settings.cache_dir / f"{entry['법령ID']}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if not is_amended(cached, entry):
                continue
            logger.info("개정 감지: %s", name)
        raw = client.fetch_law(entry["법령일련번호"])
        cache_path.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        changed_law_ids.append(str(entry["법령ID"]))

    if not changed_law_ids:
        print("변경된 법령 없음 — 인덱스 최신")
        return
    print(f"재수집 완료: {len(changed_law_ids)}개 법령 {changed_law_ids}")

    if args.reindex:
        _reindex(settings, changed_law_ids)


def _reindex(settings, changed_law_ids: list[str]) -> None:
    """변경된 법령만 Qdrant·Neo4j에서 삭제 후 재업서트(전체 코퍼스 기준 엣지 보존)."""
    from neo4j import GraphDatabase

    from korean_maritime_law_rag.bootstrap import build_embedder
    from korean_maritime_law_rag.corpus import load_corpus
    from korean_maritime_law_rag.indexing.graph import GraphStore, resolve_citation_edges
    from korean_maritime_law_rag.indexing.vector import VectorIndex, make_qdrant_client

    articles = load_corpus(settings.cache_dir)
    edges, _ = resolve_citation_edges(articles)
    changed = {lid for lid in changed_law_ids}
    changed_articles = [a for a in articles if a.law_id in changed]

    vindex = VectorIndex(build_embedder(settings), client=make_qdrant_client(settings.qdrant_url))
    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    gstore = GraphStore(driver)
    try:
        for lid in changed:
            vindex.delete_by_law(lid)
            gstore.delete_law(lid)
        vindex.upsert(changed_articles)
        gstore.upsert_articles(articles, edges=edges)  # 전체 엣지로 교차참조 보존
    finally:
        driver.close()
    print(f"증분 재색인 완료: {len(changed_articles)}개 조문")


if __name__ == "__main__":
    main()
