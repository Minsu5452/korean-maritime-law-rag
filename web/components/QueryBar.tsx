"use client";
import { useState } from "react";
import type { DemoTrace, Mode } from "@/lib/types";
import { IconArrow, IconSearch } from "./icons";

interface Props {
  mode: Mode;
  traces: DemoTrace[];
  running: boolean;
  question: string;
  activeId?: string;
  onDemo: (trace: DemoTrace) => void;
  onLive: (query: string) => void;
}

export function QueryBar({ mode, traces, running, question, activeId, onDemo, onLive }: Props) {
  const [text, setText] = useState("");
  const demo = mode === "demo";

  const submitLive = () => {
    const q = text.trim();
    if (q && !running) onLive(q);
  };

  return (
    <div>
      <div className="group flex h-[60px] items-center gap-1 rounded-field border border-line-strong bg-surface pl-4 pr-2 transition focus-within:border-brand focus-within:shadow-[0_0_0_4px_rgba(49,130,246,0.18)]">
        <IconSearch className="h-[22px] w-[22px] shrink-0 text-muted transition group-focus-within:text-brand" />
        <input
          value={demo ? question : text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submitLive();
          }}
          disabled={demo || running}
          placeholder={
            demo
              ? "예시 상황을 선택하세요"
              : "상황이나 조문을 입력하세요 (예: 어선에 무선설비가 없을 때 벌칙)"
          }
          className="h-full min-w-0 flex-1 bg-transparent px-3 text-[17px] font-medium text-ink placeholder:font-normal placeholder:text-muted focus:outline-none disabled:cursor-default"
        />
        {!demo && (
          <button
            type="button"
            onClick={submitLive}
            disabled={running || !text.trim()}
            className="flex h-[46px] shrink-0 items-center gap-1.5 rounded-control bg-brand px-5 text-[15.5px] font-semibold text-white transition hover:bg-brand-strong disabled:opacity-40"
          >
            검색
            <IconArrow className="h-4 w-4" />
          </button>
        )}
      </div>

      {traces.length > 0 && (
        <div className="mt-5">
          <div className="mb-2.5 text-[13px] font-semibold text-muted">추천 질문</div>
          <div className="flex flex-wrap gap-2.5">
            {traces.map((t) => (
              <button
                key={t.id}
                type="button"
                disabled={running}
                onClick={() => {
                  if (demo) {
                    onDemo(t);
                    return;
                  }
                  setText(t.question);
                  onLive(t.question);
                }}
                className={`rounded-full border px-4 py-2.5 text-left text-[14px] leading-snug transition disabled:opacity-50 ${
                  activeId === t.id
                    ? "border-brand bg-brand-soft font-semibold text-brand-strong"
                    : "border-line-strong bg-surface text-ink-soft hover:border-brand hover:bg-brand-weak hover:text-brand-strong"
                }`}
              >
                {t.question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
