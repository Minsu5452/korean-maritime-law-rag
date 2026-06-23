from typing import Any

from korean_maritime_law_rag.models import Article, LawType
from korean_maritime_law_rag.parsing.crossref import extract_cross_refs


def _law_type(info: dict) -> LawType:
    """법종구분(content)으로 법령 종류를 정규화한다. 없으면 법령명 접미사로 추론한다."""
    kind = (info.get("법종구분") or {}).get("content", "") or ""
    if "대통령령" in kind:
        return "시행령"
    if "총리령" in kind or "부령" in kind:
        return "시행규칙"
    if "법률" in kind:
        return "법률"
    if kind:
        return "기타"
    name = (info.get("법령명_한글") or "").strip()
    if name.endswith("시행령"):
        return "시행령"
    if name.endswith("시행규칙"):
        return "시행규칙"
    return "법률"


def _as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _flatten_text(value: Any) -> str:
    """문자열, 리스트, 리스트-of-리스트 등 다양한 형태로 오는 법령 텍스트를 단일 문자열로 변환한다.

    법령정보 API 일부 법령(예: 어선법, 항만법)에서 호내용/목내용이
    [[번호+텍스트, 부연설명, ...]] 형태의 list-of-list로 올 수 있다.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    # 리스트(중첩 가능): 재귀로 평탄화하고 줄바꿈으로 잇는다.
    parts: list[str] = []
    for item in value:
        parts.append(_flatten_text(item))
    return "\n".join(p for p in parts if p)


def _clause_text(clause: dict) -> str:
    parts = [_flatten_text(clause.get("항내용", ""))]
    for ho in _as_list(clause.get("호")):
        parts.append(_flatten_text(ho.get("호내용", "")))
        for mok in _as_list(ho.get("목")):
            parts.append(_flatten_text(mok.get("목내용", "")))
    return "\n".join(p for p in parts if p)


def parse_law(raw: dict) -> list[Article]:
    law = raw["법령"]
    info = law["기본정보"]
    law_id = str(info["법령ID"])
    law_name = info["법령명_한글"].strip()
    law_type = _law_type(info)
    law_enforce = (info.get("시행일자") or "").strip() or None
    promulgation = (info.get("공포일자") or "").strip() or None

    articles: list[Article] = []
    for unit in _as_list(law.get("조문", {}).get("조문단위")):
        if unit.get("조문여부") != "조문":
            continue
        no = f"제{unit['조문번호']}조"
        if unit.get("조문가지번호"):
            no += f"의{unit['조문가지번호']}"
        body_parts = [_flatten_text(unit.get("조문내용", ""))]
        body_parts += [_clause_text(c) for c in _as_list(unit.get("항"))]
        body_text = "\n".join(p for p in body_parts if p).strip()
        articles.append(Article(
            law_id=law_id,
            law_name=law_name,
            law_type=law_type,
            article_no=no,
            title=(unit.get("조문제목") or "").strip(),
            text=body_text,
            enforce_date=(unit.get("조문시행일자") or "").strip() or law_enforce,
            promulgation_date=promulgation,
            cross_refs=extract_cross_refs(body_text),
        ))
    articles.extend(_parse_byeolpyo(law, law_id, law_name, law_type, law_enforce, promulgation))
    return articles


def _parse_byeolpyo(
    law: dict,
    law_id: str,
    law_name: str,
    law_type: LawType,
    enforce: str | None,
    promulgation: str | None,
) -> list[Article]:
    """별표/서식 단위를 Article(unit_kind='별표')로 파싱한다. 일부 법령은 별표내용이
    파일 링크뿐이라 본문이 비는데, 그 경우 제목을 본문으로 사용한다."""
    out: list[Article] = []
    for unit in _as_list(law.get("별표", {}).get("별표단위")):
        num_raw = str(unit.get("별표번호", "")).strip()
        if not num_raw:
            continue
        num = str(int(num_raw)) if num_raw.isdigit() else num_raw  # "0001"→"1"
        kind = (unit.get("별표구분") or "별표").strip()  # 별표/별지/서식 — 시리즈 구분(충돌 방지)
        no = f"{kind}{num}"
        branch = str(unit.get("별표가지번호", "")).strip()
        if branch and not (branch.isdigit() and int(branch) == 0):  # "00"은 가지 없음
            no += f"의{str(int(branch)) if branch.isdigit() else branch}"
        title = (unit.get("별표제목") or "").strip()
        body = _flatten_text(unit.get("별표내용")).strip()
        text = body or title
        if not text:
            continue
        out.append(Article(
            law_id=law_id,
            law_name=law_name,
            law_type=law_type,
            article_no=no,
            title=title,
            text=text,
            unit_kind="별표",
            enforce_date=enforce,
            promulgation_date=promulgation,
            cross_refs=extract_cross_refs(text),
        ))
    return out
