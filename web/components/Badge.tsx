import type { ReactNode } from "react";

// 상태 배지: 부드러운 색 칩으로 상태를 표시한다. 강조는 브랜드 블루 하나로 절제한다.
const TONES = {
  brand: "bg-brand text-white",
  brandSoft: "bg-brand-soft text-brand-strong",
  meta: "bg-fill text-ink-soft",
  danger: "bg-[#feecec] text-danger",
  warning: "bg-[#fff4e3] text-[#a85a00]",
  success: "bg-[#e7f7ef] text-[#0e9f5e]",
} as const;

export function Badge({
  tone = "meta",
  children,
  className = "",
}: {
  tone?: keyof typeof TONES;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-chip px-2.5 py-1 text-[12.5px] font-semibold ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
