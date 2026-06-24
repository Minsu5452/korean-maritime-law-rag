import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";

export function Footer({ mode }: { mode: Mode }) {
  return (
    <footer className="mx-auto mt-12 max-w-3xl border-t border-line px-5 py-7 text-xs leading-relaxed text-muted">
      <p className="text-ink-soft">
        참고용 의사결정 지원 도구입니다. 법적 효력이 없으며, 실제 적용 시{" "}
        <a
          href="https://www.law.go.kr"
          target="_blank"
          rel="noreferrer"
          className="font-medium text-brand hover:text-brand-strong"
        >
          국가법령정보센터
        </a>
        에서 최신 시행 법령을 확인하세요.
      </p>
      <p className="mt-2">
        {mode === "demo"
          ? "녹화 데모는 실제 실행한 질의·응답을 그대로 재생합니다 (백엔드·키 없이 동작)."
          : "라이브 모드는 로컬 FastAPI 백엔드(localhost:8000)에 직접 질의합니다. 백엔드 실행이 필요합니다."}
      </p>
      <p className="mt-2">
        Next.js · FastAPI · LangGraph · Qdrant · Neo4j · KURE-v1 ·{" "}
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-brand hover:text-brand-strong"
        >
          소스 코드
        </a>
      </p>
    </footer>
  );
}
