import Link from "next/link";
import { EmptyState } from "@/app/empty-state";
import { PlatformIcon } from "@/app/platform-icon";
import { StatusBadge } from "@/app/status-badge";
import { PageHeader, Pill } from "@/components/ui/layout";
import { listCampaigns, listContent } from "@/lib/api/queries";
import { formatDate, PLATFORM_LABEL, ROLE_LABEL, snippet } from "@/lib/format";
import type { ContentStatus } from "@/types/api";

const TABS: { label: string; value: ContentStatus }[] = [
  { label: "Pending review", value: "pending_review" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
];

export default async function ReviewsPage({ searchParams }: { searchParams: Promise<{ status?: string }> }) {
  const sp = await searchParams;
  const status = TABS.find((t) => t.value === sp.status)?.value ?? "pending_review";
  const campaigns = await listCampaigns();
  const lists = await Promise.all(campaigns.map((c) => listContent(String(c.id), status)));
  const rows = campaigns
    .flatMap((c, i) => lists[i].map((p) => ({ p, c })))
    .sort((a, b) => b.p.updated_at.localeCompare(a.p.updated_at));

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <PageHeader title="Reviews" description="Content across all your campaigns. Only reviewers can approve or reject." />

      <nav className="flex gap-2">
        {TABS.map((t) => (
          <Link key={t.value} href={`?status=${t.value}`}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${status === t.value ? "bg-ink text-white" : "bg-white text-muted hover:text-ink"}`}>
            {t.label}
          </Link>
        ))}
      </nav>

      {rows.length === 0 ? (
        <EmptyState title="Nothing here" text="Content with this status shows up here." />
      ) : (
        <ul className="space-y-2">
          {rows.map(({ p, c }) => (
            <li key={p.id}>
              <Link href={`/campaigns/${c.id}/content/${p.id}`}
                className="flex items-center gap-4 rounded-2xl border border-line bg-white p-4 transition-colors hover:border-ink/30">
                <PlatformIcon platform={p.platform} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold">{snippet(p.current_version?.body ?? "")}</p>
                  <p className="truncate text-xs text-muted">
                    {c.brand_name} · {c.name} · {PLATFORM_LABEL[p.platform]} · v{p.current_version?.version_no ?? 1} · {formatDate(p.updated_at)}
                  </p>
                </div>
                {c.my_role === "reviewer" && status === "pending_review" && <Pill className="bg-brand/10 text-brand">Your review</Pill>}
                <span className="hidden text-xs text-muted sm:inline">{ROLE_LABEL[c.my_role]}</span>
                <StatusBadge status={p.status} />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
