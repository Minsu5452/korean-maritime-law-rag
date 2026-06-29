import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";

export function Footer({ mode }: { mode: Mode }) {
  return (
    <footer className="mt-12 border-t border-line bg-surface">
      <div className="mx-auto flex w-full max-w-[880px] flex-col gap-2.5 px-5 py-6">
        <div className="flex flex-wrap items-center gap-2 text-[13.5px]">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-ink-soft transition hover:text-brand-strong"
          >
            소스 코드
          </a>
          <span className="text-line-strong">·</span>
          <a
            href="https://www.law.go.kr"
            target="_blank"
            rel="noreferrer"
            className="font-medium text-ink-soft transition hover:text-brand-strong"
          >
            국가법령정보센터
          </a>
          <span className="text-line-strong">·</span>
          <a href="#disclaimer" className="font-medium text-ink-soft transition hover:text-brand-strong">
            면책 고지
          </a>
        </div>
        <p className="text-[12.5px] leading-relaxed text-muted">
          법령 원문 출처: 국가법령정보센터 OPEN API · 본 도구는 비영리 참고용이며 법적 효력이 없습니다.
          정확한 적용은 원문과 소관 부서 확인이 필요합니다.
        </p>
        <p className="text-[12.5px] leading-relaxed text-muted">
          {mode === "demo"
            ? "녹화 데모는 실제 실행한 질의·응답을 그대로 재생합니다 (백엔드·키 없이 동작)."
            : "라이브 모드는 로컬 FastAPI 백엔드(localhost:8000)에 직접 질의합니다. 먼저 백엔드를 실행해야 합니다."}
        </p>
      </div>
    </footer>
  );
}
