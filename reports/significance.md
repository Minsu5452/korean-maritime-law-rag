# 검색 전략 통계 요약

이 표는 `scripts/significance.py`로 생성한 마지막 저장 결과입니다. hit@1은 검색 인덱스 빌드에 따라
문항 단위로 1건 정도 달라질 수 있어, 임베더 비교표(`reports/embedder_ablation.md`)와 정확히 맞추려면
두 리포트를 같은 인덱스에서 함께 재생성해야 합니다(`make up && make index`).

정답 조문이 있는 질문은 n=154입니다(multihop 117, single 29, definition 8).

| 전략/라우팅 | 유형 | hit@1 | 95% Wilson CI |
|---|---|---|---|
| vector | overall | 83/154=0.539 | [0.460, 0.616] |
| vector | single | 21/29=0.724 | [0.543, 0.853] |
| vector | definition | 6/8=0.750 | [0.409, 0.929] |
| vector | multihop | 56/117=0.479 | [0.390, 0.568] |
| hybrid | overall | 71/154=0.461 | [0.384, 0.540] |
| hybrid | single | 21/29=0.724 | [0.543, 0.853] |
| hybrid | definition | 3/8=0.375 | [0.137, 0.694] |
| hybrid | multihop | 47/117=0.402 | [0.317, 0.492] |
| graph | overall | 42/154=0.273 | [0.209, 0.348] |
| graph | single | 12/29=0.414 | [0.255, 0.593] |
| graph | definition | 2/8=0.250 | [0.071, 0.591] |
| graph | multihop | 28/117=0.239 | [0.171, 0.324] |
| oracle 라우팅 | overall | 55/154=0.357 | [0.286, 0.435] |
| oracle 라우팅 | single | 21/29=0.724 | [0.543, 0.853] |
| oracle 라우팅 | definition | 6/8=0.750 | [0.409, 0.929] |
| oracle 라우팅 | multihop | 28/117=0.239 | [0.171, 0.324] |

## 멀티홉(n=117) McNemar 비교
- graph vs vector: graph만 맞춘 문항 b=17, vector만 맞춘 문항 c=45, p=0.0005 (p < 0.05)
- graph vs hybrid: graph만 맞춘 문항 b=21, hybrid만 맞춘 문항 c=40, p=0.0204 (p < 0.05)
