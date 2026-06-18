from typing import Literal

from pydantic import BaseModel, Field, computed_field


class CrossRef(BaseModel):
    ref_type: Literal["internal", "external"]
    target_law: str | None = None       # external일 때 법령명
    target_article: str                  # "제15조", "제15조의2"
    target_clause: str | None = None     # "제2항"
    rel: Literal["cite", "apply"] = "cite"  # apply = 준용


LawType = Literal["법률", "시행령", "시행규칙", "행정규칙", "기타"]
UnitKind = Literal["조문", "별표"]


class Article(BaseModel):
    law_id: str
    law_name: str
    law_type: LawType = "법률"            # 법령 종류 (법종구분 기반)
    parent_law_id: str | None = None     # 시행령/규칙이 위임받은 상위 법률의 law_id
    article_no: str                      # "제8조", "제8조의2", "별표1"
    title: str = ""
    text: str
    unit_kind: UnitKind = "조문"          # 조문 vs 별표
    enforce_date: str | None = None      # 시행일 YYYYMMDD (조문 우선, 없으면 법령)
    promulgation_date: str | None = None  # 공포일 YYYYMMDD
    cross_refs: list[CrossRef] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def doc_id(self) -> str:
        return f"{self.law_id}::{self.article_no}"


class SearchResult(BaseModel):
    doc_id: str
    score: float
    law_name: str = ""
    article_no: str = ""
    snippet: str = ""
