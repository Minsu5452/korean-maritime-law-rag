import type { NextConfig } from "next";

// 정적 내보내기(out/)로 빌드해 백엔드 없이 데모를 호스팅한다(Vercel/GitHub Pages).
// 라이브 모드는 빌드와 무관하게 브라우저에서 NEXT_PUBLIC_API_BASE로 직접 호출한다.
const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
