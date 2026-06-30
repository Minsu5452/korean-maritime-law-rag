import type { ReactNode } from "react";
import type { CitedArticle } from "./types";

// 답변 본문에서 법령명(「…」 또는 'OO법' 접두)과 조문 번호(제N조…)를 찾아 인용 칩으로 만든다.
// 칩에 마우스를 올리면 같은 조문을 가리키는 근거 카드가 함께 강조된다.
const PATTERN =
  /(「[^」]+」|(?:[가-힣]+법(?:\s*시행령|\s*시행규칙)?\s*)?제\d+조(?:의\d+)?(?:제\d+항)?(?:제\d+호)?)/g;

interface CiteOptions {
  evidence?: CitedArticle[];
  activeDocId?: string | null;
  onHover?: (docId: string | null) => void;
}

// 인용 토큰을 근거 조문에 연결한다. 법령명이 토큰에 함께 있으면 그 법령으로 한정하고,
// 없으면 조문 번호만으로 매칭한다.
function resolveDocId(raw: string, evidence: CitedArticle[]): string | undefined {
  const art = raw.match(/제\d+조(?:의\d+)?/)?.[0];
  if (!art) return undefined;
  const byArticle = evidence.filter((e) => e.article_no === art);
  if (byArticle.length === 0) return undefined;
  const withLaw = byArticle.find((e) => raw.includes(e.law_name));
  return (withLaw ?? byArticle[0]).doc_id;
}

export function highlightCitations(text: string, opts: CiteOptions = {}): ReactNode[] {
  const { evidence = [], activeDocId = null, onHover } = opts;
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let match: RegExpExecArray | null;
  PATTERN.lastIndex = 0;

  while ((match = PATTERN.exec(text)) !== null) {
    if (match.index > last) out.push(text.slice(last, match.index));
    const raw = match[0];
    const linkedId = resolveDocId(raw, evidence) ?? null;
    const isActive = linkedId !== null && activeDocId === linkedId;
    const hasArticle = /제\d+조/.test(raw);
    out.push(
      <span
        key={key++}
        onMouseEnter={onHover && linkedId ? () => onHover(linkedId) : undefined}
        onMouseLeave={onHover && linkedId ? () => onHover(null) : undefined}
        className={[
          "mx-px inline-flex items-center gap-0.5 whitespace-nowrap rounded-chip border px-1.5 align-baseline font-semibold text-brand-strong transition",
          isActive
            ? "border-brand bg-[#dce9ff] shadow-[0_0_0_3px_rgba(49,130,246,0.12)]"
            : "border-transparent bg-brand-soft",
          linkedId ? "cursor-pointer hover:border-brand hover:bg-[#dce9ff]" : "",
        ].join(" ")}
      >
        {hasArticle && <span className="font-bold opacity-70">§</span>}
        {raw}
      </span>,
    );
    last = match.index + raw.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
