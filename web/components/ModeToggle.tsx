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
    <div className="inline-flex rounded-full border border-line bg-slate-50 p-0.5 text-xs">
      {(["demo", "live"] as const).map((m) => (
        <button
          key={m}
          type="button"
          onClick={() => onMode(m)}
          className={`rounded-full px-3 py-1.5 font-medium transition ${
            mode === m
              ? "bg-white text-ink shadow-sm"
              : "text-muted hover:text-ink-soft"
          }`}
        >
          {m === "demo" ? "녹화 데모" : "라이브"}
        </button>
      ))}
    </div>
  );
}
