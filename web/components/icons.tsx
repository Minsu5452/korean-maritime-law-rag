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
export const IconSearch = ({ className }: P) => (
  <svg {...base} strokeWidth={2} className={className}><circle cx="11" cy="11" r="7" /><path d="M21 21l-3.5-3.5" /></svg>
);
export const IconInfo = ({ className }: P) => (
  <svg {...base} className={className}><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><circle cx="12" cy="7.8" r="1" fill="currentColor" stroke="none" /></svg>
);
export const IconCheck = ({ className }: P) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12.5l4.5 4.5L19 7" /></svg>
);
export const IconClock = ({ className }: P) => (
  <svg {...base} className={className}><circle cx="12" cy="12" r="9" /><path d="M12 8v4l2.5 2.5" /></svg>
);
export const IconGithub = ({ className }: P) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className}><path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.5 2.87 8.32 6.84 9.67.5.1.68-.22.68-.49l-.01-1.9c-2.78.62-3.37-1.2-3.37-1.2-.46-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.9 1.57 2.35 1.12 2.92.86.09-.66.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.7 0 0 .84-.28 2.75 1.05a9.34 9.34 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.4.2 2.44.1 2.7.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9l-.01 2.82c0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.26C22 6.58 17.52 2 12 2Z" /></svg>
);

// 브랜드 로고: 물결 위의 길잡이 별(해양 길잡이 모티프). 공식 로고가 아닌 데모용 도형.
export const IconLogo = ({ className }: P) => (
  <svg viewBox="0 0 28 28" fill="none" className={className}>
    <path d="M14 5 L15.5 9 L19.3 10 L15.5 11 L14 15.5 L12.5 11 L8.7 10 L12.5 9 Z" fill="currentColor" />
    <path d="M5.6 19 q2.1 -2.1 4.2 0 t4.2 0 t4.2 0" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" fill="none" />
    <path d="M5.6 22.6 q2.1 -2.1 4.2 0 t4.2 0 t4.2 0" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" fill="none" opacity={0.6} />
  </svg>
);

// 답변 근거 도출 단계 아이콘.
export const IconSparkle = ({ className }: P) => (
  <svg {...base} className={className}><path d="M12 3.5 13.7 8.3 18.5 10 13.7 11.7 12 16.5 10.3 11.7 5.5 10 10.3 8.3Z" /><path d="M18.5 16.5l.9 2.4 2.4.9-2.4.9-.9 2.4-.9-2.4-2.4-.9 2.4-.9Z" strokeWidth={1.4} /></svg>
);
export const IconDocSearch = ({ className }: P) => (
  <svg {...base} className={className}><path d="M6 3h7l5 5v6.5" /><path d="M13 3v5h5" /><path d="M8 12h4M8 15.5h3" /><circle cx="15.5" cy="17.5" r="3" /><path d="M17.8 19.8 20.5 22.5" /></svg>
);
export const IconDocCheck = ({ className }: P) => (
  <svg {...base} className={className}><path d="M7 3h7l4 4v14H7z" /><path d="M14 3v4h4" /><path d="M9.5 13.5l2 2 3.5-4" /></svg>
);
export const IconPen = ({ className }: P) => (
  <svg {...base} className={className}><path d="M16.5 4.5l3 3L9 18l-4 1 1-4z" /><path d="M14.5 6.5l3 3" /></svg>
);
export const IconShieldCheck = ({ className }: P) => (
  <svg {...base} className={className}><path d="M12 3l7 2.5v5c0 4.4-2.9 7.6-7 9-4.1-1.4-7-4.6-7-9v-5z" /><path d="M9 12l2.2 2.2L15.5 9.8" /></svg>
);
