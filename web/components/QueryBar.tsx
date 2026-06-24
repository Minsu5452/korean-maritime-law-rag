"use client";
import { useState } from "react";
import type { DemoTrace, Mode } from "@/lib/types";
import { IconArrow } from "./icons";

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
      <div className="flex gap-2">
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
          className="h-14 min-w-0 flex-1 rounded-lg border border-line-strong bg-surface px-4 text-[17px] text-ink placeholder:text-muted focus:border-brand focus:outline-none focus:ring-4 focus:ring-brand/15 disabled:cursor-default disabled:bg-fill"
        />
        {!demo && (
          <button
            type="button"
            onClick={submitLive}
            disabled={running || !text.trim()}
            className="flex h-14 shrink-0 items-center gap-1.5 rounded-lg bg-brand px-6 text-[17px] font-bold text-white transition hover:bg-brand-strong disabled:opacity-40"
          >
            검색
            <IconArrow className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="mt-3.5 flex flex-wrap items-center gap-2">
        {traces.length > 0 && <span className="mr-1 text-xs text-muted">자주 찾는 질의</span>}
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
            className={`rounded-md border px-3 py-2 text-[15px] transition disabled:opacity-50 ${
              activeId === t.id
                ? "border-brand bg-brand-soft font-bold text-brand-strong"
                : "border-line bg-surface text-ink-soft hover:bg-fill"
            }`}
          >
            {t.question}
          </button>
        ))}
      </div>
    </div>
  );
}
