"use client";
import { useEffect, useRef, useState } from "react";
import { AnswerCard } from "@/components/AnswerCard";
import { EvidenceList } from "@/components/EvidenceList";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { QueryBar } from "@/components/QueryBar";
import { TraceTimeline } from "@/components/TraceTimeline";
import { DEFAULT_API_BASE } from "@/lib/constants";
import type { DemoTrace, Mode } from "@/lib/types";
import { useRunner } from "@/lib/useRunner";

export default function Home() {
  const [mode, setMode] = useState<Mode>("demo");
  const [traces, setTraces] = useState<DemoTrace[]>([]);
  const [activeId, setActiveId] = useState<string | undefined>(undefined);
  const { state, runDemo, runLive, reset } = useRunner();
  const autoStarted = useRef(false);

  useEffect(() => {
    fetch("/demo/traces.json")
      .then((r) => r.json())
      .then((data: DemoTrace[]) => setTraces(data))
      .catch(() => undefined);
  }, []);

  // 첫 진입 시 대표 예시를 자동 재생해 바로 동작을 보여준다.
  useEffect(() => {
    if (!autoStarted.current && mode === "demo" && traces.length > 0) {
      autoStarted.current = true;
      setActiveId(traces[0].id);
      runDemo(traces[0]);
    }
  }, [traces, mode, runDemo]);

  const onDemo = (t: DemoTrace) => {
    setActiveId(t.id);
    runDemo(t);
  };
  const onLive = (q: string) => {
    setActiveId(undefined);
    runLive(DEFAULT_API_BASE, q);
  };
  const onMode = (m: Mode) => {
    setMode(m);
    reset();
    setActiveId(undefined);
  };

  const started = state.phase !== "idle";

  return (
    <div className="flex min-h-full flex-col">
      <Header mode={mode} onMode={onMode} />
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 pb-10 pt-9 sm:pt-12">
        <Hero />
        <div className="mt-7">
          <QueryBar
            mode={mode}
            traces={traces}
            running={state.phase === "running"}
            question={state.question}
            activeId={activeId}
            onDemo={onDemo}
            onLive={onLive}
          />
        </div>

        {started ? (
          <div className="mt-6 space-y-4">
            <TraceTimeline
              seen={state.seen}
              activeStep={state.activeStep}
              response={state.response}
              running={state.phase === "running"}
            />
            <AnswerCard state={state} />
            {state.response && <EvidenceList items={state.response.evidence} />}
          </div>
        ) : (
          <p className="mt-10 text-center text-sm text-muted">
            예시 질의를 선택하면 에이전트의 검색·생성 과정을 단계별로 보여줍니다.
          </p>
        )}
      </main>
      <Footer mode={mode} />
    </div>
  );
}
