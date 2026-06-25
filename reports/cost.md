# 질의당 토큰·비용

에이전트 모델 `openai:gpt-4o-mini` 기준, 골드셋 답변 가능 문항 18건을 실제로 실행해 측정했습니다.
비용은 OpenAI 공개 단가(입력 $0.15 / 출력 $0.60 per 1M tokens) 기준 추정이며, 단가가 바뀌면 `scripts/measure_cost.py`의 `PRICE`를 갱신해 재계산합니다.

| 지표 | 수치 |
|---|---:|
| 측정 문항 | 18 |
| 질의당 입력 토큰(평균) | 5635 |
| 질의당 출력 토큰(평균) | 202 |
| 질의당 비용(추정) | $0.00097 (약 1.4원) |

재현: `OPENAI_API_KEY=... uv run python scripts/measure_cost.py`
