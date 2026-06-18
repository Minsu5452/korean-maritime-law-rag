# RAGAS 평가

이 파일은 `scripts/ragas_score.py`로 생성한 마지막 저장 결과입니다.
평가 모델은 실행 시점 인자 또는 스크립트 기본값을 따르므로, 현재 모델 기준 수치가 필요하면
`OPENAI_API_KEY=... /root/ragasenv/bin/python scripts/ragas_score.py`로 다시 생성해야 합니다.

| 지표 | 값 |
|---|---|
| 근거성(faithfulness) | 0.940 |
| 답변 관련성(answer relevancy) | 0.876 |
| 검색 문맥 정밀도(context precision) | 0.984 |
| 검색 문맥 재현율(context recall) | 0.991 |
