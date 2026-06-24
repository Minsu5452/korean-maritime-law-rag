"use client";
import { useState } from "react";
import { formatEnforceDate, lawGoKrUrl } from "@/lib/constants";
import { LAW_TYPE_TONE } from "@/lib/pipeline";
import type { CitedArticle } from "@/lib/types";
import { IconChevron, IconExternal } from "./icons";

export function EvidenceList({ items }: { items: CitedArticle[] }) {
  if (items.length === 0) return null;
  return (
    <section className="overflow-hidden rounded-md border border-line">
      <div className="flex items-center gap-2 border-b border-line bg-fill px-4 py-2.5">
        <span className="text-sm font-extrabold text-ink">근거 조문</span>
        <span className="rounded bg-brand px-1.5 py-0.5 text-[11px] font-bold text-white">
          {items.length}
        </span>
      </div>
      <div>
        {items.map((a) => (
          <EvidenceRow key={a.doc_id} article={a} />
        ))}
      </div>
    </section>
  );
}

function EvidenceRow({ article }: { article: CitedArticle }) {
  const [open, setOpen] = useState(false);
  const collapsible = article.text.length > 150;
  const enforceDate = formatEnforceDate(article.enforce_date);

  return (
    <div className="border-b border-line px-4 py-3.5 last:border-b-0">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span className="font-bold text-ink">{article.law_name}</span>
        <span className="font-bold text-brand-strong">{article.article_no}</span>
        {article.title && <span className="text-[14px] text-ink-soft">({article.title})</span>}
        <span className={`ml-auto shrink-0 rounded border px-1.5 py-0.5 text-[11px] ${LAW_TYPE_TONE}`}>
          {article.law_type}
        </span>
      </div>

      {article.text && (
        <>
          <p
            className={`mt-2 whitespace-pre-line text-[14px] leading-relaxed text-ink-soft ${
              open ? "" : "line-clamp-2"
            }`}
          >
            {article.text}
          </p>
          {collapsible && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              className="mt-1 inline-flex items-center gap-0.5 text-[12px] font-bold text-brand hover:text-brand-strong"
            >
              {open ? "접기" : "조문 본문 더 보기"}
              <IconChevron className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
            </button>
          )}
        </>
      )}

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-muted">
        {enforceDate && <span>{enforceDate} 시행</span>}
        <a
          href={lawGoKrUrl(article.law_name)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-0.5 font-bold text-brand hover:text-brand-strong"
        >
          국가법령정보센터 원문
          <IconExternal className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
}
