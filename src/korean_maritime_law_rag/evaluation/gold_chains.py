"""그래프 구조에서 멀티홉 정답 체인 후보를 추출한다(구조만, LLM 없음).

골드셋 작성의 토대: 추출된 (anchor, gold) 쌍에서 사람이 자연스러운 질문을 직접 쓴다.
그래프 경로 자체를 질문으로 자동생성하지 않는다(순환·편향 방지)."""
from dataclasses import dataclass

from korean_maritime_law_rag.models import Article

_PENALTY_TITLE = ("벌칙", "과태료")
_PENALTY_TEXT = ("징역", "벌금", "과태료", "처한다", "부과한다")
_DELEGATION = ("대통령령으로 정", "총리령으로 정", "부령으로 정", "령으로 정한다")


@dataclass
class GoldChainCandidate:
    kind: str        # "penalty" | "delegation"
    anchor: str      # 질문을 출제할 조문 doc_id (의무/위임 조문)
    gold: list[str]  # 정답 조문 doc_id(들)
    hops: int


def _is_penalty(a: Article) -> bool:
    return any(k in a.title for k in _PENALTY_TITLE) or any(k in a.text for k in _PENALTY_TEXT)


def _has_delegation(a: Article) -> bool:
    return any(k in a.text for k in _DELEGATION)


def extract_chains(articles: list[Article], edges: list[dict]) -> list[GoldChainCandidate]:
    by_id = {a.doc_id: a for a in articles}
    out: list[GoldChainCandidate] = []
    seen: set[tuple] = set()

    def add(c: GoldChainCandidate) -> None:
        key = (c.kind, c.anchor, tuple(c.gold))
        if key not in seen:
            seen.add(key)
            out.append(c)

    for e in edges:
        src, dst, rel = by_id.get(e["src"]), by_id.get(e["dst"]), e["rel"]
        if src is None or dst is None:
            continue
        # 벌칙 체인: 벌칙조문(src)이 의무조문(dst)을 인용 → 의무에서 출제, 정답=벌칙
        if rel in ("CITES", "APPLIES") and _is_penalty(src) and not _is_penalty(dst):
            add(GoldChainCandidate("penalty", anchor=dst.doc_id, gold=[src.doc_id], hops=1))
        # 위임 체인: 시행령(src)이 법 위임조문(dst)을 구현 → 위임조문에서 출제, 정답=시행령
        if rel == "IMPLEMENTS" and _has_delegation(dst):
            add(GoldChainCandidate("delegation", anchor=dst.doc_id, gold=[src.doc_id], hops=1))
    return out
