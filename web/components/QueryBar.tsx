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
    <div className="rounded-2xl border border-line bg-surface p-2 shadow-[0_1px_2px_rgba(15,23,42,0.04),0_12px_28px_-20px_rgba(15,23,42,0.25)]">
      <div className="flex items-center gap-2">
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
          className="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-[15px] text-ink placeholder:text-muted focus:outline-none disabled:cursor-default"
        />
        {!demo && (
          <button
            type="button"
            onClick={submitLive}
            disabled={running || !text.trim()}
            className="flex shrink-0 items-center gap-1.5 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-strong disabled:opacity-40"
          >
            질의
            <IconArrow className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="px-1 pb-1 pt-2">
        {traces.length > 0 && (
          <div className="mb-1.5 text-[11px] font-medium text-muted">자주 찾는 질의</div>
        )}
        <div className="flex flex-wrap gap-2">
          {traces.map((t) => (
            <button
              key={t.id}
              type="button"
              disabled={running}
              onClick={() => (demo ? onDemo(t) : (setText(t.question), onLive(t.question)))}
              className={`rounded-full border px-3 py-1.5 text-xs transition disabled:opacity-50 ${
                activeId === t.id
                  ? "border-brand bg-brand-soft text-brand-strong"
                  : "border-line bg-white text-ink-soft hover:border-slate-300"
              }`}
            >
              {t.question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
