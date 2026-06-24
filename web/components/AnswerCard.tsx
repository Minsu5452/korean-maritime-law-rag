"use client";
import { highlightCitations } from "@/lib/citations";
import { STRATEGY_LABEL, TYPE_LABEL } from "@/lib/pipeline";
import type { RunState } from "@/lib/useRunner";
import { Badge } from "./Badge";

export function AnswerCard({ state }: { state: RunState }) {
  const { phase, response, answer, type, strategy, error } = state;

  if (phase === "error") {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-700">
        <p className="font-semibold">라이브 백엔드에 연결하지 못했습니다.</p>
        <p className="mt-1 text-rose-600/90">{error}</p>
        <p className="mt-2 text-xs text-rose-500">
          로컬에서 <span className="font-mono">uvicorn</span> 백엔드를 띄웠는지, 데모 모드로
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
    <div className="rounded-2xl border border-line bg-surface p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_12px_28px_-20px_rgba(15,23,42,0.25)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-ink text-[11px] font-bold text-white">
          A
        </span>
        {type && <Badge tone="indigo">유형 {TYPE_LABEL[type] ?? type}</Badge>}
        {strategy && strategy !== "none" && (
          <Badge tone="blue">검색 {STRATEGY_LABEL[strategy] ?? strategy}</Badge>
        )}
        {response && response.retrieval_attempts > 0 && (
          <Badge tone="slate">검색 {response.retrieval_attempts}회</Badge>
        )}
        {response && !response.refused && response.generation_attempts > 0 && (
          <Badge tone="slate">생성 {response.generation_attempts}회</Badge>
        )}
        {response?.refused && <Badge tone="rose">거절</Badge>}
        {response?.low_confidence && !response.refused && <Badge tone="amber">저신뢰</Badge>}
        {response?.used_live_fallback && <Badge tone="emerald">실시간 조회</Badge>}
      </div>

      <div className="mt-4 min-h-[2.5rem] text-[15px] leading-[1.85] text-ink">
        {waiting ? (
          <div className="space-y-2">
            <div className="shimmer h-3.5 w-11/12 rounded" />
            <div className="shimmer h-3.5 w-9/12 rounded" />
            <p className="pt-1 text-xs text-muted">근거 조문을 검색하고 답변을 만드는 중…</p>
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
