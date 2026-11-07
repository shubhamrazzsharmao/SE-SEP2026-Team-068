"use client";

import { useEffect, useRef, useState } from "react";
import type { ReviewComment } from "@/types/review";

function initials(name: string) {
  return name.replace(/\(.*\)/, "").trim().slice(0, 1).toUpperCase();
}

function WithMentions({ text }: { text: string }) {
  const parts = text.split(/(@[A-Z][a-z]+(?: [A-Z][a-z]+)?)/g);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith("@") ? (
          <span key={i} className="rounded bg-[#E3E6F8] px-1 font-medium text-[#4A55A8]">
            {p}
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
}

export function CommentThread({ comments, onSend }: { comments: ReviewComment[]; onSend: (body: string) => void }) {
  const [draft, setDraft] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [comments.length]);

  function send() {
    const body = draft.trim();
    if (!body) return;
    onSend(body);
    setDraft("");
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div ref={listRef} className="flex max-h-[330px] min-h-[200px] flex-1 flex-col gap-4 overflow-y-auto px-5 py-5">
        {comments.length === 0 && <p className="m-auto text-[13px] text-[#8A7B6D]">No comments yet. Start the discussion.</p>}
        {comments.map((c) =>
          c.role === "system" ? (
            <p key={c.id} className="mx-auto rounded-full bg-[#F3E9DC] px-3 py-1 text-center text-[12px] text-[#6B5B4E]">
              {c.body} <span className="text-[#A6988A]">· {c.time}</span>
            </p>
          ) : (
            <div key={c.id} className="flex items-end gap-3">
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-[12px] font-semibold ${
                  c.role === "client" ? "bg-[#E3E6F8] text-[#4A55A8]" : "bg-[#EFE4D4] text-[#6B5B4E]"
                }`}
              >
                {initials(c.author)}
              </span>
              <div className="min-w-0">
                <p className="mb-1 flex flex-wrap items-center gap-2 text-[12px]">
                  <span className="font-bold text-[#251A14]">{c.author}</span>
                  <span className="text-[#A6988A]">{c.time}</span>
                  {c.role === "client" && <span className="rounded-full bg-[#E3E6F8] px-2 py-0.5 text-[10px] font-semibold text-[#4A55A8]">Client</span>}
                </p>
                <p className="rounded-2xl rounded-bl-md bg-[#F6EFE5] px-4 py-2.5 text-[14px] leading-snug text-[#251A14]">
                  <WithMentions text={c.body} />
                </p>
              </div>
            </div>
          ),
        )}
      </div>

      <div className="flex items-center gap-3 border-t border-[#EFE4D4] px-4 py-3">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#251A14] text-[12px] font-semibold text-white">S</span>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Write something, mention @name…"
          className="h-11 min-w-0 flex-1 rounded-full bg-[#F6EFE5] px-4 text-[14px] text-[#251A14] outline-none transition placeholder:text-[#8A7B6D] focus:ring-4 focus:ring-[#FF4F26]/15"
        />
        <button
          type="button"
          onClick={send}
          disabled={!draft.trim()}
          aria-label="Send comment"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#FF4F26] text-white transition hover:bg-[#e8431d] disabled:bg-[#EDE3D3] disabled:text-[#A6988A]"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}