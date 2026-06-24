"use client";
import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";
import { IconExternal, IconGithub } from "./icons";
import { ModeToggle } from "./ModeToggle";

export function Header({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <div className="border-b border-line">
      <div className="bg-fill">
        <div className="mx-auto flex h-8 max-w-[1040px] items-center px-5 text-xs text-muted">
          해양경찰청 현장 실무 지원 도구 · 참고용
        </div>
      </div>
      <header className="bg-surface">
        <div className="mx-auto flex h-16 max-w-[1040px] items-center gap-3 px-5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand text-[15px] font-bold text-white">
              해
            </span>
            <div className="leading-tight">
              <div className="text-[17px] font-bold text-ink">해양법령 길잡이</div>
              <div className="text-xs text-muted">해양경찰청 현장 실무 지원</div>
            </div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <ModeToggle mode={mode} onMode={onMode} />
            <a
              href="https://www.law.go.kr"
              target="_blank"
              rel="noreferrer"
              className="hidden items-center gap-1 rounded-md border border-line px-3 py-2 text-xs font-medium text-ink-soft transition hover:bg-fill sm:inline-flex"
            >
              국가법령정보센터
              <IconExternal className="h-3.5 w-3.5" />
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub 저장소"
              className="flex h-9 w-9 items-center justify-center rounded-md border border-line text-ink-soft transition hover:bg-fill"
            >
              <IconGithub className="h-4 w-4" />
            </a>
          </div>
        </div>
      </header>
    </div>
  );
}
