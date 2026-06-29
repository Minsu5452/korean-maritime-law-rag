# 해양법령 길잡이 — 웹 데모

상위 `korean-maritime-law-rag` 백엔드를, 해양경찰청 현장 실무를 가정해 보여주는 Next.js
프론트엔드입니다. 에이전트가 질문을 분석하고, 조문을
검색하고, 근거를 확인하고, 답변을 작성한 뒤 인용을 검증하는 과정을 단계별로 시각화하고,
답변이 근거로 삼은 조문을 시행일·원문 링크와 함께 카드로 보여줍니다.

두 가지 모드가 있습니다.

- **녹화 데모(기본)**: `scripts/capture_demo_traces.py`로 실제 실행한 질의·응답을 `public/demo/traces.json`에 녹화해, 백엔드나 API 키 없이 그대로 재생합니다.
- **라이브**: 로컬 FastAPI 백엔드의 `/query/stream`(SSE)에 직접 질의합니다.

## 개발

```bash
npm install
npm run dev      # http://localhost:3000
```

라이브 모드는 백엔드가 필요합니다(저장소 루트에서 실행).

```bash
make up && make index
OPENAI_API_KEY=... uv run uvicorn korean_maritime_law_rag.serving.app:app --port 8000
```

백엔드 주소는 `NEXT_PUBLIC_API_BASE`(기본값 `http://localhost:8000`)로 바꿉니다.

## 빌드 / 배포

```bash
npm run build    # 정적 사이트를 out/에 생성 (next.config.ts의 output: "export")
```

`out/`은 정적 호스팅에 그대로 올릴 수 있습니다. Vercel은 이 `web/` 디렉터리를 루트로 임포트하면
녹화 데모가 키 없이 배포됩니다.

## 구성

```text
web/
├── app/         레이아웃·페이지(클라이언트 오케스트레이션)
├── components/  Header · QueryBar · TraceTimeline · AnswerCard · EvidenceList 등
├── lib/         타입, SSE 클라이언트, 데모 재생/라이브 실행 훅
└── public/demo/ 녹화된 질의 트레이스(traces.json)
```

데모 데이터를 다시 만들려면 백엔드 인덱스를 띄운 뒤 저장소 루트에서:

```bash
OPENAI_API_KEY=... uv run python scripts/capture_demo_traces.py
```
