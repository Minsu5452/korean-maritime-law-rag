"use client";
import { useEffect, useRef, useState } from "react";
import { AnswerCard } from "@/components/AnswerCard";
import { EvidenceList } from "@/components/EvidenceList";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { IconInfo } from "@/components/icons";
import { QueryBar } from "@/components/QueryBar";
import { TraceTimeline } from "@/components/TraceTimeline";
import { DEFAULT_API_BASE } from "@/lib/constants";
import type { DemoTrace, Mode } from "@/lib/types";
import { useRunner } from "@/lib/useRunner";

export default function Home() {
  const [mode, setMode] = useState<Mode>("demo");
  const [traces, setTraces] = useState<DemoTrace[]>([]);
  const [activeId, setActiveId] = useState<string | undefined>(undefined);
  const [linkedDoc, setLinkedDoc] = useState<string | null>(null);
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
    setLinkedDoc(null);
    runDemo(t);
  };
  const onLive = (q: string) => {
    setActiveId(undefined);
    setLinkedDoc(null);
    runLive(DEFAULT_API_BASE, q);
  };
  const onMode = (m: Mode) => {
    setMode(m);
    reset();
    setActiveId(undefined);
    setLinkedDoc(null);
  };

  const started = state.phase !== "idle";
  const { response } = state;

  return (
    <div className="flex min-h-full flex-col">
      <Header mode={mode} onMode={onMode} />

      {/* 참고 고지 */}
      <div id="disclaimer" className="mx-auto w-full max-w-[880px] px-5">
        <div className="mt-5 flex items-start gap-2.5 rounded-field border border-[#dce9ff] bg-brand-weak px-4 py-3 text-[13.5px] leading-relaxed text-ink-soft">
          <IconInfo className="mt-0.5 h-[18px] w-[18px] shrink-0 text-brand" />
          <span>
            이 시스템은 현장 <b className="font-semibold text-ink">참고용</b>이며 법적 효력이 없습니다.
            정확한 적용은{" "}
            <a
              href="https://www.law.go.kr"
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-brand-strong underline-offset-2 hover:underline"
            >
              국가법령정보센터
            </a>{" "}
            원문과 소관 부서 확인이 필요합니다.
          </span>
        </div>
      </div>

      <main className="mx-auto w-full max-w-[880px] flex-1 px-5 pb-8 pt-8">
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
          <section className="mt-9">
            <TraceTimeline
              seen={state.seen}
              activeStep={state.activeStep}
              response={state.response}
              running={state.phase === "running"}
            />
            <div className="mt-4">
              <AnswerCard state={state} activeDocId={linkedDoc} onHoverCite={setLinkedDoc} />
            </div>
            {response && (
              <div className="mt-7">
                <EvidenceList
                  items={response.evidence}
                  activeDocId={linkedDoc}
                  onHover={setLinkedDoc}
                />
              </div>
            )}
          </section>
        ) : (
          <p className="mt-8 text-[15px] text-muted">
            예시 질의를 선택하면 답변 근거 도출 과정을 단계별로 보여줍니다.
          </p>
        )}
      </main>
      <Footer mode={mode} />
    </div>
  );
}
