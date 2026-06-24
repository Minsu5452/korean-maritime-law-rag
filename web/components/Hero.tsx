export function Hero() {
  return (
    <div className="text-center">
      <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white/70 px-3 py-1 text-xs font-medium text-ink-soft">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        조문 단위 검색 · 근거 인용 · 인용 검증
      </span>
      <h1 className="mt-4 text-2xl font-bold tracking-tight text-ink sm:text-[32px]">
        해양 법령을 <span className="text-brand">근거 조문</span>과 함께 답합니다
      </h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-ink-soft sm:text-[15px]">
        BM25·벡터·조문 관계 그래프를 합쳐 검색하고, LangGraph 에이전트가 질문 분류 → 검색 → 근거
        평가 → 답변 생성 → 인용 검증을 거쳐 답합니다.
      </p>
    </div>
  );
}
