from korean_maritime_law_rag.agent.generator import generate
from korean_maritime_law_rag.agent.state import GeneratedAnswer
from korean_maritime_law_rag.llm import FakeChatModel
from korean_maritime_law_rag.models import Article


def _articles():
    return [
        Article(law_id="100", law_name="테스트선박법", article_no="제83조",
                title="벌칙", text="제7조를 위반한 자는 3년 이하의 징역에 처한다."),
    ]


def test_generate_returns_answer_with_citations():
    scripted = GeneratedAnswer(answer="3년 이하의 징역에 처합니다.", citations=["100::제83조"])
    model = FakeChatModel(structured_outputs=[scripted])
    out = generate("건조검사 위반 처벌은?", _articles(), model)
    assert out.answer.strip()
    assert out.citations == ["100::제83조"]
