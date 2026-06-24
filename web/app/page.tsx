"use client";
import { useEffect, useRef, useState } from "react";
import { AnswerCard } from "@/components/AnswerCard";
import { Badge } from "@/components/Badge";
import { EvidenceList } from "@/components/EvidenceList";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { QueryBar } from "@/components/QueryBar";
import { TraceTimeline } from "@/components/TraceTimeline";
import { DEFAULT_API_BASE } from "@/lib/constants";
import { STRATEGY_LABEL, TYPE_LABEL } from "@/lib/pipeline";
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
  const { response } = state;

  return (
    <div className="flex min-h-full flex-col">
      <Header mode={mode} onMode={onMode} />

      {/* 참고 고지 */}
      <div className="mx-auto w-full max-w-[1040px] px-5">
        <div className="mt-4 flex items-start gap-2 rounded-md border border-[#c9d8f5] border-l-4 border-l-brand bg-brand-soft px-3.5 py-2.5 text-[13px] leading-relaxed text-[#27406e]">
          <span className="font-extrabold text-brand">ⓘ</span>
          <span>
            이 시스템은 현장 <b className="font-bold">참고용</b>이며 법적 효력이 없습니다. 정확한 적용은{" "}
            <a
              href="https://www.law.go.kr"
              target="_blank"
              rel="noreferrer"
              className="font-bold text-brand-strong underline-offset-2 hover:underline"
            >
              국가법령정보센터
            </a>{" "}
            원문과 소관 부서 확인이 필요합니다.
          </span>
        </div>
      </div>

      <main className="mx-auto w-full max-w-[1040px] flex-1 px-5 pb-6 pt-5">
        <Hero />
        <div className="mt-5">
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
          <section className="mt-5 overflow-hidden rounded-md border border-line">
            <div className="flex flex-wrap items-center gap-2 border-b border-line bg-fill px-4 py-2.5">
              <span className="text-sm font-extrabold text-ink">조회 결과</span>
              {response && (
                <span className="ml-auto flex flex-wrap items-center gap-1.5">
                  <Badge tone="brandSoft">{TYPE_LABEL[response.query_type] ?? response.query_type}</Badge>
                  {response.strategy !== "none" && (
                    <Badge tone="meta">검색 {STRATEGY_LABEL[response.strategy] ?? response.strategy}</Badge>
                  )}
                  <Badge tone="meta">근거 {response.evidence.length}건</Badge>
                </span>
              )}
            </div>
            <div className="space-y-4 p-4 sm:p-5">
              <TraceTimeline
                seen={state.seen}
                activeStep={state.activeStep}
                response={state.response}
                running={state.phase === "running"}
              />
              <AnswerCard state={state} />
              {response && <EvidenceList items={response.evidence} />}
            </div>
          </section>
        ) : (
          <p className="mt-8 text-sm text-muted">
            예시 질의를 선택하면 답변 근거 도출 과정을 단계별로 보여줍니다.
          </p>
        )}
      </main>
      <Footer mode={mode} />
    </div>
  );
}
