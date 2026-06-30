"use client";
import { Fragment } from "react";
import { PIPELINE, TYPE_LABEL } from "@/lib/pipeline";
import type { AgentResponse } from "@/lib/types";
import {
  IconCheck,
  IconDocCheck,
  IconDocSearch,
  IconPen,
  IconRefuse,
  IconShieldCheck,
  IconSparkle,
} from "./icons";

interface Props {
  seen: string[];
  activeStep: string | null;
  response: AgentResponse | null;
  running: boolean;
}

type NodeState = "active" | "done" | "pending";
type IconCmp = ({ className }: { className?: string }) => React.ReactElement;

const STEP_ICON: Record<string, IconCmp> = {
  classify: IconSparkle,
  retrieve: IconDocSearch,
  grade_evidence: IconDocCheck,
  generate: IconPen,
  verify: IconShieldCheck,
};

export function TraceTimeline({ seen, activeStep, response, running }: Props) {
  const seenSet = new Set(seen);
  const reachedIdx = PIPELINE.reduce((m, n, i) => (seenSet.has(n.key) ? i : m), -1);
  const activeIdx = PIPELINE.findIndex((n) => n.key === activeStep);
  const progressIdx = Math.max(reachedIdx, activeIdx);
  const refused = response?.refused ?? false;
  const attempts: Record<string, number> = {
    retrieve: response?.retrieval_attempts ?? 0,
    generate: response?.generation_attempts ?? 0,
  };
  const activeLabel = PIPELINE.find((n) => n.key === activeStep)?.label;

  const stateOf = (key: string): NodeState =>
    activeStep === key ? "active" : seenSet.has(key) ? "done" : "pending";

  return (
    <section>
      <div className="mb-4 flex items-center gap-2">
        <span className="text-[15px] font-bold text-ink">답변 근거 도출 과정</span>
        {running && (
          <span className="ml-auto inline-flex items-center gap-1.5 text-[12.5px] font-semibold text-brand">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand" />
            {activeLabel ? `${activeLabel} 중` : "실행 중"}
          </span>
        )}
      </div>

      <div className="rounded-card border border-line bg-surface px-5 py-5 shadow-sm sm:px-6">
        <div className="flex items-start">
          {PIPELINE.map((node, i) => {
            const st = stateOf(node.key);
            const count = attempts[node.key] ?? 0;
            const Icon = STEP_ICON[node.key];
            const connectorFilled = progressIdx > i;
            return (
              <Fragment key={node.key}>
                <div className="flex w-0 flex-1 flex-col items-center text-center">
                  <div
                    className={[
                      "relative flex h-[46px] w-[46px] items-center justify-center rounded-full transition-colors duration-300",
                      st === "active"
                        ? "animate-breathe bg-brand text-white"
                        : st === "done"
                          ? "bg-brand-soft text-brand"
                          : "bg-fill text-muted",
                    ].join(" ")}
                  >
                    <Icon className="h-[22px] w-[22px]" />
                    {st === "done" && (
                      <span className="absolute -bottom-0.5 -right-0.5 flex h-[18px] w-[18px] items-center justify-center rounded-full border-2 border-surface bg-brand text-white">
                        <IconCheck className="h-2.5 w-2.5" />
                      </span>
                    )}
                  </div>
                  <div
                    className={`mt-2.5 text-[13px] font-semibold ${st === "pending" ? "text-muted" : "text-ink"}`}
                  >
                    {node.label}
                  </div>
                  <div className="mt-0.5 text-[11px] leading-tight text-muted">{node.sub}</div>
                  {count > 1 && (
                    <span className="mt-1.5 inline-flex rounded-full bg-fill px-2 py-0.5 text-[10px] font-semibold text-muted">
                      재시도 ×{count}
                    </span>
                  )}
                </div>

                {i < PIPELINE.length - 1 && (
                  <div
                    className={`mt-[22px] h-0.5 w-6 shrink-0 rounded sm:w-9 ${
                      connectorFilled ? "bg-brand" : "bg-line"
                    }`}
                  />
                )}
              </Fragment>
            );
          })}

          {refused && (
            <>
              <div className="mt-[22px] h-0.5 w-6 shrink-0 rounded bg-danger/30 sm:w-9" />
              <div className="flex w-0 flex-1 flex-col items-center text-center">
                <div className="flex h-[46px] w-[46px] items-center justify-center rounded-full bg-[#feecec] text-danger">
                  <IconRefuse className="h-[22px] w-[22px]" />
                </div>
                <div className="mt-2.5 text-[13px] font-semibold text-danger">거절</div>
                <div className="mt-0.5 text-[11px] leading-tight text-muted">근거 없음</div>
              </div>
            </>
          )}
        </div>

        {response && (
          <div className="mt-5 flex flex-wrap items-center gap-2 border-t border-line pt-4 text-[13px] text-muted">
            <span className="rounded-chip bg-brand-soft px-2.5 py-0.5 text-[12.5px] font-semibold text-brand-strong">
              {TYPE_LABEL[response.query_type] ?? response.query_type}
            </span>
            {response.retrieval_attempts > 0 && (
              <>
                <span className="text-line-strong">·</span>
                <span>검색 {response.retrieval_attempts}회</span>
              </>
            )}
            {response.generation_attempts > 0 && (
              <>
                <span className="text-line-strong">·</span>
                <span>생성 {response.generation_attempts}회</span>
              </>
            )}
            {response.evidence.length > 0 && (
              <>
                <span className="text-line-strong">·</span>
                <span>근거 {response.evidence.length}건</span>
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
