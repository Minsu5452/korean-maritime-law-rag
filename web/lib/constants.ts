export const REPO_URL = "https://github.com/Minsu5452/korean-maritime-law-rag";

// 국가법령정보센터 법령 원문 링크(법령명 기준).
export const lawGoKrUrl = (lawName: string) =>
  `https://www.law.go.kr/법령/${encodeURIComponent(lawName)}`;

// YYYYMMDD → "YYYY.MM.DD".
export const formatEnforceDate = (yyyymmdd?: string | null) =>
  yyyymmdd && yyyymmdd.length === 8
    ? `${yyyymmdd.slice(0, 4)}.${yyyymmdd.slice(4, 6)}.${yyyymmdd.slice(6, 8)}`
    : null;

// 라이브 모드가 호출할 백엔드. 배포 빌드 시 NEXT_PUBLIC_API_BASE로 덮어쓴다.
export const DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
