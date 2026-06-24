"use client";
import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";
import { IconGithub, IconGraph } from "./icons";
import { ModeToggle } from "./ModeToggle";

export function Header({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <header className="sticky top-0 z-20 border-b border-line/70 bg-white/70 backdrop-blur-md">
      <div className="mx-auto flex max-w-3xl items-center gap-3 px-5 py-3">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-sm">
            <IconGraph className="h-5 w-5" />
          </span>
          <div className="leading-tight">
            <div className="text-sm font-semibold text-ink">해양법령 길잡이</div>
            <div className="text-[11px] text-muted">해양경찰청 현장 실무 지원</div>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <ModeToggle mode={mode} onMode={onMode} />
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub 저장소"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-line text-ink-soft transition hover:bg-slate-50 hover:text-ink"
          >
            <IconGithub className="h-4 w-4" />
          </a>
        </div>
      </div>
    </header>
  );
}
