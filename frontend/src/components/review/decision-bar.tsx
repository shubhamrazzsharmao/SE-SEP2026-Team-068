"use client";

import { useState } from "react";
import { LuCheck, LuMessageSquareDiff, LuX } from "react-icons/lu";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Textarea } from "@/components/ui/fields";
import { approve, reject, requestChanges } from "@/lib/actions";
import type { ContentStatus } from "@/types/api";

type Props = {
  pieceId: number;
  versionNo: number;
  status: ContentStatus;
  rejectionReason: string | null;
  /** Caller is a reviewer of this campaign. */
  isReviewer: boolean;
  /** Caller created or edited the current version (backend forbids self-review). */
  selfReview: boolean;
  /** e.g. "Alex · Nov 24, 10:12 AM", shown on the approved banner. */
  approvedBy?: string;
};

/**
 * Review actions for one content piece. What it shows depends on the status:
 * pending -> approve / request changes / reject (reviewers only), approved -> green banner,
 * rejected -> red banner with the reason. The backend re-checks every rule.
 */
export function DecisionBar({ pieceId, versionNo, status, rejectionReason, isReviewer, selfReview, approvedBy }: Props) {
  const [mode, setMode] = useState<"idle" | "changes" | "reject">("idle");

  if (status === "approved") {
    return (
      <Banner tone="green" icon={<LuCheck size={13} strokeWidth={3.4} />}>
        <strong>Approved on v{versionNo}{approvedBy && ` by ${approvedBy}`}.</strong> Editing it later sends the piece back to review.
      </Banner>
    );
  }

  if (status === "rejected") {
    return (
      <Banner tone="red" icon={<LuX size={13} strokeWidth={3.4} />}>
        <strong>Rejected on v{versionNo}.</strong> {rejectionReason && <>Reason: &ldquo;{rejectionReason}&rdquo;. </>}Rejection is final.
      </Banner>
    );
  }

  if (status !== "pending_review") return null;

  if (!isReviewer) {
    return <Banner tone="muted">Waiting for a reviewer to approve v{versionNo}, request changes or reject it.</Banner>;
  }

  if (selfReview) {
    return <Banner tone="amber">You created or edited v{versionNo}, so another reviewer has to review it.</Banner>;
  }

  if (mode === "changes") {
    return (
      <ActionForm action={requestChanges.bind(null, pieceId, versionNo)} reset className="space-y-3">
        <Textarea label="What should change?" name="feedback" required minLength={5} maxLength={2000} autoFocus
          placeholder="Shorter, and lead with the date." hint="The AI writes one revised version of this piece." />
        <div className="flex gap-2">
          <SubmitButton variant="dark" pendingText="Revising…">Send feedback</SubmitButton>
          <CancelButton onClick={() => setMode("idle")} />
        </div>
      </ActionForm>
    );
  }

  if (mode === "reject") {
    return (
      <ActionForm action={reject.bind(null, pieceId, versionNo)} reset confirm="Rejecting is final. Continue?" className="space-y-3">
        <Textarea label="Why is it rejected?" name="reason" required minLength={10} maxLength={2000} autoFocus
          placeholder="Off-brand claim about results." hint="The creator sees this reason. At least 10 characters." />
        <div className="flex gap-2">
          <SubmitButton variant="danger" pendingText="Rejecting…">Reject v{versionNo}</SubmitButton>
          <CancelButton onClick={() => setMode("idle")} />
        </div>
      </ActionForm>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <ActionForm action={approve.bind(null, pieceId, versionNo)}>
        <SubmitButton variant="success" className="h-12 w-full" pendingText="Approving…">
          <LuCheck size={16} strokeWidth={2.6} /> Approve v{versionNo}
        </SubmitButton>
      </ActionForm>
      <button type="button" onClick={() => setMode("changes")}
        className="inline-flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-ink/15 bg-white text-sm font-semibold transition-colors hover:border-ink/40">
        <LuMessageSquareDiff size={16} /> Request changes
      </button>
      <button type="button" onClick={() => setMode("reject")}
        className="inline-flex h-12 items-center justify-center gap-2 rounded-xl border-2 border-red-600 bg-white text-sm font-semibold text-red-700 transition-colors hover:bg-red-50">
        <LuX size={16} strokeWidth={2.6} /> Reject
      </button>
    </div>
  );
}

const TONES = {
  green: { box: "bg-green-50 text-green-800", dot: "bg-green-600" },
  red: { box: "bg-red-50 text-red-800", dot: "bg-red-600" },
  amber: { box: "bg-amber-50 text-amber-800", dot: "bg-amber-500" },
  muted: { box: "bg-paper text-muted", dot: "bg-muted" },
};

function Banner({ tone, icon, children }: { tone: keyof typeof TONES; icon?: React.ReactNode; children: React.ReactNode }) {
  const t = TONES[tone];
  return (
    <div className={`flex items-start gap-3 rounded-2xl px-4 py-3 text-sm ${t.box}`}>
      {icon && <span className={`mt-px flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-white ${t.dot}`}>{icon}</span>}
      <p>{children}</p>
    </div>
  );
}

function CancelButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" onClick={onClick} className="rounded-xl px-4 py-2.5 text-sm font-medium text-muted hover:text-ink">
      Cancel
    </button>
  );
}
