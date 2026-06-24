"use client";
import { useState } from "react";
import { formatEnforceDate, lawGoKrUrl } from "@/lib/constants";
import { LAW_TYPE_TONE } from "@/lib/pipeline";
import type { CitedArticle } from "@/lib/types";
import { IconChevron, IconDoc, IconExternal } from "./icons";

export function EvidenceList({ items }: { items: CitedArticle[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <div className="mb-2.5 flex items-center gap-2">
        <IconDoc className="h-4 w-4 text-brand" />
        <span className="text-sm font-semibold text-ink">근거 조문</span>
        <span className="rounded-full bg-brand-soft px-2 py-0.5 text-xs font-semibold text-brand">
          {items.length}
        </span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((a) => (
          <EvidenceCard key={a.doc_id} article={a} />
        ))}
      </div>
    </div>
  );
}

function EvidenceCard({ article }: { article: CitedArticle }) {
  const [open, setOpen] = useState(false);
  const tone = LAW_TYPE_TONE[article.law_type] ?? "bg-slate-50 text-slate-600 border-slate-200";
  const collapsible = article.text.length > 150;
  const enforceDate = formatEnforceDate(article.enforce_date);

  return (
    <div className="group rounded-xl border border-line bg-surface p-4 transition-shadow hover:shadow-[0_10px_24px_-18px_rgba(15,23,42,0.4)]">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-ink">{article.law_name}</span>
            <span className="font-semibold text-brand-strong">{article.article_no}</span>
          </div>
          {article.title && (
            <div className="mt-0.5 text-sm text-ink-soft">{article.title}</div>
          )}
        </div>
        <span className={`shrink-0 rounded-md border px-1.5 py-0.5 text-[11px] font-medium ${tone}`}>
          {article.law_type}
        </span>
      </div>

      {article.text && (
        <>
          <p
            className={`mt-2.5 whitespace-pre-line text-[13px] leading-relaxed text-ink-soft ${
              open ? "" : "line-clamp-3"
            }`}
          >
            {article.text}
          </p>
          {collapsible && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              className="mt-1.5 inline-flex items-center gap-0.5 text-xs font-medium text-brand hover:text-brand-strong"
            >
              {open ? "접기" : "조문 본문 더 보기"}
              <IconChevron className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
            </button>
          )}
        </>
      )}

      <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-line pt-2 text-[11px] text-muted">
        {enforceDate && <span>{enforceDate} 시행</span>}
        <a
          href={lawGoKrUrl(article.law_name)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-0.5 font-medium text-brand hover:text-brand-strong"
        >
          국가법령정보센터 원문
          <IconExternal className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
}
