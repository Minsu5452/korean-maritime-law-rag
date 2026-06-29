export function Hero() {
  return (
    <div>
      <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-soft px-2.5 py-1 text-[13px] font-semibold text-brand-strong">
        <span className="h-[5px] w-[5px] rounded-full bg-brand" />
        해양경찰청 현장 법령 지원
      </span>
      <h1 className="mt-4 text-[28px] font-bold leading-[1.28] tracking-[-0.02em] text-ink sm:text-[34px]">
        법령 근거, 조문으로 바로 확인하세요
      </h1>
      <p className="mt-3 max-w-[640px] text-[17px] leading-relaxed text-ink-soft">
        상황이나 조문을 입력하면 적용 법령과 벌칙을 근거 조문·시행일과 함께 보여줍니다.
      </p>
    </div>
  );
}
