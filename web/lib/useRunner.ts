"use client";
import { useCallback, useRef, useState } from "react";
import { streamQuery } from "./sse";
import type { AgentResponse, DemoTrace, QueryType, StreamEvent } from "./types";

export type RunPhase = "idle" | "running" | "done" | "error";

export interface RunState {
  phase: RunPhase;
  question: string;
  seen: string[]; // 관찰한 백엔드 노드 step (순서대로, 재시도 시 중복 포함)
  activeStep: string | null;
  type: QueryType | null;
  strategy: string | null;
  response: AgentResponse | null;
  answer: string; // 점진적으로 드러나는 답변
  error: string | null;
}

const INITIAL: RunState = {
  phase: "idle",
  question: "",
  seen: [],
  activeStep: null,
  type: null,
  strategy: null,
  response: null,
  answer: "",
  error: null,
};

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// 노드별 체감 시간(데모 재생). 실제 지연이 아니라 진행을 읽히게 하는 연출값.
const STEP_MS: Record<string, number> = {
  classify: 620,
  retrieve: 900,
  grade_evidence: 760,
  generate: 940,
  verify: 680,
  refuse: 560,
  refuse_low_confidence: 620,
};

export function useRunner() {
  const [state, setState] = useState<RunState>(INITIAL);
  const runId = useRef(0);
  const abort = useRef<AbortController | null>(null);

  const reveal = useCallback(async (full: string, id: number) => {
    const step = Math.max(1, Math.floor(full.length / 90));
    for (let i = step; i < full.length; i += step) {
      if (id !== runId.current) return;
      const slice = full.slice(0, i);
      setState((s) => ({ ...s, answer: slice }));
      await sleep(16);
    }
    if (id === runId.current) setState((s) => ({ ...s, answer: full }));
  }, []);

  const reset = useCallback(() => {
    runId.current++;
    abort.current?.abort();
    setState(INITIAL);
  }, []);

  // 데모: 녹화된 trace(진행 이벤트 + 최종 응답)를 재생한다.
  const runDemo = useCallback(
    async (trace: DemoTrace) => {
      const id = ++runId.current;
      abort.current?.abort();
      setState({ ...INITIAL, phase: "running", question: trace.question });
      const seen: string[] = [];

      for (const ev of trace.events) {
        if (id !== runId.current) return;
        seen.push(ev.step);
        setState((s) => ({
          ...s,
          seen: [...seen],
          activeStep: ev.step,
          type: ev.query_type ?? s.type,
          strategy: ev.strategy ?? s.strategy,
        }));
        await sleep(STEP_MS[ev.step] ?? 700);
      }
      if (id !== runId.current) return;

      setState((s) => ({
        ...s,
        activeStep: null,
        response: trace.response,
        type: trace.response.query_type,
        strategy: trace.response.strategy,
      }));
      await reveal(trace.response.answer, id);
      if (id === runId.current) setState((s) => ({ ...s, phase: "done" }));
    },
    [reveal],
  );

  // 라이브: 로컬 FastAPI 백엔드에 SSE로 질의한다.
  const runLive = useCallback(
    async (apiBase: string, query: string) => {
      const id = ++runId.current;
      const controller = new AbortController();
      abort.current?.abort();
      abort.current = controller;
      setState({ ...INITIAL, phase: "running", question: query });
      const seen: string[] = [];
      let final: AgentResponse | null = null;

      try {
        await streamQuery(
          apiBase,
          query,
          (ev: StreamEvent) => {
            if (id !== runId.current) return;
            if ("response" in ev) {
              final = ev.response;
              setState((s) => ({
                ...s,
                activeStep: null,
                response: ev.response,
                type: ev.response.query_type,
                strategy: ev.response.strategy,
              }));
            } else {
              seen.push(ev.step);
              setState((s) => ({
                ...s,
                seen: [...seen],
                activeStep: ev.step,
                type: ev.query_type ?? s.type,
                strategy: ev.strategy ?? s.strategy,
              }));
            }
          },
          controller.signal,
        );
        if (id !== runId.current) return;
        // final은 위 SSE 콜백에서만 대입돼 TS 흐름 분석이 닿지 않으므로 단언이 필요하다.
        if (final) await reveal((final as AgentResponse).answer, id);
        if (id === runId.current) setState((s) => ({ ...s, phase: "done" }));
      } catch (err) {
        if (id !== runId.current) return;
        const message = err instanceof Error ? err.message : "알 수 없는 오류";
        setState((s) => ({ ...s, phase: "error", activeStep: null, error: message }));
      }
    },
    [reveal],
  );

  return { state, runDemo, runLive, reset };
}
