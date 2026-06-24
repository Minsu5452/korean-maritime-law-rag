# 아키텍처

이 프로젝트는 해양 관련 법령을 조문 단위로 정규화하고, 텍스트 검색과 조문 관계 그래프를 함께 사용하는 RAG 시스템입니다.
LLM은 질문 분류, 근거 평가, 쿼리 재작성, 답변 생성에 사용하고, 수집·파싱·검색·인용 검증은 가능한 한 결정적인 코드 경로로 처리합니다.

## 전체 흐름

```text
law.go.kr OPEN API
  -> raw JSON cache
  -> Article parser
  -> BM25 / Qdrant / Neo4j
  -> Retriever(RRF, optional reranker)
  -> LangGraph agent
  -> FastAPI
  -> Next.js 웹 데모 (web/)
```

| 단계 | 주요 파일 | 책임 |
|---|---|---|
| 수집 | `collectors/law_api.py`, `scripts/collect.py` | 현행 법령 검색, 본문 다운로드, raw JSON 캐시 저장 |
| 파싱 | `parsing/article_parser.py`, `parsing/crossref.py` | 조문·별표 정규화, 인용·준용·위임 관계 추출 |
| 색인 | `indexing/lexical.py`, `indexing/vector.py`, `indexing/graph.py` | BM25, Qdrant, Neo4j 인덱스 구축 |
| 검색 | `retrieval/retriever.py`, `retrieval/fusion.py`, `retrieval/reranker.py` | 전략별 검색, RRF 병합, 선택적 reranking |
| 에이전트 | `agent/graph.py`, `agent/generator.py`, `agent/verify.py` | 질문 분류, 검색, 근거 평가, 생성, 인용 검증 |
| 서빙 | `serving/app.py` | health/readiness, 질의 API, SSE 스트리밍 |
| 프론트엔드 | `web/` (Next.js) | 에이전트 트레이스 시각화, 근거 조문 인용 카드, 녹화/라이브 모드 |
| 평가 | `evaluation/`, `scripts/evaluate*.py`, `scripts/significance.py` | 검색 전략, 생성 품질, 지연 시간 평가 |

## 데이터와 코퍼스

`configs/laws.yaml`의 법령명을 기준으로 법률, 시행령, 시행규칙을 함께 수집합니다. API 응답은 `data/cache/raw/`에 저장해 API 키 없이도 인덱싱과 테스트를 재현할 수 있게 했습니다.

현재 캐시 기준 규모는 다음과 같습니다.

| 지표 | 값 |
|---|---:|
| 법령 문서 | 105 |
| 조문·별표 | 7,506 |
| 그래프 엣지 | 16,281 |
| CITES | 11,025 |
| APPLIES | 394 |
| IMPLEMENTS | 4,862 |

`docs/api-notes.md`에는 law.go.kr 응답 필드와 파서가 처리해야 하는 응답 변형을 따로 정리했습니다.

## 파싱과 관계 추출

`article_parser.py`는 law.go.kr 본문 응답을 `Article` 모델로 변환합니다.
조문과 별표를 같은 검색 단위로 다루고, 법령명, 조문번호, 제목, 시행일, 법령 종류, 상위 법률 ID를 메타데이터로 보관합니다.

`crossref.py`는 조문 텍스트에서 다음 관계를 추출합니다.

| 관계 | 의미 | 예 |
|---|---|---|
| `CITES` | 다른 조문을 인용 | `「선박안전법」 제8조` |
| `APPLIES` | 준용 관계 | `제5조를 준용한다` |
| `IMPLEMENTS` | 하위 법령이 상위 법률 조문을 구현 | 시행령·시행규칙 본문의 `법 제N조` |

법령 인용은 표기가 비교적 명시적이어서 LLM 추출 대신 규칙 기반 파서를 사용했습니다.
이 방식은 누락 가능성이 있지만, 실행 결과가 재현 가능하고 단위 테스트로 관리하기 쉽습니다.

## 인덱스

세 인덱스는 같은 `Article` 코퍼스를 공유합니다.

