"use client";
import { highlightCitations } from "@/lib/citations";
import type { RunState } from "@/lib/useRunner";
import { Badge } from "./Badge";

export function AnswerCard({ state }: { state: RunState }) {
  const { phase, response, answer, error } = state;

  if (phase === "error") {
    return (
      <div className="rounded-md border border-danger/40 bg-[#fdf1ee] p-5 text-[15px] text-danger">
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
  // 진행 중이고 아직 드러난 답변 글자가 없으면 대기(응답 도착~첫 글자 사이 빈 렌더 방지).
  const waiting = phase === "running" && answer.length === 0;

  return (
    <div className="overflow-hidden rounded-md border border-line">
      <div className="flex flex-wrap items-center gap-2 border-b border-line bg-fill px-4 py-2.5">
        <span className="text-sm font-extrabold text-ink">답변</span>
        {response && response.retrieval_attempts > 0 && (
          <Badge tone="meta">검색 {response.retrieval_attempts}회</Badge>
        )}
        {response && !response.refused && response.generation_attempts > 0 && (
          <Badge tone="meta">생성 {response.generation_attempts}회</Badge>
        )}
        {response?.refused && <Badge tone="danger">거절</Badge>}
        {response?.low_confidence && !response.refused && <Badge tone="warning">신뢰도 낮음</Badge>}
        {response?.used_live_fallback && <Badge tone="success">실시간 조회</Badge>}
      </div>

      <div className="min-h-[2.5rem] px-4 py-4 text-[17px] leading-[1.8] text-ink sm:px-5">
        {waiting ? (
          <div className="space-y-2.5">
            <div className="shimmer h-4 w-11/12 rounded" />
            <div className="shimmer h-4 w-9/12 rounded" />
            <p className="pt-1 text-sm text-muted">근거 조문을 검색하고 답변을 작성하는 중…</p>
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
