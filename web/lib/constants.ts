export const REPO_URL = "https://github.com/Minsu5452/korean-maritime-law-rag";

// 라이브 모드가 호출할 백엔드. 배포 빌드 시 NEXT_PUBLIC_API_BASE로 덮어쓴다.
export const DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
