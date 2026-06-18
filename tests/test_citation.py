from korean_maritime_law_rag.retrieval.citation import parse_citation


def test_parse_citation_with_law_name():
    assert parse_citation("「선박안전법」 제8조의 내용은?") == ("선박안전법", "제8조")


def test_parse_citation_without_brackets():
    assert parse_citation("선박안전법 제8조 알려줘") == ("선박안전법", "제8조")


def test_parse_citation_branch_number():
    assert parse_citation("항만법 제2조의3은?") == ("항만법", "제2조의3")


def test_no_citation_returns_none():
    assert parse_citation("선박 검사는 누가 하나요") is None
    assert parse_citation("제5조가 뭐죠") is None  # 법령명 없으면 모호 → None


def test_parse_citation_with_middle_dot():
    q = "수상에서의 수색ㆍ구조 등에 관한 법률 제17조 내용은?"
    assert parse_citation(q) == ("수상에서의 수색ㆍ구조 등에 관한 법률", "제17조")


def test_parse_citation_with_space_separated_beopryul():
    q = "해양사고의 조사 및 심판에 관한 법률 제8조 알려줘"
    assert parse_citation(q) == ("해양사고의 조사 및 심판에 관한 법률", "제8조")
