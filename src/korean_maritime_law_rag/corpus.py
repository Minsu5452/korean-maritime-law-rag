import json
from datetime import date
from pathlib import Path

from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.parsing.article_parser import parse_law


def filter_as_of(articles: list[Article], as_of: str | None = None) -> list[Article]:
    """as_of(YYYYMMDD) 시점에 시행 중인 조문만 남긴다(기본=오늘 기준 현행).

    enforce_date가 as_of보다 늦은(아직 시행 전) 조문은 제외한다. enforce_date가 없는
    조문은 시점 정보가 없으므로 항상 포함한다(보수적).
    """
    cutoff = as_of or date.today().strftime("%Y%m%d")
    return [a for a in articles if a.enforce_date is None or a.enforce_date <= cutoff]


def link_parents(articles: list[Article]) -> list[Article]:
    """시행령/시행규칙 조문에 상위 법률 law_id(parent_law_id)를 채운다.

    법령명에서 ' 시행령'/' 시행규칙' 접미사를 떼어 같은 이름의 법률을 찾는다.
    대응되는 법률이 코퍼스에 없으면 parent_law_id는 None으로 둔다.
    """
    law_id_by_name = {a.law_name: a.law_id for a in articles if a.law_type == "법률"}
    for a in articles:
        if a.law_type in ("시행령", "시행규칙") and a.parent_law_id is None:
            parent_name = a.law_name.removesuffix(" 시행령").removesuffix(" 시행규칙")
            a.parent_law_id = law_id_by_name.get(parent_name)
    return articles


def load_corpus(cache_dir: Path) -> list[Article]:
    articles: list[Article] = []
    for path in sorted(cache_dir.glob("*.json")):
        articles.extend(parse_law(json.loads(path.read_text(encoding="utf-8"))))
    return link_parents(articles)
