"use client";
import { highlightCitations } from "@/lib/citations";
import type { RunState } from "@/lib/useRunner";
import { Badge } from "./Badge";
import { IconClock, IconSparkle } from "./icons";

export function AnswerCard({
  state,
  activeDocId,
  onHoverCite,
}: {
  state: RunState;
  activeDocId: string | null;
  onHoverCite: (docId: string | null) => void;
}) {
  const { phase, response, answer, error } = state;

  if (phase === "error") {
    return (
      <div className="rounded-2xl border border-danger/30 bg-[#fef2f2] p-5 text-[15px] text-danger">
        <p className="font-bold">라이브 백엔드에 연결하지 못했습니다.</p>
        <p className="mt-1">{error}</p>
        <p className="mt-2 text-[13px] text-danger/80">
          로컬 FastAPI 백엔드(localhost:8000)가 실행 중인지, 아니면 녹화 데모로 전환했는지
          확인하세요.
        </p>
      </div>
    );
  }

  const streaming =
    phase === "running" &&
    response !== null &&
    answer.length > 0 &&
    answer.length < response.answer.length;
  // 진행 중이고 아직 드러난 답변 글자가 없으면 대기(응답 도착~첫 글자 사이 빈 렌더 방지).
  const waiting = phase === "running" && answer.length === 0;

  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      <div className="flex flex-wrap items-center gap-2 px-5 pt-4 sm:px-6">
        <span className="text-[14px] font-bold text-ink">답변</span>
        {response && !response.refused && (
          <span className="inline-flex items-center gap-1.5 rounded-md bg-fill px-2 py-1 text-[11.5px] font-semibold text-ink-soft">
            <IconSparkle className="h-3 w-3" />
            근거 기반 생성
          </span>
        )}
        {response?.refused && <Badge tone="danger">거절</Badge>}
        {response?.low_confidence && !response.refused && <Badge tone="warning">신뢰도 낮음</Badge>}
        {response?.used_live_fallback && <Badge tone="success">실시간 조회</Badge>}
      </div>

      <div className="min-h-[2.5rem] px-5 py-4 text-[16.5px] leading-[1.85] text-ink sm:px-6">
        {waiting ? (
          <div className="space-y-2.5">
            <div className="shimmer h-4 w-11/12 rounded" />
            <div className="shimmer h-4 w-9/12 rounded" />
            <p className="pt-1 text-sm text-muted">근거 조문을 검색하고 답변을 작성하는 중…</p>
          </div>
        ) : (
          <p className={response?.refused ? "text-ink-soft" : ""}>
            <span className={streaming ? "caret" : ""}>
              {highlightCitations(answer, {
                evidence: response?.evidence ?? [],
                activeDocId,
                onHover: onHoverCite,
              })}
            </span>
          </p>
        )}
      </div>

      {response && !response.refused && !waiting && (
        <div className="flex items-center gap-2 border-t border-line px-5 py-3 text-[12.5px] text-muted sm:px-6">
          <IconClock className="h-3.5 w-3.5 text-brand" />
          근거 조문을 바탕으로 작성한 답변입니다 · 법적 효력 없음
        </div>
      )}
    </div>
  );
}
