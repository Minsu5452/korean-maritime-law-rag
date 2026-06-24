"use client";
import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";
import { IconEmblem, IconExternal, IconGithub } from "./icons";
import { ModeToggle } from "./ModeToggle";

export function Header({ mode, onMode }: { mode: Mode; onMode: (m: Mode) => void }) {
  return (
    <div>
      {/* 정부 식별 띠 */}
      <div className="border-b border-line bg-surface">
        <div className="mx-auto flex h-[34px] max-w-[1040px] items-center justify-between px-5 text-xs">
          <div className="flex items-center gap-2 text-ink-soft">
            <IconEmblem className="h-[18px] w-[18px] text-brand" />
            <span className="font-bold">해양경찰청</span>
            <span className="hidden tracking-wide text-muted sm:inline">KOREA COAST GUARD</span>
          </div>
          <div className="flex items-center gap-3 text-ink-soft">
            <a
              href="https://www.law.go.kr"
              target="_blank"
              rel="noreferrer"
              className="hidden items-center gap-1 hover:text-brand sm:inline-flex"
            >
              국가법령정보센터
              <IconExternal className="h-3 w-3" />
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub 저장소"
              className="inline-flex items-center gap-1 hover:text-brand"
            >
              <IconGithub className="h-3.5 w-3.5" />
              GitHub
            </a>
          </div>
        </div>
      </div>

      {/* 워드마크 헤더 (정부 블루 식별선) */}
      <header className="border-b-2 border-brand bg-surface">
        <div className="mx-auto flex h-[72px] max-w-[1040px] items-center gap-3 px-5">
          <IconEmblem className="h-[42px] w-[42px] shrink-0 text-brand" />
          <div className="leading-tight">
            <div className="text-[21px] font-extrabold tracking-tight text-ink">해양법령 길잡이</div>
            <div className="mt-0.5 text-xs font-medium text-muted">
              해양경찰청 현장 법령·벌칙 조회 시스템
            </div>
          </div>
          <div className="ml-auto">
            <ModeToggle mode={mode} onMode={onMode} />
          </div>
        </div>
      </header>

      {/* 브레드크럼 */}
      <div className="border-b border-line bg-fill">
        <div className="mx-auto flex h-[38px] max-w-[1040px] items-center gap-1.5 px-5 text-xs text-muted">
          <span>홈</span>
          <span className="text-line-strong">›</span>
          <span className="font-bold text-ink-soft">현장 법령·벌칙 조회</span>
        </div>
      </div>
    </div>
  );
}
