export function Hero() {
  return (
    <div>
      <h1 className="flex items-center gap-2 text-[22px] font-extrabold tracking-tight text-ink">
        <span className="h-[18px] w-1 rounded-sm bg-brand" />
        법령·벌칙 조회
      </h1>
      <p className="mt-1.5 pl-3 text-[15px] text-ink-soft">
        상황이나 조문을 입력하면 적용 법령과 벌칙을 근거 조문·시행일과 함께 보여줍니다.
      </p>
    </div>
  );
}
