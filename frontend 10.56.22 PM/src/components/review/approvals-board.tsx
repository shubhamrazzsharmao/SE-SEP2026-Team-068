"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { PostReviewCard } from "@/components/post/post-review-card";
import { CommentThread } from "@/components/review/comment-thread";
import { DecisionBar } from "@/components/review/decision-bar";
import { MOCK_REVIEWS } from "@/mocks/reviews";
import type { ReviewComment, ReviewPost } from "@/types/review";

type Tab = "internal" | "client" | "approved";

const TABS: { id: Tab; label: string; tone: string }[] = [
  { id: "internal", label: "Internal", tone: "#FF4F26" },
  { id: "client", label: "Client", tone: "#5C6AC4" },
  { id: "approved", label: "Approved", tone: "#16A34A" },
];

const EMPTY: Record<Tab, string> = {
  internal: "Nothing waiting on the team. New drafts show up here.",
  client: "Nothing is with the client right now.",
  approved: "No approved posts yet. Approved posts collect here.",
};

const uid = () => `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
const now = () => new Date().toLocaleString("en-GB", { day: "numeric", month: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
const system = (body: string): ReviewComment => ({ id: uid(), author: "System", role: "system", time: now(), body });

function tabOf(p: ReviewPost): Tab {
  if (p.status === "approved") return "approved";
  if (p.status === "client") return "client";
  return "internal"; // internal + rework
}

export function ApprovalsBoard() {
  // TODO: replace with a TanStack Query hook (useReviews) once the API exists.
  const [posts, setPosts] = useState<ReviewPost[]>(MOCK_REVIEWS);
  const [tab, setTab] = useState<Tab>("internal");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  const groups = useMemo(() => {
    const g: Record<Tab, ReviewPost[]> = { internal: [], client: [], approved: [] };
    posts.forEach((p) => g[tabOf(p)].push(p));
    return g;
  }, [posts]);

  const visible = groups[tab];
  const selected = visible.find((p) => p.id === selectedId) ?? visible[0];
  const approvedCount = groups.approved.length;

  function flash(msg: string) {
    setNotice(msg);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setNotice(null), 3200);
  }

  function change(id: string, fn: (p: ReviewPost) => ReviewPost) {
    setPosts((all) => all.map((p) => (p.id === id ? fn(p) : p)));
  }

  function comment(p: ReviewPost, body: string) {
    change(p.id, (x) => ({ ...x, comments: [...x.comments, { id: uid(), author: "Sarah", role: "team", time: now(), body }] }));
  }

  function approve(p: ReviewPost) {
    if (p.status === "internal") {
      change(p.id, (x) => ({ ...x, status: "client", comments: [...x.comments, system(`Internal approved v${x.version}. Sent to the client.`)] }));
      flash("Internal approved. Moved to Client.");
    } else {
      change(p.id, (x) => ({ ...x, status: "approved", comments: [...x.comments, system(`Client approved v${x.version}.`)] }));
      flash(`1 post approved · ${approvedCount + 1} of ${posts.length} done`);
    }
  }

  function rework(p: ReviewPost) {
    const who = p.status === "client" ? "Client" : "Internal";
    change(p.id, (x) => ({ ...x, status: "rework", comments: [...x.comments, system(`${who} rework requested on v${x.version}.`)] }));
    setTab("internal");
    flash("Rework requested. Back with the creator.");
  }

  function resubmit(p: ReviewPost) {
    change(p.id, (x) => ({
      ...x,
      status: "internal",
      version: x.version + 1,
      comments: [...x.comments, system(`Resubmitted as v${x.version + 1}.`)],
    }));
    flash(`Resubmitted as v${p.version + 1}.`);
  }

  return (
    <section className="mx-auto w-full max-w-[1080px] px-5 pb-24 pt-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[12px] font-semibold uppercase tracking-[0.2em] text-[#FF4F26]">Reviews</p>
          <h1 className="mt-2 font-display text-[clamp(28px,4vw,40px)] font-extrabold uppercase leading-none tracking-tight text-[#251A14]">
            Pending approvals
          </h1>
        </div>
        <button
          type="button"
          className="flex h-10 items-center gap-2 rounded-full bg-[#251A14] px-4 text-[13px] font-semibold text-white transition hover:bg-black"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="9" cy="8" r="3.2" />
            <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M19 8v6M16 11h6" />
          </svg>
          Invite user
        </button>
      </div>

      {/* approved summary */}
      <div className="mt-6 flex flex-wrap items-center gap-4 rounded-2xl border border-[#E6DCCD] bg-white/70 px-5 py-4">
        <p className="text-[14px] text-[#251A14]">
          <strong className="font-display text-[20px] font-extrabold text-[#16A34A]">{approvedCount}</strong>{" "}
          {approvedCount === 1 ? "post approved" : "posts approved"} <span className="text-[#8A7B6D]">of {posts.length}</span>
        </p>
        <div className="flex min-w-[160px] flex-1 gap-1.5" aria-hidden>
          {posts.map((_, i) => (
            <span key={i} className="h-2 flex-1 rounded-full transition-colors duration-500" style={{ background: i < approvedCount ? "#16A34A" : "#E6DCCD" }} />
          ))}
        </div>
      </div>

      {/* tabs */}
      <div role="tablist" className="mt-6 flex gap-2 border-b border-[#E6DCCD]">
        {TABS.map((t) => {
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              role="tab"
              aria-selected={active}
              type="button"
              onClick={() => {
                setTab(t.id);
                setSelectedId(null);
              }}
              className={`-mb-px flex items-center gap-2 border-b-2 px-4 pb-3 pt-2 text-[14px] font-medium transition ${
                active ? "border-[#251A14] text-[#251A14]" : "border-transparent text-[#6B5B4E] hover:text-[#251A14]"
              }`}
            >
              {t.label}
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[11px] font-bold text-white" style={{ background: t.tone }}>
                {groups[t.id].length}
              </span>
            </button>
          );
        })}
      </div>

      {!selected ? (
        <div className="mt-10 flex flex-col items-center rounded-[22px] border border-dashed border-[#D9CBB8] bg-white/50 px-6 py-16 text-center">
          <div aria-hidden className="mb-4 grid grid-cols-3 gap-1.5">
            {["#FF7A57", "#E8DCCB", "#8F9BDB", "#E8DCCB", "#251A14", "#E8DCCB", "#B7B3CF", "#E8DCCB", "#FF4F26"].map((c, i) => (
              <span key={i} className="h-5 w-5 rounded-md" style={{ background: c }} />
            ))}
          </div>
          <p className="max-w-[320px] text-[14px] text-[#6B5B4E]">{EMPTY[tab]}</p>
        </div>
      ) : (
        <>
          {visible.length > 1 && (
            <div className="mt-5 flex flex-wrap gap-2">
              {visible.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setSelectedId(p.id)}
                  className={`h-9 rounded-full border px-4 text-[13px] font-medium transition ${
                    p.id === selected.id ? "border-[#251A14] bg-[#251A14] text-white" : "border-[#E6DCCD] bg-white text-[#251A14] hover:border-[#251A14]"
                  }`}
                >
                  {p.client}
                </button>
              ))}
            </div>
          )}

          <div className="mt-6 grid items-start gap-6 lg:grid-cols-[1.05fr_1fr]">
            <PostReviewCard key={selected.id} post={selected} />

            <aside className="overflow-hidden rounded-[22px] border border-[#E6DCCD] bg-white shadow-[0_14px_40px_-24px_rgba(37,26,20,0.35)]">
              <div className="flex items-center gap-3 border-b border-[#EFE4D4] px-5 py-4">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#FFE7DF] text-[#FF4F26]">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />
                  </svg>
                </span>
                <h2 className="text-[16px] font-bold text-[#251A14]">Communication</h2>
                <span className="ml-auto text-[12px] text-[#8A7B6D]">{selected.comments.filter((c) => c.role !== "system").length} comments</span>
              </div>

              <CommentThread key={selected.id} comments={selected.comments} onSend={(b) => comment(selected, b)} />

              <div className="border-t border-[#EFE4D4]">
                <DecisionBar
                  status={selected.status}
                  version={selected.version}
                  onApprove={() => approve(selected)}
                  onRework={() => rework(selected)}
                  onResubmit={() => resubmit(selected)}
                />
              </div>
            </aside>
          </div>
        </>
      )}

      {notice && (
        <div role="status" className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-full bg-[#251A14] px-5 py-3 text-[14px] font-medium text-white shadow-xl">
          {notice}
        </div>
      )}
    </section>
  );
}