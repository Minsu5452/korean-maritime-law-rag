import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";

export function Footer({ mode }: { mode: Mode }) {
  return (
    <div className="mx-auto w-full max-w-[1040px] px-5">
      <div className="mt-6 rounded-md border border-line border-l-[3px] border-l-brand bg-fill px-4 py-3.5 text-sm leading-relaxed text-ink-soft">
        <b className="text-ink">참고용 의사결정 지원 도구입니다.</b> 법적 효력이 없으며, 실제 적용 시{" "}
        <a
          href="https://www.law.go.kr"
          target="_blank"
          rel="noreferrer"
          className="font-bold text-brand hover:text-brand-strong"
        >
          국가법령정보센터
        </a>
        에서 최신 시행 법령을 확인하세요.
      </div>
      <footer className="mt-6 border-t border-line py-6 text-xs leading-relaxed text-muted">
        <p>
          {mode === "demo"
            ? "녹화 데모는 실제 실행한 질의·응답을 그대로 재생합니다 (백엔드·키 없이 동작)."
            : "라이브 모드는 로컬 FastAPI 백엔드(localhost:8000)에 직접 질의합니다. 백엔드 실행이 필요합니다."}
        </p>
        <p className="mt-1.5">
          해양 법령 105개 · 조문 단위 검색 · 근거 인용 · 인용 검증 ·{" "}
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="font-bold text-brand hover:text-brand-strong"
          >
            소스 코드
          </a>
        </p>
      </footer>
    </div>
  );
}
