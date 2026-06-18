import pytest

from korean_maritime_law_rag.models import Article
from korean_maritime_law_rag.parsing.crossref import extract_cross_refs


def _article(law_id, law_name, no, title, text):
    return Article(law_id=law_id, law_name=law_name, article_no=no, title=title,
                   text=text, cross_refs=extract_cross_refs(text))


@pytest.fixture()
def small_corpus() -> list[Article]:
    return [
        _article("100", "테스트선박법", "제5조", "선박검사",
                 "선박소유자는 해양수산부장관의 검사를 받아야 한다."),
        _article("100", "테스트선박법", "제8조", "검사 기준",
                 "제5조에 따른 검사의 기준은 대통령령으로 정한다."),
        _article("100", "테스트선박법", "제98조", "벌칙",
                 "제5조를 위반하여 검사를 받지 아니한 자는 1년 이하의 징역에 처한다."),
        _article("200", "테스트항만법", "제2조", "정의",
                 "항만이란 선박의 출입 화물의 하역을 위한 시설을 말한다. "
                 "「테스트선박법」 제5조에 따른 검사를 준용한다."),
        Article(law_id="300", law_name="테스트선박법 시행령", law_type="시행령",
                parent_law_id="100", article_no="제3조", title="검사 기준",
                text="법 제5조에 따른 검사의 세부 기준은 다음 각 호와 같다.",
                cross_refs=extract_cross_refs("법 제5조에 따른 검사의 세부 기준은 다음 각 호와 같다.")),
    ]
