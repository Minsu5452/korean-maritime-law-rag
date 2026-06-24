"use client";
import { highlightCitations } from "@/lib/citations";
import { STRATEGY_LABEL, TYPE_LABEL } from "@/lib/pipeline";
import type { RunState } from "@/lib/useRunner";
import { Badge } from "./Badge";

export function AnswerCard({ state }: { state: RunState }) {
  const { phase, response, answer, type, strategy, error } = state;

  if (phase === "error") {
    return (
      <div className="rounded-lg border border-danger/40 bg-[#fdf1ee] p-5 text-[15px] text-danger">
        <p className="font-bold">라이브 백엔드에 연결하지 못했습니다.</p>
        <p className="mt-1">{error}</p>
        <p className="mt-2 text-[13px] text-danger/80">
          로컬에서 <span className="font-mono">uvicorn</span> 백엔드를 띄웠는지, 녹화 데모로
          전환했는지 확인하세요.
        </p>
      </div>
    );
  }

  const streaming =
    phase === "running" &&
    response !== null &&
    answer.length > 0 &&
    answer.length < response.answer.length;
  const waiting = phase === "running" && response === null;

  return (
    <div className="rounded-lg border border-line bg-surface p-6">
      <div className="flex flex-wrap items-center gap-2">
        <span className="mr-1 text-sm font-bold text-ink">답변</span>
        {type && <Badge tone="brand">유형 {TYPE_LABEL[type] ?? type}</Badge>}
        {strategy && strategy !== "none" && (
          <Badge tone="brandSoft">검색 {STRATEGY_LABEL[strategy] ?? strategy}</Badge>
        )}
        {response && response.retrieval_attempts > 0 && (
          <Badge tone="meta">검색 {response.retrieval_attempts}회</Badge>
        )}
        {response && !response.refused && response.generation_attempts > 0 && (
          <Badge tone="meta">생성 {response.generation_attempts}회</Badge>
        )}
        {response?.refused && <Badge tone="danger">거절</Badge>}
        {response?.low_confidence && !response.refused && <Badge tone="warning">저신뢰</Badge>}
        {response?.used_live_fallback && <Badge tone="success">실시간 조회</Badge>}
      </div>

      <div className="mt-4 min-h-[2.5rem] text-[17px] leading-[1.8] text-ink">
        {waiting ? (
          <div className="space-y-2.5">
            <div className="shimmer h-4 w-11/12 rounded" />
            <div className="shimmer h-4 w-9/12 rounded" />
            <p className="pt-1 text-sm text-muted">근거 조문을 검색하고 답변을 만드는 중…</p>
          </div>
        ) : (
          <p className={response?.refused ? "text-ink-soft" : ""}>
            <span className={streaming ? "caret" : ""}>{highlightCitations(answer)}</span>
          </p>
        )}
      </div>
    </div>
  );
}
