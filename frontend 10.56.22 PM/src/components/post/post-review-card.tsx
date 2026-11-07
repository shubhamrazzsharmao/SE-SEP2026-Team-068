"use client";

import { useState } from "react";
import type { Platform, ReviewPost, ReviewStatus } from "@/types/review";

const BODY_LIMIT = 230;

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join("");
}

function PlatformIcon({ platform }: { platform: Platform }) {
  if (platform === "linkedin") return <span className="text-[9px] font-extrabold leading-none">in</span>;
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
    </svg>
  );
}

const STATUS: Record<ReviewStatus, { label: string; cls: string }> = {
  internal: { label: "In internal review", cls: "bg-[#FFE7DF] text-[#D83A12]" },
  rework: { label: "Rework requested", cls: "bg-[#FFF1CC] text-[#9A6700]" },
  client: { label: "Waiting on client", cls: "bg-[#E3E6F8] text-[#4A55A8]" },
  approved: { label: "Approved", cls: "bg-[#D9F5E3] text-[#15803D]" },
};

export function StatusBadge({ status, version }: { status: ReviewStatus; version?: number }) {
  const s = STATUS[status];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ${s.cls}`}>
      {s.label}
      {status === "approved" && version ? ` · v${version}` : ""}
    </span>
  );
}

function PostArt({ palette, platform }: { palette: string[]; platform: Platform }) {
  const filler = ["#EFE4D4", "#E8DCCB", "#F3E9DC", ...palette.slice(3)];
  return (
    <div aria-hidden className="grid h-[250px] grid-cols-6 grid-rows-4 gap-1.5 bg-[#F3E9DC] p-4">
      <div
        className="col-span-2 row-span-2 flex items-center justify-center rounded-xl text-white"
        style={{ background: palette[0], gridColumn: "1 / span 2", gridRow: "1 / span 2" }}
      >
        <PlatformIcon platform={platform} />
      </div>
      <div className="col-span-2 rounded-xl" style={{ background: palette[2], gridColumn: "4 / span 2", gridRow: "1" }} />
      <div className="rounded-xl" style={{ background: palette[4], gridColumn: "6", gridRow: "2" }} />
      <div className="rounded-xl" style={{ background: palette[1], gridColumn: "3", gridRow: "3" }} />
      <div className="col-span-2 row-span-2 rounded-xl" style={{ background: palette[4], gridColumn: "5 / span 2", gridRow: "3 / span 2", opacity: 0.7 }} />
      {Array.from({ length: 14 }).map((_, i) => (
        <div key={i} className="rounded-xl opacity-70" style={{ background: filler[i % filler.length] }} />
      ))}
    </div>
  );
}

export function PostReviewCard({ post }: { post: ReviewPost }) {
  const [expanded, setExpanded] = useState(false);
  const long = post.body.length > BODY_LIMIT;
  const text = expanded || !long ? post.body : post.body.slice(0, BODY_LIMIT).trimEnd() + "…";

  return (
    <article className="overflow-hidden rounded-[22px] border border-[#E6DCCD] bg-white shadow-[0_14px_40px_-24px_rgba(37,26,20,0.35)]">
      <div className="flex items-start gap-3 p-5 pb-0">
        <div className="relative">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#E8DCCB] text-[13px] font-bold text-[#6B5B4E]">
            {initials(post.client)}
          </span>
          <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-[#251A14] text-white ring-2 ring-white">
            <PlatformIcon platform={post.platform} />
          </span>
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-[16px] font-bold text-[#251A14]">{post.client}</h2>
          <p className="text-[12px] text-[#8A7B6D]">
            {post.createdAt} · v{post.version}
          </p>
        </div>
        <StatusBadge status={post.status} version={post.version} />
      </div>

      <div className="px-5 pb-4 pt-4 text-[14px] leading-relaxed text-[#251A14]">
        <p className="mb-2 font-semibold">{post.title}</p>
        <p className="whitespace-pre-line">{text}</p>
        {long && (
          <button type="button" onClick={() => setExpanded((e) => !e)} className="mt-1 font-medium text-[#D83A12] hover:underline">
            {expanded ? "Show less" : "Show more"}
          </button>
        )}
      </div>

      <PostArt palette={post.palette} platform={post.platform} />
    </article>
  );
}