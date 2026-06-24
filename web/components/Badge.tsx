import type { ReactNode } from "react";

// KRDS 배지: 4px 라운드, 단색/옅은블루/회색. 강조는 정부 블루 하나로.
const TONES = {
  brand: "bg-brand text-white font-bold",
  brandSoft: "border border-brand bg-brand-soft text-brand-strong font-bold",
  meta: "bg-fill text-ink-soft",
  danger: "bg-danger text-white font-bold",
  warning: "bg-warning text-ink font-bold",
  success: "bg-success text-white font-bold",
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
      className={`inline-flex items-center gap-1 rounded px-2.5 py-1 text-[13px] ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
