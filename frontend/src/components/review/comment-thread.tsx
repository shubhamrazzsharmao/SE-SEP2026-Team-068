"use client";

import { useEffect, useRef } from "react";
import { LuArrowUp } from "react-icons/lu";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { addComment } from "@/lib/actions";
import { formatDate, ROLE_LABEL } from "@/lib/format";
import type { CommentOut, MemberRole } from "@/types/api";

type Props = {
  pieceId: number;
  comments: CommentOut[];
  meId: string;
  /** Current campaign members, used for role badges and @mention highlighting. */
  members: { user_id: string; name: string; member_role: MemberRole }[];
};

/** Chat-style discussion of one content piece. Any campaign member can read and post. */
export function CommentThread({ pieceId, comments, meId, members }: Props) {
  const listRef = useRef<HTMLDivElement>(null);
  const roles = new Map(members.map((m) => [m.user_id, m.member_role]));
  const names = members.map((m) => m.name).filter(Boolean);

  // Keep the newest comment in view when one is added.
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [comments.length]);

  return (
    <div className="-mx-6 -mb-6 flex flex-col border-t border-line">
      <div ref={listRef} className="flex max-h-[420px] min-h-[160px] flex-col gap-4 overflow-y-auto px-6 py-5">
        {comments.length === 0 && <p className="m-auto text-sm text-muted">No comments yet. Start the discussion.</p>}
        {comments.map((c) => {
          const mine = c.user_id === meId;
          const role = roles.get(c.user_id);
          return (
            <div key={c.id} className={`flex items-end gap-3 ${mine ? "flex-row-reverse" : ""}`}>
              <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${mine ? "bg-ink text-white" : "bg-paper text-ink"}`}>
                {initials(c.author_name)}
              </span>
              <div className={`min-w-0 max-w-[80%] ${mine ? "text-right" : ""}`}>
                <p className={`mb-1 flex flex-wrap items-center gap-2 text-xs ${mine ? "justify-end" : ""}`}>
                  <span className="font-bold text-ink">{mine ? "You" : c.author_name}</span>
                  {role && <span className="rounded-full bg-paper px-2 py-0.5 text-[10px] font-semibold text-muted">{ROLE_LABEL[role]}</span>}
                  <span className="text-muted">{formatDate(c.created_at)}</span>
                </p>
                <p className={`inline-block whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-left text-sm leading-snug ${
                  mine ? "rounded-br-md bg-ink text-white" : "rounded-bl-md bg-paper text-ink"
                }`}>
                  <WithMentions text={c.body} names={names} />
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <ActionForm action={addComment.bind(null, pieceId)} reset className="border-t border-line px-6 py-4">
        <div className="flex items-center gap-3">
          <label className="sr-only" htmlFor="comment-body">Write a comment</label>
          <input id="comment-body" name="body" required maxLength={2000} autoComplete="off"
            placeholder="Write something, mention @name…"
            className="h-11 min-w-0 flex-1 rounded-xl bg-paper px-4 text-sm outline-none transition focus:ring-4 focus:ring-brand/15" />
          <SubmitButton className="h-11 shrink-0" pendingText="Sending…">
            <LuArrowUp size={16} strokeWidth={2.4} /> Send
          </SubmitButton>
        </div>
      </ActionForm>
    </div>
  );
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] ?? "?") + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
}

/** Highlights "@Full Name" for campaign members (longest names first), otherwise "@word". */
function WithMentions({ text, names }: { text: string; names: string[] }) {
  const escaped = [...names].sort((a, b) => b.length - a.length).map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const pattern = new RegExp(`(@(?:${[...escaped, "[\\w.-]+"].join("|")}))`, "g");
  return (
    <>
      {text.split(pattern).map((part, i) =>
        i % 2 === 1 ? (
          <span key={i} className="rounded bg-brand/15 px-1 font-medium">{part}</span>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}
