import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";

export function Footer({ mode }: { mode: Mode }) {
  return (
    <footer className="mx-auto mt-12 max-w-3xl border-t border-line px-5 py-7 text-center text-xs leading-relaxed text-muted">
      <p>
        {mode === "demo"
          ? "녹화 데모는 scripts/ask.py로 실제 실행한 질의·응답을 그대로 재생합니다. 법률 자문이 아니라 RAG 구현 예시입니다."
          : "라이브 모드는 로컬 FastAPI 백엔드(localhost:8000)에 직접 질의합니다. 백엔드 실행이 필요합니다."}
      </p>
      <p className="mt-2">
        Next.js · FastAPI · LangGraph · Qdrant · Neo4j · KURE-v1 ·{" "}
        <a href={REPO_URL} target="_blank" rel="noreferrer" className="font-medium text-brand hover:text-brand-strong">
          소스 코드
        </a>
      </p>
    </footer>
  );
}
