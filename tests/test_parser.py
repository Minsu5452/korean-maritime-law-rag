import json
from pathlib import Path

from korean_maritime_law_rag.parsing.article_parser import parse_law

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "lawservice_sample.json").read_text(encoding="utf-8")
)


def test_parse_law_returns_articles():
    articles = parse_law(FIXTURE)
    assert len(articles) > 0
    first = articles[0]
    assert first.article_no.startswith("제")
    assert first.text.strip()
    assert first.doc_id == f"{first.law_id}::{first.article_no}"


def test_parse_law_skips_non_article_units():
    # 조문여부 != "조문" (장 제목 등) 단위는 제외된다
    articles = parse_law(FIXTURE)
    assert all(a.article_no.endswith("조") or "의" in a.article_no for a in articles)


def test_parse_law_extracts_cross_refs():
    articles = parse_law(FIXTURE)
    total_refs = sum(len(a.cross_refs) for a in articles)
    assert total_refs > 0  # 실제 법령엔 교차참조가 반드시 존재


def test_parse_handles_single_clause_as_dict():
    # 항이 배열이 아니라 단일 객체로 오는 quirk
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "테스트법"},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "1", "조문제목": "목적",
            "조문내용": "제1조(목적) 이 법은 …",
            "항": {"항내용": "① 단일 항 내용"},
        }]},
    }}
    articles = parse_law(raw)
    assert "단일 항 내용" in articles[0].text


def test_parse_handles_호내용_list_of_list():
    """어선법(001483.json) quirk: 호내용이 [[번호+텍스트, 설명, ...]] 형태의 리스트-of-리스트로 올 때 파싱 가능해야 한다."""
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "어선법"},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "21", "조문제목": "검사",
            "조문내용": "",
            "항": [{
                "항번호": "①",
                "항내용": "① 어선의 소유자는 검사를 받아야 한다.",
                "호": [
                    {"호번호": "1.", "호내용": [["1.  정기검사", "    최초로 항행의 목적에 사용하는 때 행하는 정밀한 검사"]]},
                    {"호번호": "2.", "호내용": [["2.  중간검사", "    정기검사와 다음의 정기검사 사이에 행하는 간단한 검사"]]},
                ],
            }],
        }]},
    }}
    articles = parse_law(raw)
    assert len(articles) == 1
    assert "정기검사" in articles[0].text
    assert "중간검사" in articles[0].text


def test_parse_handles_조문내용_as_list():
    # 실데이터 quirk(시행규칙): 조문내용이 리스트로 올 때 join 에러 없이 파싱
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "선박안전법 시행규칙",
                  "법종구분": {"content": "해양수산부령"}},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "1", "조문제목": "목적",
            "조문내용": ["제1조(목적)", "이 규칙은 선박안전법에서 위임한 사항을 정한다."],
        }]},
    }}
    a = parse_law(raw)[0]
    assert "이 규칙은" in a.text


def test_parse_handles_항내용_as_list():
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "테스트규칙", "법종구분": {"content": "총리령"}},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "2", "조문제목": "정의", "조문내용": "제2조(정의)",
            "항": [{"항내용": ["① 다음과 같다.", "부연 설명"]}],
        }]},
    }}
    a = parse_law(raw)[0]
    assert "다음과 같다" in a.text


def test_parse_law_sets_law_type_법률_from_fixture():
    articles = parse_law(FIXTURE)
    assert all(a.law_type == "법률" for a in articles)


def test_parse_law_sets_enforce_date_from_조문시행일자():
    articles = parse_law(FIXTURE)
    first = articles[0]
    assert first.enforce_date == "20260201"
    assert first.promulgation_date == "20250131"


def test_parse_law_normalizes_대통령령_to_시행령():
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "선박안전법 시행령",
                  "법종구분": {"content": "대통령령"},
                  "시행일자": "20260101", "공포일자": "20251201"},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "3", "조문제목": "정의",
            "조문내용": "제3조(정의) 이 영에서 …",
        }]},
    }}
    a = parse_law(raw)[0]
    assert a.law_type == "시행령"
    assert a.enforce_date == "20260101"  # 조문시행일자 없으면 법령 시행일자로 폴백


