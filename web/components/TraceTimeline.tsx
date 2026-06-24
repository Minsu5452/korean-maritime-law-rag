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
    <section className="rounded-2xl border border-line bg-surface/80 p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_12px_28px_-20px_rgba(15,23,42,0.25)]">
      <div className="mb-4 flex items-center gap-2">
        <span className="text-sm font-semibold text-ink">에이전트 진행</span>
        <span className="text-xs text-muted">LangGraph 노드</span>
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
          const Icon = node.Icon;
          const count = attempts[node.key] ?? 0;
          const connectorFilled = progressIdx > i;
          const connectorFlowing = running && activeIdx === i + 1;
          return (
            <Fragment key={node.key}>
              <div className="flex w-0 flex-1 flex-col items-center text-center">
                <div
                  className={[
                    "relative flex h-11 w-11 items-center justify-center rounded-full border transition-all duration-300",
                    st === "active"
                      ? "animate-node-pulse border-brand bg-brand-soft text-brand"
                      : st === "done"
                        ? "border-brand bg-brand text-white"
                        : "border-line bg-surface text-muted",
                  ].join(" ")}
                >
                  <Icon className="h-5 w-5" />
                  {count > 1 && (
                    <span className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full border border-white bg-amber-500 px-1 text-[10px] font-bold text-white">
                      ×{count}
                    </span>
                  )}
                </div>
                <div
                  className={`mt-2 text-xs font-semibold ${st === "pending" ? "text-muted" : "text-ink"}`}
                >
                  {node.label}
                </div>
                <div className="mt-0.5 text-[11px] leading-tight text-muted">{node.sub}</div>
              </div>

              {i < PIPELINE.length - 1 && (
                <div className="mt-5 h-0.5 w-6 shrink-0 sm:w-10">
                  <div
                    className={[
                      "h-full w-full rounded-full",
                      connectorFlowing
                        ? "trace-flow"
                        : connectorFilled
                          ? "bg-brand"
                          : "bg-line",
                    ].join(" ")}
                  />
                </div>
              )}
            </Fragment>
          );
        })}

        {refused && (
          <>
            <div className="mt-5 h-0.5 w-6 shrink-0 sm:w-10">
              <div className="h-full w-full rounded-full bg-rose-300" />
            </div>
            <div className="flex w-0 flex-1 flex-col items-center text-center">
              <div className="flex h-11 w-11 items-center justify-center rounded-full border border-rose-200 bg-rose-50 text-rose-600">
                <IconRefuse className="h-5 w-5" />
              </div>
              <div className="mt-2 text-xs font-semibold text-rose-600">거절</div>
              <div className="mt-0.5 text-[11px] leading-tight text-muted">근거 없음</div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
