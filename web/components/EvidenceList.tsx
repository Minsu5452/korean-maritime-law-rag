"use client";
import { useState } from "react";
import { formatEnforceDate, lawGoKrUrl } from "@/lib/constants";
import { LAW_TYPE_TONE } from "@/lib/pipeline";
import type { CitedArticle } from "@/lib/types";
import { IconChevron, IconExternal } from "./icons";

export function EvidenceList({
  items,
  activeDocId,
  onHover,
}: {
  items: CitedArticle[];
  activeDocId: string | null;
  onHover: (docId: string | null) => void;
}) {
  if (items.length === 0) return null;
  return (
    <section>
      <div className="mb-3.5 flex items-center gap-2">
        <span className="text-[16px] font-bold text-ink">근거 조문</span>
        <span className="rounded-full border border-line bg-fill px-2.5 py-0.5 text-[12.5px] font-semibold text-ink-soft">
          근거 {items.length}건
        </span>
      </div>
      <div className="space-y-3.5">
        {items.map((a) => (
          <EvidenceCard
            key={a.doc_id}
            article={a}
            linked={activeDocId === a.doc_id}
            onHover={onHover}
          />
        ))}
      </div>
    </section>
  );
}

function EvidenceCard({
  article,
  linked,
  onHover,
}: {
  article: CitedArticle;
  linked: boolean;
  onHover: (docId: string | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const collapsible = article.text.length > 150;
  const enforceDate = formatEnforceDate(article.enforce_date);

  return (
    <article
      onMouseEnter={() => onHover(article.doc_id)}
      onMouseLeave={() => onHover(null)}
      className={`group relative overflow-hidden rounded-card border bg-surface py-5 pl-6 pr-5 transition ${
        linked
          ? "-translate-y-0.5 border-[#d4e3ff] shadow-[0_0_0_3px_#eaf2ff,0_4px_16px_rgba(0,0,0,0.06)]"
          : "border-line shadow-sm hover:-translate-y-0.5 hover:border-[#d4e3ff] hover:shadow-pop"
      }`}
    >
      <span
        className={`absolute inset-y-3.5 left-0 w-[3px] rounded-full transition ${
          linked ? "bg-brand" : "bg-line-strong group-hover:bg-brand"
        }`}
      />

      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className="text-[18px] font-bold tracking-tight text-ink">{article.law_name}</span>
        <span className="text-[18px] font-bold tracking-tight text-brand-strong">
          {article.article_no}
        </span>
        {article.title && <span className="text-[14px] font-medium text-muted">{article.title}</span>}
      </div>

      <div className="mt-2.5 flex flex-wrap gap-1.5">
        <span className={`inline-flex items-center rounded-chip border px-2 py-0.5 text-[12px] ${LAW_TYPE_TONE}`}>
          {article.law_type}
        </span>
        {enforceDate && (
          <span className="inline-flex items-center gap-1.5 rounded-chip border border-line bg-fill px-2 py-0.5 text-[12px] text-ink-soft">
            <span className="h-[5px] w-[5px] rounded-full bg-muted" />
            {enforceDate} 시행
          </span>
        )}
      </div>

      {article.text && (
        <>
          <p
            className={`mt-3 whitespace-pre-line text-[14px] leading-relaxed text-ink-soft ${
              open ? "" : "line-clamp-2"
            }`}
          >
            {article.text}
          </p>
          {collapsible && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              className="mt-1.5 inline-flex items-center gap-0.5 text-[12px] font-semibold text-brand hover:text-brand-strong"
            >
              {open ? "접기" : "조문 본문 더 보기"}
              <IconChevron className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
            </button>
          )}
        </>
      )}

      <div className="mt-4">
        <a
          href={lawGoKrUrl(article.law_name)}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 rounded-control border border-line-strong bg-surface px-3.5 py-2 text-[13.5px] font-semibold text-brand-strong transition hover:border-brand hover:bg-brand-weak"
        >
          국가법령정보센터 원문
          <IconExternal className="h-3.5 w-3.5" />
        </a>
      </div>
    </article>
  );
}
