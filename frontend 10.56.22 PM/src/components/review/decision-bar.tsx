"use client";

import type { ReviewStatus } from "@/types/review";

type Props = {
  status: ReviewStatus;
  version: number;
  onApprove: () => void;
  onRework: () => void;
  onResubmit: () => void;
};

export function DecisionBar({ status, version, onApprove, onRework, onResubmit }: Props) {
  if (status === "approved") {
    return (
      <div className="m-4 mt-2 flex items-center gap-3 rounded-2xl bg-[#D9F5E3] px-4 py-3 text-[13px] text-[#15803D]">
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#16A34A] text-white">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round">
            <path d="m5 12 5 5 9-10" />
          </svg>
        </span>
        <span>
          <strong>Approved on v{version}.</strong> Edit it later and the post goes straight back to review.
        </span>
      </div>
    );
  }

  if (status === "rework") {
    return (
      <div className="p-4 pt-2">
        <button
          type="button"
          onClick={onResubmit}
          className="h-12 w-full rounded-2xl bg-[#251A14] text-[14px] font-semibold text-white transition hover:bg-black"
        >
          Resubmit as v{version + 1}
        </button>
      </div>
    );
  }

  const label = status === "internal" ? "Internal" : "Client";
  return (
    <div className="grid grid-cols-2 gap-3 p-4 pt-2">
      <button
        type="button"
        onClick={onApprove}
        className="flex h-12 items-center justify-center gap-2 rounded-2xl bg-[#16A34A] text-[14px] font-semibold text-white transition hover:bg-[#15803D]"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
          <path d="m5 12 5 5 9-10" />
        </svg>
        {label} approve
      </button>
      <button
        type="button"
        onClick={onRework}
        className="flex h-12 items-center justify-center gap-2 rounded-2xl border-2 border-[#D83A12] bg-white text-[14px] font-semibold text-[#D83A12] transition hover:bg-[#FFF1EC]"
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round">
          <path d="M6 6l12 12M18 6 6 18" />
        </svg>
        {label} rework
      </button>
    </div>
  );
}