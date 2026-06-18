from korean_maritime_law_rag.parsing.crossref import extract_cross_refs, extract_parent_refs


def test_internal_article_with_clause():
    refs = extract_cross_refs("제15조제2항에 따라 처분할 수 있다.")
    assert len(refs) == 1
    r = refs[0]
    assert (r.ref_type, r.target_article, r.target_clause, r.rel) == ("internal", "제15조", "제2항", "cite")


def test_external_law_reference():
    refs = extract_cross_refs("「선박안전법」 제8조에 따른 검사를 받아야 한다.")
    assert len(refs) == 1
    assert refs[0].ref_type == "external"
    assert refs[0].target_law == "선박안전법"
    assert refs[0].target_article == "제8조"


def test_apply_relation_for_junyong():
    refs = extract_cross_refs("이 경우 제5조를 준용한다.")
    assert refs[0].rel == "apply"


def test_article_with_branch_number():
    refs = extract_cross_refs("제3조의2에 따라 지정한다.")
    assert refs[0].target_article == "제3조의2"


def test_clause_only_reference_is_skipped():
    # 같은 조 안의 "제1항" 참조는 엣지를 만들지 않는다
    assert extract_cross_refs("제1항에 따른 조치를 한다.") == []


def test_no_reference():
    assert extract_cross_refs("해양수산부장관은 기본계획을 수립한다.") == []


def test_external_not_double_counted_as_internal():
    refs = extract_cross_refs("「해양환경관리법」 제2조에 따른 오염물질을 말한다.")
    assert len(refs) == 1
    assert refs[0].ref_type == "external"


def test_multiple_references():
    refs = extract_cross_refs("제10조 및 「항만법」 제2조제1항에 따른다.")
    kinds = {(r.ref_type, r.target_article) for r in refs}
    assert ("internal", "제10조") in kinds
    assert ("external", "제2조") in kinds


def test_external_with_abbreviation_parenthetical():
    refs = extract_cross_refs(
        '「선박의 입항 및 출항 등에 관한 법률」(이하 "선박입출항법"이라 한다) 제2조에 따른다.'
    )
    assert len(refs) == 1
    assert refs[0].ref_type == "external"
    assert refs[0].target_law == "선박의 입항 및 출항 등에 관한 법률"
    assert refs[0].target_article == "제2조"


def test_internal_not_misclassified_after_external_law_mention():
    # 「법」 뒤에 일반 문장이 이어지다 나오는 조문 번호는 internal 유지
    refs = extract_cross_refs("「선박안전법」에 따른 처분 결과는 제5조에 따라 보고한다.")
    kinds = {(r.ref_type, r.target_article) for r in refs}
    assert ("internal", "제5조") in kinds
    assert ("external", "제5조") not in kinds


def test_extract_parent_refs_matches_standalone_법():
    # 시행령 본문의 '법 제5조' 약식 상위법 참조
    refs = extract_parent_refs("법 제5조제2항에 따른 세부기준은 이 영에서 정한다")
    assert "제5조" in refs


def test_extract_parent_refs_handles_branch_and_dedup():
    refs = extract_parent_refs("법 제5조의2 및 법 제5조의2에 따라")
    assert refs == ["제5조의2"]  # 가지번호 보존 + 중복 제거


def test_extract_parent_refs_ignores_law_name_suffix():
    # 명명참조(괄호 유무 무관)는 약식 상위법 참조가 아니다 — '...법' 접미사 제외
    assert extract_parent_refs("「선박안전법」 제5조에 따른다") == []
    assert extract_parent_refs("선박안전법 제5조에 따른다") == []
