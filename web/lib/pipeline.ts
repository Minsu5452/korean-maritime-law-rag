export interface PipelineNode {
  key: string;
  label: string;
  sub: string;
}

// 답변 근거 도출 과정(사용자 관점 라벨). 내부적으로는 LangGraph 노드와 1:1 대응.
export const PIPELINE: PipelineNode[] = [
  { key: "classify", label: "질문 분석", sub: "유형 판별" },
  { key: "retrieve", label: "조문 검색", sub: "관련 조문 탐색" },
  { key: "grade_evidence", label: "근거 확인", sub: "충분성 판단" },
  { key: "generate", label: "답변 작성", sub: "근거 기반 생성" },
  { key: "verify", label: "인용 검증", sub: "인용 정확성 확인" },
];

export const TYPE_LABEL: Record<string, string> = {
  single: "단일 조문",
  definition: "정의",
  multihop: "여러 조문 연계",
  unanswerable: "근거 없음",
};

export const STRATEGY_LABEL: Record<string, string> = {
  vector: "벡터",
  hybrid: "하이브리드",
  graph: "그래프 확장",
  none: "없음",
};

// 법령 종류 칩(회색 톤). 종류 텍스트 자체로 구분되므로 색은 절제한다.
export const LAW_TYPE_TONE = "border-line bg-fill text-ink-soft";