- `Bm25Index`: Kiwi 토큰화 기반의 표면형 검색
- `VectorIndex`: Qdrant에 임베딩 벡터 저장, `doc_id` 기반 UUID5로 멱등 upsert
- `GraphStore`: Neo4j에 `Law`, `Article`, `CITES`, `APPLIES`, `IMPLEMENTS` 저장

`GraphStore.upsert_articles()`는 기존 그래프를 유지하며 노드와 엣지를 MERGE합니다.
반면 `GraphStore.build()`는 초기 구축용 전체 재빌드 함수라 Neo4j DB의 기존 노드를 삭제합니다.
개발용 그래프와 통합 테스트용 그래프가 같은 DB를 공유하지 않도록 `integration` 테스트는 분리해서 실행해야 합니다.

## 검색

`Retriever`는 세 가지 전략을 제공합니다.

| 전략 | 구성 |
|---|---|
| `vector` | Qdrant cosine 검색 |
| `hybrid` | vector + BM25 RRF |
| `graph` | vector + BM25 + 그래프 확장 RRF |

질문 유형에 따라 전략을 라우팅합니다(`agent/router.py`).

| 질문 유형 | 전략 | 의도 |
|---|---|---|
| 단일 조문(single) | hybrid | 표면형과 의미를 함께 |
| 정의(definition) | vector | 의미 중심 |
| 멀티홉(multihop) | graph | 인용·위임 관계로 후보 확장 |
| `「법령명」 제N조` 형태 | graph | 분류를 건너뛰고 정확 조문 고정 |

그래프 전략은 먼저 텍스트 기반 후보를 얻고, 해당 후보의 인접 조문을 Neo4j에서 확장합니다.
이 확장 후보는 별도 ranking으로 보고 RRF에 합산합니다.
질문에 `「법령명」 제N조` 형태가 들어 있으면 `parse_citation()`으로 먼저 잡아 graph 검색에서 해당 조문을 최상위로 고정합니다(RRF 점수에 +1.0). 로컬 인덱스에 그 조문이 없고 실시간 조회가 켜져 있으면 law.go.kr를 한 번 조회해 보강합니다.

reranker는 기본값이 꺼져 있습니다.
`BAAI/bge-reranker-v2-m3` cross-encoder를 사용할 수 있지만, 로컬 실행 비용과 GPU 의존성이 있어 선택 기능으로 둡니다.

## 에이전트

`agent/graph.py`는 LangGraph 워크플로를 구성합니다.

```text
classify
  -> refuse                         # unanswerable: 검색 없이 거절
  -> retrieve
  -> grade_evidence
      -> rewrite_query + retrieve   # 근거 부족 + 재작성 가능 시 재검색
      -> refuse                     # 재검색 후에도 근거 부족(저신뢰 거절)
      -> generate
  -> verify
      -> regenerate                 # 인용이 검색 결과 밖이면 재생성
      -> done
```

에이전트 상태에는 질문 유형, 선택된 검색 전략, 근거 충분성, 검색 횟수, 생성 횟수, 잘못된 인용 목록이 남습니다.
`generator.py`는 검색된 `doc_id`만 citation enum으로 넘겨 생성 모델이 검색 결과 밖의 조문을 인용하지 못하도록 제한합니다.
`verify.py`는 생성 결과의 citation이 실제 검색 결과에 포함되는지 한 번 더 확인합니다.
거절은 두 경로입니다. classify에서 unanswerable로 분류되면 검색 없이 거절하고(`strategy=none`), grade_evidence 후에도 근거가 부족하면 저신뢰로 거절합니다(`low_confidence=true`). 재검색과 재생성은 각각 기본 2회로 제한합니다.

## 서빙과 관측성

`serving/app.py`는 다음 엔드포인트를 제공합니다.

- `GET /health`
- `GET /ready`
- `POST /query`
- `POST /query/stream`

