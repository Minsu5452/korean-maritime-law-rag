import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "해양법령 길잡이 — 해양경찰청 현장 법령 조회",
  description:
    "현장 상황에 적용되는 해양 법령과 벌칙을 근거 조문·시행일과 함께 확인하는 의사결정 지원 도구입니다.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
