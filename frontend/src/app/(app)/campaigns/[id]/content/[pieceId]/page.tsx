import { LuTrash2 } from "react-icons/lu";
import { PlatformIcon } from "@/app/platform-icon";
import { StatusBadge } from "@/app/status-badge";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Textarea } from "@/components/ui/fields";
import { Card, PageHeader, Pill } from "@/components/ui/layout";
import { CommentThread } from "@/components/review/comment-thread";
import { DecisionBar } from "@/components/review/decision-bar";
import { deleteContent, editContent } from "@/lib/actions";
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

  // Mirrors the backend rules so we only show buttons that can work. The backend re-checks everything.
  const selfReview = piece.created_by === me.id || v?.created_by === me.id;
  const canEdit = ["owner", "creator", "reviewer"].includes(role) && piece.status !== "rejected";
  const canDelete = role === "owner" || role === "creator";
  const approval = piece.status === "approved"
    ? piece.reviews.findLast((r) => r.decision === "approved" && r.version_no === versionNo)
    : undefined;
  const approvedBy = approval && `${names.get(approval.reviewer_id) ?? "a reviewer"} · ${formatDate(approval.created_at)}`;

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
          </Card>

          {piece.status !== "draft" && <Card title="Review">
            <DecisionBar
              key={`${piece.status}-${versionNo}`}
              pieceId={piece.id}
              versionNo={versionNo}
              status={piece.status}
              rejectionReason={piece.rejection_reason}
              isReviewer={role === "reviewer"}
              selfReview={selfReview}
              approvedBy={approvedBy}
            />
          </Card>}

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
            <CommentThread pieceId={piece.id} comments={comments} meId={me.id} members={members} />
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