`/query/stream`은 LangGraph 노드 진행을 SSE로 흘려보냅니다.
`web/`의 Next.js 프론트엔드는 이 스트림을 그대로 시각화합니다. 분류→검색→근거 평가→생성→검증 진행과 근거 조문 인용을 보여주며, 실제 실행을 녹화해 키 없이 재생하는 데모 모드와 로컬 백엔드에 직접 질의하는 라이브 모드를 둡니다. 데모 데이터는 `scripts/capture_demo_traces.py`로 생성합니다.
Langfuse는 선택 기능이며, 키나 패키지가 없으면 관측성 없이 실행됩니다.
로컬에서 추적을 보려면 `make up`으로 Langfuse 컨테이너를 띄운 뒤 `uv sync --extra obs`와
`MLR_LANGFUSE_ENABLED=true`를 사용합니다. 개발용 public/secret key는 `.env.example`과
`docker-compose.yml`의 초기화 값에 맞춰 두었습니다.

검색 결과가 로컬 인덱스에 없을 때 law.go.kr를 즉시 조회하는 실시간 조회도 선택 기능입니다.
`MLR_ENABLE_LAW_API_FALLBACK=true`와 `MLR_LAW_OC`가 모두 있어야 하며, 네트워크와 외부 API 상태에 의존합니다.

## 평가

검색 평가는 `tests/qa_pairs.yaml`의 골드 질의셋을 사용합니다.
정답 조문이 있는 문항은 hit@1, hit@5, recall@10, MRR을 계산하고, unanswerable 문항은 거절 정확도로 봅니다.

주요 스크립트:

| 스크립트 | 출력 |
|---|---|
| `scripts/validate_gold.py` | 골드셋 구조 검증 |
| `scripts/significance.py` | 전략별 hit@1, Wilson CI, McNemar 비교 |
| `scripts/ablation_embeddings.py` | 임베더·검색전략·reranker 비교 |
| `scripts/evaluate_all.py` | 에이전트 분류, 인용, 거절, 근거성, 지연 평가 |
| `scripts/ragas_score.py` | 격리 환경에서 RAGAS 지표 계산 |

평가 결과는 `reports/`에 저장합니다.
README에는 핵심 요약만 두고, 상세 수치와 표는 report 파일을 기준으로 확인합니다.

## 운영 메모

- `make up`은 Qdrant, Neo4j, 로컬 Langfuse 컨테이너를 실행합니다. 앱이 추적 정보를 보내는지는 `MLR_LANGFUSE_ENABLED` 설정으로 결정합니다.
- `make index`는 raw JSON 캐시에서 BM25, Qdrant, Neo4j 인덱스를 다시 만듭니다.
- `scripts/embed_corpus.py`는 임베딩을 `data/embeddings/*.npz`로 미리 저장해 반복 인덱싱 시간을 줄입니다.
- `scripts/poll_amendments.py --reindex`는 수집 대상 법령의 개정 여부를 확인하고 변경분을 다시 색인합니다.
- `MLR_AS_OF=YYYYMMDD`는 ablation·골드체인 추출 스크립트에서 해당 일자 기준 현행 조문만 남기는 필터입니다(`corpus.filter_as_of`). 기본 색인·서빙 경로는 캐시 전체를 사용하며, 과거 시점 전문 복원 기능은 아닙니다.
- 기본 테스트는 외부 API, 실제 LLM, 실제 임베딩 모델 다운로드에 의존하지 않습니다.
- `tests/test_graph.py`는 Neo4j가 필요한 통합 테스트이며 기본 pytest 실행에서는 제외됩니다.
- 수집에는 `MLR_LAW_OC`, 에이전트와 생성 평가에는 `OPENAI_API_KEY`가 필요합니다.
- `make smoke`는 설정과 로컬 파일 경로 중심의 빠른 점검입니다. 실제 Qdrant, Neo4j, LLM 호출까지 보려면 인덱싱과 API 실행 경로를 별도로 확인해야 합니다.

## 한계

- 조문 수준 검색을 기준으로 하며, 호·목 단위의 세밀한 참조 해석은 제한적입니다.
- 별표 내부 참조나 복잡한 약칭 인용은 일부 누락될 수 있습니다.
- 현행 법령 기준으로 설계되어 과거 시점별 조문 복원은 지원하지 않습니다.
- 내부 평가용 골드셋이므로 외부 공개 벤치마크와 직접 비교하기에는 범위가 다릅니다.
