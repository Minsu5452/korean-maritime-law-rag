import { REPO_URL } from "@/lib/constants";
import type { Mode } from "@/lib/types";

export function Footer({ mode }: { mode: Mode }) {
  return (
    <footer className="mt-8 bg-[#20262e] text-[#aeb6bf]">
      <div className="mx-auto w-full max-w-[1040px] px-5 py-6 text-xs leading-relaxed">
        <p className="text-[13px] font-bold text-[#e7eaee]">
          해양법령 길잡이 · 해양경찰청 현장 법령·벌칙 조회 시스템 (참고용)
        </p>
        <p className="mt-2">
          법령 원문 출처: 국가법령정보센터 OPEN API · 본 도구는 비영리 참고용이며 법적 효력이 없습니다.
          정확한 적용은 원문과 소관 부서 확인이 필요합니다.
        </p>
        <p className="mt-2">
          {mode === "demo"
            ? "녹화 데모는 실제 실행한 질의·응답을 그대로 재생합니다 (백엔드·키 없이 동작)."
            : "라이브 모드는 로컬 FastAPI 백엔드(localhost:8000)에 직접 질의합니다. 먼저 백엔드를 실행해야 합니다."}
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-white/10 pt-3">
          <span>해양 법령 105개 · 조문 단위 검색 · 근거 인용 · 인용 검증</span>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="font-bold text-[#9fb6e0] hover:text-white"
          >
            소스 코드 →
          </a>
        </div>
      </div>
    </footer>
  );
}
