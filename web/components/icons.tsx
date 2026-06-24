// 의존성을 늘리지 않으려 아이콘은 인라인 SVG로 둔다(lucide 스타일, currentColor).
type P = { className?: string };
const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export const IconRefuse = ({ className }: P) => (
  <svg {...base} className={className}><circle cx="12" cy="12" r="9" /><path d="m9 9 6 6M15 9l-6 6" /></svg>
);
export const IconChevron = ({ className }: P) => (
  <svg {...base} className={className}><path d="m6 9 6 6 6-6" /></svg>
);
export const IconExternal = ({ className }: P) => (
  <svg {...base} className={className}><path d="M14 5h5v5M19 5l-8 8M19 13v6H5V5h6" /></svg>
);
export const IconArrow = ({ className }: P) => (
  <svg {...base} className={className}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
);
export const IconDoc = ({ className }: P) => (
  <svg {...base} className={className}><path d="M14 3v5h5M7 3h8l5 5v11a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M9.5 13h5M9.5 16h3" /></svg>
);
export const IconGithub = ({ className }: P) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className}><path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.5 2.87 8.32 6.84 9.67.5.1.68-.22.68-.49l-.01-1.9c-2.78.62-3.37-1.2-3.37-1.2-.46-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.9 1.57 2.35 1.12 2.92.86.09-.66.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.7 0 0 .84-.28 2.75 1.05a9.34 9.34 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.4.2 2.44.1 2.7.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9l-.01 2.82c0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.26C22 6.58 17.52 2 12 2Z" /></svg>
);
