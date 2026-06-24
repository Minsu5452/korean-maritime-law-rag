"use client";
import { Fragment } from "react";
import { PIPELINE } from "@/lib/pipeline";
import type { AgentResponse } from "@/lib/types";
import { IconRefuse } from "./icons";

interface Props {
  seen: string[];
  activeStep: string | null;
  response: AgentResponse | null;
  running: boolean;
}

type NodeState = "active" | "done" | "pending";

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

  const stateOf = (key: string): NodeState =>
    activeStep === key ? "active" : seenSet.has(key) ? "done" : "pending";

  return (
    <section className="rounded-lg border border-line bg-surface p-6">
      <div className="mb-5 flex items-center gap-2">
        <span className="text-sm font-bold text-ink-soft">답변 근거 도출 과정</span>
        {running && (
          <span className="ml-auto inline-flex items-center gap-1.5 text-xs font-medium text-brand">
            <span className="h-1.5 w-1.5 animate-ping rounded-full bg-brand" />
            실행 중
          </span>
        )}
      </div>

      <div className="flex items-start">
        {PIPELINE.map((node, i) => {
          const st = stateOf(node.key);
          const count = attempts[node.key] ?? 0;
          const connectorFilled = progressIdx > i;
          return (
            <Fragment key={node.key}>
              <div className="flex w-0 flex-1 flex-col items-center text-center">
                <div
                  className={[
                    "relative flex h-10 w-10 items-center justify-center rounded-lg border text-[16px] font-bold transition-colors duration-300",
                    st === "active"
                      ? "animate-step-ring border-brand bg-brand-soft text-brand"
                      : st === "done"
                        ? "border-brand bg-brand text-white"
                        : "border-line bg-surface text-muted",
                  ].join(" ")}
                >
                  {i + 1}
                  {count > 1 && (
                    <span className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full border border-white bg-warning px-1 text-[10px] font-bold text-ink">
                      ×{count}
                    </span>
                  )}
                </div>
                <div
                  className={`mt-2 text-sm font-bold ${st === "pending" ? "text-muted" : "text-ink"}`}
                >
                  {node.label}
                </div>
                <div className="mt-0.5 text-xs leading-tight text-muted">{node.sub}</div>
              </div>

              {i < PIPELINE.length - 1 && (
                <div className="mt-5 h-0.5 w-6 shrink-0 sm:w-10">
                  <div
                    className={`h-full w-full rounded ${connectorFilled ? "bg-brand" : "bg-line"}`}
                  />
                </div>
              )}
            </Fragment>
          );
        })}

        {refused && (
          <>
            <div className="mt-5 h-0.5 w-6 shrink-0 sm:w-10">
              <div className="h-full w-full rounded bg-danger/40" />
            </div>
            <div className="flex w-0 flex-1 flex-col items-center text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-danger/40 bg-[#fdf1ee] text-danger">
                <IconRefuse className="h-5 w-5" />
              </div>
              <div className="mt-2 text-sm font-bold text-danger">거절</div>
              <div className="mt-0.5 text-xs leading-tight text-muted">근거 없음</div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
