"use client";
import type { Mode } from "@/lib/types";

export function ModeToggle({
  mode,
  onMode,
}: {
  mode: Mode;
  onMode: (m: Mode) => void;
}) {
  return (
    <div
      role="group"
      aria-label="실행 모드"
      className="inline-flex rounded-[9px] bg-fill p-[3px]"
    >
      {(["demo", "live"] as const).map((m) => (
        <button
          key={m}
          type="button"
          onClick={() => onMode(m)}
          className={`inline-flex items-center gap-1.5 rounded-[7px] px-3 py-1.5 text-[13px] font-semibold leading-none transition ${
            mode === m ? "bg-surface text-ink shadow-sm" : "text-muted hover:text-ink-soft"
          }`}
        >
          {m === "demo" && <span className="h-1.5 w-1.5 rounded-full bg-brand" />}
          {m === "demo" ? "녹화 데모" : "라이브"}
        </button>
      ))}
    </div>
  );
}
