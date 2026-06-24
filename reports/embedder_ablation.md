# 임베더·검색 전략 비교 (정답 조문 154문항)

## 임베더 3종 × 전략 (reranker off)

| 모델 | 전략 | hit_rate@1 | hit_rate@5 | recall@10 | mrr |
|---|---|---|---|---|---|
| nlpai-lab/KURE-v1 | vector | 0.539 | 0.844 | 0.896 | 0.672 |
| nlpai-lab/KURE-v1 | hybrid | 0.455 | 0.844 | 0.909 | 0.618 |
| nlpai-lab/KURE-v1 | graph | 0.279 | 0.890 | 0.945 | 0.529 |
| BAAI/bge-m3 | vector | 0.539 | 0.740 | 0.828 | 0.633 |
| BAAI/bge-m3 | hybrid | 0.468 | 0.805 | 0.854 | 0.602 |
| BAAI/bge-m3 | graph | 0.279 | 0.844 | 0.938 | 0.510 |
| intfloat/multilingual-e5-large | vector | 0.532 | 0.818 | 0.899 | 0.667 |
| intfloat/multilingual-e5-large | hybrid | 0.500 | 0.844 | 0.903 | 0.646 |
| intfloat/multilingual-e5-large | graph | 0.273 | 0.870 | 0.929 | 0.525 |

**vector hit@1 기준 모델: nlpai-lab/KURE-v1**

## nlpai-lab/KURE-v1 reranker on/off

### rerank=off

| 전략 | 유형 | hit_rate@1 | hit_rate@5 | recall@10 | mrr |
|---|---|---|---|---|---|
| vector | overall | 0.539 | 0.844 | 0.896 | 0.672 |
| vector | definition | 0.875 | 0.875 | 0.875 | 0.875 |
| vector | multihop | 0.479 | 0.829 | 0.889 | 0.630 |
| vector | single | 0.690 | 0.897 | 0.931 | 0.785 |
| hybrid | overall | 0.455 | 0.844 | 0.909 | 0.618 |
| hybrid | definition | 0.375 | 0.750 | 0.875 | 0.520 |
| hybrid | multihop | 0.402 | 0.829 | 0.906 | 0.583 |
| hybrid | single | 0.690 | 0.931 | 0.931 | 0.784 |
| graph | overall | 0.279 | 0.890 | 0.945 | 0.529 |
| graph | definition | 0.250 | 0.750 | 0.750 | 0.417 |
| graph | multihop | 0.248 | 0.889 | 0.957 | 0.519 |
| graph | single | 0.414 | 0.931 | 0.948 | 0.604 |

### rerank=on

| 전략 | 유형 | hit_rate@1 | hit_rate@5 | recall@10 | mrr |
|---|---|---|---|---|---|
| vector | overall | 0.734 | 0.948 | 0.961 | 0.827 |
| vector | definition | 0.875 | 1.000 | 1.000 | 0.938 |
| vector | multihop | 0.692 | 0.940 | 0.966 | 0.801 |
| vector | single | 0.862 | 0.966 | 0.931 | 0.903 |
| hybrid | overall | 0.727 | 0.948 | 0.961 | 0.824 |
| hybrid | definition | 0.875 | 0.875 | 0.875 | 0.875 |
| hybrid | multihop | 0.684 | 0.949 | 0.974 | 0.801 |
| hybrid | single | 0.862 | 0.966 | 0.931 | 0.903 |
| graph | overall | 0.727 | 0.955 | 0.968 | 0.827 |
| graph | definition | 0.875 | 1.000 | 1.000 | 0.938 |
| graph | multihop | 0.684 | 0.949 | 0.974 | 0.801 |
| graph | single | 0.862 | 0.966 | 0.931 | 0.903 |
