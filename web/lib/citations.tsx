import type { ReactNode } from "react";

// 답변 본문에서 법령명(「…」)과 조문 번호(제N조…)를 찾아 강조한다.
// 인용 카드와 시각적으로 이어 붙여, 답변이 어떤 조문을 근거로 했는지 바로 알아볼 수 있게 한다.
const PATTERN = /(「[^」]+」|제\d+조(?:의\d+)?(?:제\d+항)?(?:제\d+호)?)/g;

export function highlightCitations(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let match: RegExpExecArray | null;
  PATTERN.lastIndex = 0;

  while ((match = PATTERN.exec(text)) !== null) {
    if (match.index > last) out.push(text.slice(last, match.index));
    out.push(
      <span key={key++} className="font-semibold text-brand-strong">
        {match[0]}
      </span>,
    );
    last = match.index + match[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
