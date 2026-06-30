"use client";
import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";
import { IconGithub, IconLogo } from "./icons";
import { ModeToggle } from "./ModeToggle";

export function Header({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/85 backdrop-blur-md backdrop-saturate-150">
      <div className="mx-auto flex h-[60px] max-w-[880px] items-center gap-3 px-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-[38px] w-[38px] shrink-0 items-center justify-center rounded-control bg-gradient-to-b from-[#3a8bff] to-brand text-white shadow-[0_2px_6px_rgba(49,130,246,0.28)]">
            <IconLogo className="h-6 w-6" />
          </div>
          <div className="leading-tight">
            <div className="text-[17px] font-bold tracking-tight text-ink">해양법령 길잡이</div>
            <div className="mt-px text-[11.5px] font-medium text-muted">해양 법령 근거 검색</div>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2.5">
          <ModeToggle mode={mode} onMode={onMode} />
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub 저장소"
            className="flex h-[38px] w-[38px] items-center justify-center rounded-control text-muted transition hover:bg-fill hover:text-ink"
          >
            <IconGithub className="h-5 w-5" />
          </a>
        </div>
      </div>
    </header>
  );
}
