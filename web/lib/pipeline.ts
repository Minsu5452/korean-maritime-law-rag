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

// LangGraph 에이전트의 핵심 경로(분류→검색→근거평가→생성→검증).
export const PIPELINE: PipelineNode[] = [
  { key: "classify", label: "질문 분류", sub: "유형 판별", Icon: IconClassify },
  { key: "retrieve", label: "검색", sub: "BM25·벡터·그래프", Icon: IconRetrieve },
  { key: "grade_evidence", label: "근거 평가", sub: "충분성 판단", Icon: IconGrade },
  { key: "generate", label: "답변 생성", sub: "인용 범위 제한", Icon: IconGenerate },
  { key: "verify", label: "인용 검증", sub: "환각 인용 제거", Icon: IconVerify },
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
  graph: "그래프",
  none: "없음",
};

export const LAW_TYPE_TONE: Record<string, string> = {
  법률: "bg-blue-50 text-blue-700 border-blue-200",
  시행령: "bg-indigo-50 text-indigo-700 border-indigo-200",
  시행규칙: "bg-violet-50 text-violet-700 border-violet-200",
};
