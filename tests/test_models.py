from korean_maritime_law_rag.models import Article, CrossRef


def test_article_doc_id_format():
    a = Article(law_id="009682", law_name="선박안전법", article_no="제8조", text="본문")
    assert a.doc_id == "009682::제8조"


def test_crossref_defaults():
    r = CrossRef(ref_type="internal", target_article="제15조")
    assert r.rel == "cite"
    assert r.target_law is None


def test_article_cross_refs_uses_default_factory():
    field = Article.model_fields["cross_refs"]

    assert field.default_factory is list


def test_article_law_type_defaults_preserve_back_compat():
    a = Article(law_id="009682", law_name="선박안전법", article_no="제8조", text="본문")
    assert a.law_type == "법률"
    assert a.parent_law_id is None
    assert a.unit_kind == "조문"
    assert a.enforce_date is None
    assert a.promulgation_date is None


def test_article_accepts_subordinate_legislation_metadata():
    a = Article(
        law_id="009683",
        law_name="선박안전법 시행령",
        article_no="제3조",
        text="법 제5조에 따른 세부사항은 …",
        law_type="시행령",
        parent_law_id="009682",
        enforce_date="20260101",
        promulgation_date="20251201",
    )
    assert a.law_type == "시행령"
    assert a.parent_law_id == "009682"
    assert a.enforce_date == "20260101"
    assert a.promulgation_date == "20251201"


def test_article_byeolpyo_unit_kind_doc_id():
    a = Article(
        law_id="009683",
        law_name="선박안전법 시행규칙",
        article_no="별표1",
        text="과태료 부과기준 …",
        law_type="시행규칙",
        unit_kind="별표",
    )
    assert a.unit_kind == "별표"
    assert a.doc_id == "009683::별표1"
