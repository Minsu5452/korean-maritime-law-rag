import type { ComponentType } from "react";
import {
  IconClassify,
  IconGenerate,
  IconGrade,
  IconRetrieve,
  IconVerify,
} from "@/components/icons";

export interface PipelineNode {
  key: string;
  label: string;
  sub: string;
  Icon: ComponentType<{ className?: string }>;
}

// 답변 근거 도출 과정(사용자 관점 라벨). 내부적으로는 LangGraph 노드와 1:1 대응.
export const PIPELINE: PipelineNode[] = [
  { key: "classify", label: "질문 분석", sub: "유형 판별", Icon: IconClassify },
  { key: "retrieve", label: "조문 검색", sub: "관련 조문 탐색", Icon: IconRetrieve },
  { key: "grade_evidence", label: "근거 확인", sub: "충분성 판단", Icon: IconGrade },
  { key: "generate", label: "답변 작성", sub: "근거 기반 생성", Icon: IconGenerate },
  { key: "verify", label: "인용 검증", sub: "인용 정확성 확인", Icon: IconVerify },
];

export const TYPE_LABEL: Record<string, string> = {
  single: "단일 조문",
  definition: "정의",
  multihop: "멀티홉",
  unanswerable: "근거 없음",
};

export const STRATEGY_LABEL: Record<string, string> = {
  vector: "벡터",
  hybrid: "하이브리드",
  graph: "그래프 확장",
  none: "없음",
};

export const LAW_TYPE_TONE: Record<string, string> = {
  법률: "bg-blue-50 text-blue-700 border-blue-200",
  시행령: "bg-indigo-50 text-indigo-700 border-indigo-200",
  시행규칙: "bg-violet-50 text-violet-700 border-violet-200",
};
