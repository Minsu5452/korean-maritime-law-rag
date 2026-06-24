// 백엔드(FastAPI /query/stream)와 데모 fixture가 공유하는 계약.
// AgentResponse는 src/korean_maritime_law_rag/agent/state.py의 모델과 일치한다.

export type QueryType = "single" | "definition" | "multihop" | "unanswerable";

// 데모(녹화 재생) vs 라이브(로컬 백엔드 SSE).
export type Mode = "demo" | "live";

export interface CitedArticle {
  doc_id: string;
  law_name: string;
  article_no: string;
  law_type: string;
  title: string;
  text: string;
}

export interface AgentResponse {
  answer: string;
  citations: string[];
  evidence: CitedArticle[];
  invalid_citations: string[];
  query_type: QueryType;
  strategy: string;
  refused: boolean;
  low_confidence: boolean;
  evidence_sufficient: boolean | null;
  evidence_reason: string;
  rewritten_query: string | null;
  retrieval_attempts: number;
  generation_attempts: number;
  used_live_fallback: boolean;
}

// /query/stream이 흘려보내는 노드 진행 이벤트.
export interface TraceEvent {
  step: string; // classify | retrieve | grade_evidence | generate | verify | refuse | refuse_low_confidence
  label: string;
  query_type: QueryType | null;
  strategy: string | null;
}

// 최종 이벤트는 step="final"에 response를 싣는다.
export interface FinalEvent {
  step: "final";
  response: AgentResponse;
}

export type StreamEvent = TraceEvent | FinalEvent;

// 데모 fixture = 한 질의를 실제로 실행해 녹화한 진행 이벤트 + 최종 응답.
export interface DemoTrace {
  id: string;
  question: string;
  tag: string; // 카드 칩에 보일 짧은 설명 (예: "멀티홉 · 그래프 확장")
  events: TraceEvent[];
  response: AgentResponse;
}
