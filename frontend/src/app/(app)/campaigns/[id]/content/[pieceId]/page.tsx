import { LuCheck, LuTrash2 } from "react-icons/lu";
import { PlatformIcon } from "@/app/platform-icon";
import { StatusBadge } from "@/app/status-badge";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Textarea } from "@/components/ui/fields";
import { Card, PageHeader, Pill } from "@/components/ui/layout";
import { addComment, approve, deleteContent, editContent, reject, requestChanges } from "@/lib/actions";
import { getCampaign, getContent, getMe, listComments, listMembers } from "@/lib/api/queries";
import { formatDate, PLATFORM_LABEL } from "@/lib/format";

const ORIGIN = { ai_generated: "AI generated", human_edit: "Human edit", variation: "Variation", regeneration: "Revised by AI" };
const DECISION = {
  approved: { label: "Approved", cls: "bg-green-100 text-green-700" },
  rejected: { label: "Rejected", cls: "bg-red-100 text-red-700" },
  changes_requested: { label: "Changes requested", cls: "bg-amber-100 text-amber-700" },
};

export default async function ContentPage({ params }: { params: Promise<{ id: string; pieceId: string }> }) {
  const { id, pieceId } = await params;
  const [me, campaign, piece, comments, members] = await Promise.all([
    getMe(), getCampaign(id), getContent(pieceId), listComments(pieceId), listMembers(id),
  ]);
  const names = new Map(members.map((m) => [m.user_id, m.name]));
  const role = campaign.my_role;
  const v = piece.current_version;
  const versionNo = v?.version_no ?? 1;
  const pending = piece.status === "pending_review";

  // Mirrors the backend rules so we only show buttons that can work. The backend re-checks everything.
  const canReview = role === "reviewer" && pending;
  const selfReview = piece.created_by === me.id || v?.created_by === me.id;
  const canEdit = ["owner", "creator", "reviewer"].includes(role) && piece.status !== "rejected";
  const canDelete = role === "owner" || role === "creator";

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader
        back={{ href: `/campaigns/${id}`, label: campaign.name }}
        eyebrow={`${campaign.brand_name} · ${piece.brief.topic}`}
        title={`${PLATFORM_LABEL[piece.platform]} post`}
        actions={<StatusBadge status={piece.status} />}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card
            title={<span className="flex items-center gap-3"><PlatformIcon platform={piece.platform} /> Version {versionNo}</span>}
            aside={v && <span className="text-xs text-muted">{ORIGIN[v.origin]} · {formatDate(v.created_at)}</span>}
          >
            <div className="whitespace-pre-wrap rounded-2xl bg-paper p-5 text-[15px] leading-relaxed">{v?.body}</div>
            {v?.creative_suggestion && (
              <p className="mt-3 text-sm text-muted"><strong className="text-ink">Creative suggestion:</strong> {v.creative_suggestion}</p>
            )}
            {piece.rejection_reason && (
              <p className="mt-3 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-800"><strong>Rejected:</strong> {piece.rejection_reason}</p>
            )}
          </Card>

          {canReview && (
            <Card title="Review">
              {selfReview ? (
                <p className="text-sm text-muted">You created or edited this version, so another reviewer has to review it.</p>
              ) : (
                <div className="space-y-5">
                  <ActionForm action={approve.bind(null, piece.id, versionNo)}>
                    <SubmitButton variant="success" pendingText="Approving…"><LuCheck size={16} /> Approve version {versionNo}</SubmitButton>
                  </ActionForm>
                  <div className="grid gap-5 md:grid-cols-2">
                    <ActionForm action={requestChanges.bind(null, piece.id, versionNo)} reset className="space-y-3">
                      <Textarea label="Request changes" name="feedback" required minLength={5} maxLength={2000}
                        placeholder="Shorter, and lead with the date." hint="The AI writes one revised version." />
                      <SubmitButton variant="outline" pendingText="Revising…">Send feedback</SubmitButton>
                    </ActionForm>
                    <ActionForm action={reject.bind(null, piece.id, versionNo)} reset confirm="Rejecting is final. Continue?" className="space-y-3">
                      <Textarea label="Reject" name="reason" required minLength={10} maxLength={2000}
                        placeholder="Off-brand claim about results." hint="Final. At least 10 characters." />
                      <SubmitButton variant="danger" pendingText="Rejecting…">Reject</SubmitButton>
                    </ActionForm>
                  </div>
                </div>
              )}
            </Card>
          )}

          {canEdit && (
            <Card title="Edit">
              <ActionForm action={editContent.bind(null, piece.id)} className="space-y-3">
                <Textarea label="Text" name="body" required maxLength={5000} rows={8} defaultValue={v?.body} key={versionNo}
                  hint="Saving creates a new version and sends the piece back for review." />
                <SubmitButton variant="dark" pendingText="Saving…">Save new version</SubmitButton>
              </ActionForm>
            </Card>
          )}

          <Card title={`Comments (${comments.length})`}>
            <ul className="space-y-3">
              {comments.map((c) => (
                <li key={c.id} className="rounded-2xl bg-paper px-4 py-3 text-sm">
                  <p className="text-xs text-muted"><strong className="text-ink">{c.author_name}</strong> · {formatDate(c.created_at)}</p>
                  <p className="mt-1 whitespace-pre-wrap">{c.body}</p>
                </li>
              ))}
            </ul>
            <ActionForm action={addComment.bind(null, piece.id)} reset className="mt-4 space-y-3">
              <Textarea label="Add a comment" name="body" required maxLength={2000} rows={2} />
              <SubmitButton variant="outline" pendingText="Posting…">Post comment</SubmitButton>
            </ActionForm>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Brief">
            <dl className="space-y-3 text-sm">
              <div><dt className="text-xs text-muted">Objective</dt><dd>{piece.brief.objective}</dd></div>
              {piece.brief.target_audience && <div><dt className="text-xs text-muted">Audience</dt><dd>{piece.brief.target_audience}</dd></div>}
              {piece.brief.key_messages && <div><dt className="text-xs text-muted">Key messages</dt><dd>{piece.brief.key_messages}</dd></div>}
              <div><dt className="text-xs text-muted">Tone</dt><dd>{piece.brief.effective_tone}</dd></div>
            </dl>
          </Card>

          <Card title="History">
            <ol className="space-y-3 text-sm">
              {[...piece.versions].reverse().map((ver) => {
                const reviews = piece.reviews.filter((r) => r.version_no === ver.version_no);
                return (
                  <li key={ver.id}>
                    <details>
                      <summary className="cursor-pointer">
                        <strong>v{ver.version_no}</strong> · {ORIGIN[ver.origin]}
                        {ver.created_by && ` by ${names.get(ver.created_by) ?? "a former member"}`}
                        <span className="block text-xs text-muted">{formatDate(ver.created_at)}</span>
                      </summary>
                      <p className="mt-2 whitespace-pre-wrap rounded-xl bg-paper p-3 text-xs">{ver.body}</p>
                    </details>
                    {reviews.map((r) => (
                      <p key={r.id} className="mt-1.5 text-xs">
                        <Pill className={DECISION[r.decision].cls}>{DECISION[r.decision].label}</Pill>{" "}
                        by {names.get(r.reviewer_id) ?? "a reviewer"}{(r.reason || r.feedback) && `: "${r.reason ?? r.feedback}"`}
                      </p>
                    ))}
                  </li>
                );
              })}
            </ol>
          </Card>

          {canDelete && (
            <ActionForm action={deleteContent.bind(null, piece.id, campaign.id)} confirm="Delete this piece? Its history is kept but it disappears from the campaign.">
              <SubmitButton variant="danger" className="w-full" pendingText="Deleting…"><LuTrash2 size={15} /> Delete piece</SubmitButton>
            </ActionForm>
          )}
        </div>
      </div>
    </div>
  );
}
