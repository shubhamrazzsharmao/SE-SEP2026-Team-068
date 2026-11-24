import Link from "next/link";
import { LuSparkles, LuX } from "react-icons/lu";
import { EmptyState } from "@/app/empty-state";
import { PlatformIcon } from "@/app/platform-icon";
import { StatusBadge } from "@/app/status-badge";
import { ActionForm, SubmitButton } from "@/components/ui/action-form";
import { Input, Select, Textarea } from "@/components/ui/fields";
import { Card, PageHeader, Pill } from "@/components/ui/layout";
import { addMember, createBrief, generateContent, removeMember } from "@/lib/actions";
import { campaignActivity, getCampaign, getMe, listBriefs, listContent, listMembers } from "@/lib/api/queries";
import { BRIEF_STATUS, formatDate, PLATFORM_LABEL, PLATFORMS, ROLE_LABEL, snippet } from "@/lib/format";
import type { ContentStatus } from "@/types/api";

const FILTERS: { label: string; value?: ContentStatus }[] = [
  { label: "All" },
  { label: "Pending review", value: "pending_review" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
];

export default async function CampaignPage({ params, searchParams }: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ status?: string }>;
}) {
  const [{ id }, sp] = await Promise.all([params, searchParams]);
  const status = FILTERS.find((f) => f.value === sp.status)?.value;
  const [me, campaign] = await Promise.all([getMe(), getCampaign(id)]);
  const role = campaign.my_role;
  const isOwner = role === "owner";
  const canWrite = role === "owner" || role === "creator";

  const [briefs, content, members, activity] = await Promise.all([
    listBriefs(id), listContent(id, status), listMembers(id), isOwner ? campaignActivity(id) : Promise.resolve([]),
  ]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader
        back={{ href: "/campaigns", label: "Campaigns" }}
        eyebrow={campaign.brand_name}
        title={campaign.name}
        description={
          <>
            {campaign.description && <p>{campaign.description}</p>}
            <p className="mt-1 text-sm">Your role: <strong className="text-ink">{ROLE_LABEL[role]}</strong></p>
          </>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* ---------------- Content */}
          <Card
            title="Content"
            aside={
              <nav className="flex flex-wrap gap-1">
                {FILTERS.map((f) => (
                  <Link key={f.label} href={f.value ? `?status=${f.value}` : "?"}
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${status === f.value ? "bg-ink text-white" : "bg-paper text-muted hover:text-ink"}`}>
                    {f.label}
                  </Link>
                ))}
              </nav>
            }
          >
            {content.length === 0 ? (
              <EmptyState title="No content here" text={status ? "Nothing with this status." : "Write a brief and generate content to see it here."} />
            ) : (
              <ul className="space-y-2">
                {content.map((p) => (
                  <li key={p.id}>
                    <Link href={`/campaigns/${id}/content/${p.id}`}
                      className="flex items-center gap-4 rounded-2xl border border-line p-3 transition-colors hover:border-ink/30 hover:bg-paper">
                      <PlatformIcon platform={p.platform} />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-semibold">{snippet(p.current_version?.body ?? "")}</p>
                        <p className="truncate text-xs text-muted">
                          {PLATFORM_LABEL[p.platform]} · v{p.current_version?.version_no ?? 1} · {formatDate(p.updated_at)}
                        </p>
                      </div>
                      <StatusBadge status={p.status} />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          {/* ---------------- Briefs */}
          <Card title="Briefs">
            {briefs.length === 0 ? (
              <EmptyState title="No briefs yet" text={canWrite ? "Write the first brief below." : "Owners and creators write briefs."} />
            ) : (
              <ul className="space-y-3">
                {briefs.map((b) => (
                  <li key={b.id} className="rounded-2xl border border-line p-4">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-semibold">{b.topic}</p>
                        <p className="mt-0.5 text-sm text-muted">{b.objective}</p>
                      </div>
                      <Pill className={BRIEF_STATUS[b.status].cls}>{BRIEF_STATUS[b.status].label}</Pill>
                    </div>
                    <p className="mt-2 text-xs text-muted">
                      {b.platforms.map((p) => PLATFORM_LABEL[p]).join(", ")} · Tone: {b.effective_tone}
                    </p>
                    {canWrite && b.status === "draft" && (
                      <ActionForm action={generateContent.bind(null, b.id)} className="mt-3">
                        <SubmitButton variant="dark" pendingText="Generating…"><LuSparkles size={15} /> Generate content</SubmitButton>
                      </ActionForm>
                    )}
                  </li>
                ))}
              </ul>
            )}

            {canWrite && (
              <details className="group mt-5 rounded-2xl bg-paper p-4" open={briefs.length === 0}>
                <summary className="cursor-pointer text-sm font-semibold">New brief</summary>
                <ActionForm action={createBrief.bind(null, campaign.id)} reset className="mt-4 space-y-4">
                  <Input label="Topic" name="topic" required maxLength={255} placeholder="Week 1 kickoff" />
                  <Textarea label="Objective" name="objective" required maxLength={5000} placeholder="Get members to sign up for the 4-week challenge." />
                  <fieldset>
                    <legend className="mb-1.5 text-sm font-medium">Platforms</legend>
                    <div className="flex flex-wrap gap-3">
                      {PLATFORMS.map((p) => (
                        <label key={p} className="flex items-center gap-2 rounded-xl border border-line bg-white px-3 py-2 text-sm">
                          <input type="checkbox" name="platforms" value={p} defaultChecked={p === "linkedin"} className="accent-brand" />
                          {PLATFORM_LABEL[p]}
                        </label>
                      ))}
                    </div>
                  </fieldset>
                  <Textarea label="Target audience" name="target_audience" maxLength={5000} placeholder="Optional" />
                  <Textarea label="Key messages" name="key_messages" maxLength={5000} placeholder="Optional" />
                  <Input label="Tone override" name="tone" maxLength={100} placeholder="Optional: leave empty to use the brand tone" />
                  <SubmitButton pendingText="Saving…">Save brief</SubmitButton>
                </ActionForm>
              </details>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          {/* ---------------- Members */}
          <Card title="Team">
            <ul className="space-y-2">
              {members.map((m) => (
                <li key={m.user_id} className="flex items-center gap-3 text-sm">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-paper-hero text-xs font-bold">
                    {m.name[0]?.toUpperCase()}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{m.name}{m.user_id === me.id && " (you)"}</p>
                    <p className="truncate text-xs text-muted">{m.email}</p>
                  </div>
                  <Pill>{ROLE_LABEL[m.member_role]}</Pill>
                  {isOwner && m.user_id !== me.id && (
                    <ActionForm action={removeMember.bind(null, campaign.id, m.user_id)} confirm={`Remove ${m.name} from this campaign?`}>
                      <button type="submit" aria-label={`Remove ${m.name}`} className="grid h-7 w-7 place-items-center rounded-lg text-muted hover:bg-red-50 hover:text-red-700">
                        <LuX size={14} />
                      </button>
                    </ActionForm>
                  )}
                </li>
              ))}
            </ul>
            {isOwner && (
              <ActionForm action={addMember.bind(null, campaign.id)} reset className="mt-5 space-y-3 border-t border-line pt-4">
                <Input label="Add by email" name="email" type="email" required placeholder="teammate@agency.com"
                  hint="They must have signed in to the app at least once." />
                <Select label="Role" name="member_role" defaultValue="reviewer">
                  <option value="creator">Creator: writes briefs, generates, edits</option>
                  <option value="reviewer">Reviewer: approves, rejects, requests changes</option>
                  <option value="brand_manager">Brand manager: edits brand guidelines</option>
                  <option value="owner">Owner: everything, manages the team</option>
                </Select>
                <SubmitButton variant="dark" className="w-full" pendingText="Adding…">Add member</SubmitButton>
              </ActionForm>
            )}
          </Card>

          {/* ---------------- Activity (owners only, per backend rules) */}
          {isOwner && (
            <Card title="Activity log">
              {activity.length === 0 ? (
                <EmptyState title="Nothing yet" text="Every brief, generation and review is logged here." />
              ) : (
                <ol className="max-h-[420px] space-y-3 overflow-y-auto text-sm">
                  {activity.map((a) => (
                    <li key={a.id}>
                      <p><span className="font-medium">{a.user_name}</span> {a.action.replaceAll("_", " ")}{a.version_no ? ` (v${a.version_no})` : ""}</p>
                      <p className="text-xs text-muted">{formatDate(a.created_at)}</p>
                    </li>
                  ))}
                </ol>
              )}
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
