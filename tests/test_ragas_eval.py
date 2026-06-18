from korean_maritime_law_rag.evaluation.ragas_eval import build_ragas_rows


def test_build_ragas_rows_maps_fields():
    records = [{
        "question": "건조검사 위반 처벌은?",
        "answer": "1년 이하 징역.",
        "contexts": ["제83조 본문", "제5조 본문"],
        "reference": "제83조: 1년 이하의 징역",
    }]
    rows = build_ragas_rows(records)
    assert rows == [{
        "user_input": "건조검사 위반 처벌은?",
        "response": "1년 이하 징역.",
        "retrieved_contexts": ["제83조 본문", "제5조 본문"],
        "reference": "제83조: 1년 이하의 징역",
    }]


def test_build_ragas_rows_skips_records_without_contexts():
    records = [
        {"question": "q1", "answer": "a1", "contexts": [], "reference": "r1"},
        {"question": "q2", "answer": "a2", "contexts": ["c"], "reference": "r2"},
    ]
    rows = build_ragas_rows(records)
    assert len(rows) == 1
    assert rows[0]["user_input"] == "q2"
