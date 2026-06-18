"""골드 체인 추출기: 그래프에서 멀티홉 정답 후보를 뽑는다(LLM 없음)."""
from korean_maritime_law_rag.evaluation.gold_chains import extract_chains
from korean_maritime_law_rag.models import Article


def _corpus() -> list[Article]:
    return [
        Article(law_id="100", law_name="선박안전법", law_type="법률", article_no="제5조",
                title="건조검사", text="선박을 건조하려는 자는 건조검사를 받아야 한다."),
        Article(law_id="100", law_name="선박안전법", law_type="법률", article_no="제83조",
                title="벌칙", text="제5조를 위반한 자는 1년 이하의 징역에 처한다."),
        Article(law_id="100", law_name="선박안전법", law_type="법률", article_no="제8조",
                title="검사 기준", text="검사의 세부기준은 대통령령으로 정한다."),
        Article(law_id="200", law_name="선박안전법 시행령", law_type="시행령",
                parent_law_id="100", article_no="제3조", title="검사 세부기준",
                text="법 제8조에 따른 검사의 세부기준은 다음과 같다."),
    ]


def _edges() -> list[dict]:
    return [
        {"src": "100::제83조", "dst": "100::제5조", "rel": "CITES"},     # 벌칙→의무
        {"src": "200::제3조", "dst": "100::제8조", "rel": "IMPLEMENTS"},  # 시행령→법(위임)
    ]


def test_extract_penalty_chain_anchors_on_duty_article():
    chains = extract_chains(_corpus(), _edges())
    penalty = [c for c in chains if c.kind == "penalty"]
    assert len(penalty) == 1
    assert penalty[0].anchor == "100::제5조"   # 의무 조문에서 질문 출제
    assert penalty[0].gold == ["100::제83조"]  # 정답은 벌칙 조문


def test_extract_delegation_chain_from_implements_edge():
    chains = extract_chains(_corpus(), _edges())
    deleg = [c for c in chains if c.kind == "delegation"]
    assert len(deleg) == 1
    assert deleg[0].anchor == "100::제8조"     # 위임 조문(대통령령으로 정한다)
    assert deleg[0].gold == ["200::제3조"]     # 정답은 시행령 상세조문


def test_extract_chains_skips_penalty_to_penalty_edges():
    arts = [
        Article(law_id="100", law_name="L", article_no="제83조", title="벌칙",
                text="제84조를 위반하면 처벌한다."),
        Article(law_id="100", law_name="L", article_no="제84조", title="벌칙",
                text="징역에 처한다."),
    ]
    edges = [{"src": "100::제83조", "dst": "100::제84조", "rel": "CITES"}]
    assert [c for c in extract_chains(arts, edges) if c.kind == "penalty"] == []
