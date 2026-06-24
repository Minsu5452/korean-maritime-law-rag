export function Hero() {
  return (
    <div className="text-center">
      <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white/70 px-3 py-1 text-xs font-medium text-ink-soft">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        현장 법령·벌칙 조회
      </span>
      <h1 className="mt-4 text-2xl font-bold tracking-tight text-ink sm:text-[30px]">
        상황에 맞는 해양 법령을 <span className="text-brand">근거 조문</span>과 함께 확인하세요
      </h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-ink-soft sm:text-[15px]">
        선박 안전·어선·해상교통·해양사고·수상레저 등 105개 해양 법령을 조문 단위로 검색하고,
        답변마다 근거 조문과 시행일을 함께 제시합니다.
      </p>
    </div>
  );
}
