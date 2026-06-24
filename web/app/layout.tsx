import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "해양 법령 RAG — 근거 조문 인용 데모",
  description:
    "해양 법령을 조문 단위로 검색하고, 근거 조문을 인용해 답변하는 RAG 에이전트의 검색·생성 과정을 단계별로 보여주는 데모입니다.",
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