def test_parse_law_normalizes_부령_to_시행규칙():
    raw = {"법령": {
        "기본정보": {"법령ID": "1", "법령명_한글": "선박안전법 시행규칙",
                  "법종구분": {"content": "해양수산부령"}},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "1", "조문제목": "목적",
            "조문내용": "제1조(목적) …",
        }]},
    }}
    assert parse_law(raw)[0].law_type == "시행규칙"


def test_parse_law_extracts_byeolpyo_units():
    raw = {"법령": {
        "기본정보": {"법령ID": "9", "법령명_한글": "선박안전법 시행규칙",
                  "법종구분": {"content": "해양수산부령"}},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "1", "조문제목": "목적", "조문내용": "제1조(목적) …",
        }]},
        "별표": {"별표단위": [
            {"별표번호": "1", "별표제목": "과태료의 부과기준",
             "별표내용": ["1. 일반기준", "2. 개별기준 …"]},
            {"별표번호": "2", "별표가지번호": "2", "별표제목": "수수료",
             "별표내용": "수수료 표"},
        ]},
    }}
    articles = parse_law(raw)
    byeolpyo = [a for a in articles if a.unit_kind == "별표"]
    assert len(byeolpyo) == 2
    assert byeolpyo[0].article_no == "별표1"
    assert byeolpyo[0].title == "과태료의 부과기준"
    assert "개별기준" in byeolpyo[0].text
    assert byeolpyo[1].article_no == "별표2의2"


def test_parse_byeolpyo_strips_zero_padding_and_zero_branch():
    # 실데이터: 별표번호 "0001", 별표가지번호 "00"(가지 없음) → "별표1"
    raw = {"법령": {
        "기본정보": {"법령ID": "9", "법령명_한글": "도선법 시행규칙", "법종구분": {"content": "해양수산부령"}},
        "별표": {"별표단위": [
            {"별표번호": "0001", "별표가지번호": "00", "별표구분": "별표",
             "별표제목": "신체검사 합격기준", "별표내용": "내용"},
        ]},
    }}
    a = [x for x in parse_law(raw) if x.unit_kind == "별표"][0]
    assert a.article_no == "별표1"


def test_parse_byeolpyo_disambiguates_series_by_gubun():
    # 별표 1과 별지 1은 별표번호가 같아도 별표구분으로 구분돼 doc_id 충돌이 없어야 한다
    raw = {"법령": {
        "기본정보": {"법령ID": "9", "법령명_한글": "도선법 시행규칙", "법종구분": {"content": "해양수산부령"}},
        "별표": {"별표단위": [
            {"별표번호": "0001", "별표가지번호": "00", "별표구분": "별표",
             "별표제목": "합격기준", "별표내용": "A"},
            {"별표번호": "0001", "별표가지번호": "00", "별표구분": "별지",
             "별표제목": "면허 신청서", "별표내용": "B"},
        ]},
    }}
    arts = [x for x in parse_law(raw) if x.unit_kind == "별표"]
    assert {a.article_no for a in arts} == {"별표1", "별지1"}


def test_parse_handles_목내용_list_of_list():
    """항만법(001737.json) quirk: 목내용이 [[목기호+텍스트, 부연텍스트, ...]] 형태의 리스트-of-리스트로 올 때 파싱 가능해야 한다."""
    raw = {"법령": {
        "기본정보": {"법령ID": "2", "법령명_한글": "항만법"},
        "조문": {"조문단위": [{
            "조문여부": "조문", "조문번호": "2", "조문제목": "정의",
            "조문내용": "",
            "항": [{
                "항번호": "①",
                "항내용": "① 이 법에서 사용하는 용어의 뜻은 다음과 같다.",
                "호": [{
                    "호번호": "1.",
                    "호내용": "1.  \"항만시설\"이란 다음 각 목의 어느 하나에 해당하는 시설을 말한다.",
                    "목": [
                        {"목기호": "가.", "목내용": [["가.  기본시설", "    1) 항로, 정박지 등 수역시설", "    2) 방파제 등 외곽시설"]]},
                        {"목기호": "나.", "목내용": "나.  단순 문자열 목"},
                    ],
                }],
            }],
        }]},
    }}
    articles = parse_law(raw)
    assert len(articles) == 1
    assert "기본시설" in articles[0].text
    assert "수역시설" in articles[0].text
    assert "단순 문자열 목" in articles[0].text
