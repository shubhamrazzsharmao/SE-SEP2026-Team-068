import "server-only";
import { cache } from "react";
import { api } from "@/lib/api/client";
import { config } from "@/lib/config";
import { dashboardMock, workspaceMock } from "@/mocks/dashboard";
import type { ActivityOut, BrandOut, CampaignOut, ContentPieceOut, DashboardOut, StatusCounts, UserOut } from "@/types/api";
import type { ActivityItem, Campaign, DashboardData, ReviewItem, Stage, Workspace } from "@/types/app";

const PLATFORM_LABEL = { blog: "blog post", linkedin: "LinkedIn post", facebook: "Facebook post", instagram: "Instagram post" };

// GET /me must finish before any other call: the first authenticated request creates the
// user's profile row, and parallel first requests would race to insert it.
const getMe = cache(() => api<UserOut>("/me"));

const loadAll = cache(async () => {
  const me = await getMe();
  const [brands, campaigns, dashboard] = await Promise.all([
    api<BrandOut[]>("/brands"),
    api<CampaignOut[]>("/campaigns"),
    api<DashboardOut>("/dashboard"),
  ]);
  return { me, brands, campaigns, dashboard };
});

export const getWorkspace = cache(async (): Promise<Workspace> => {
  if (config.useMocks) return workspaceMock;
  const { me, brands, campaigns, dashboard } = await loadAll();

  // Brands are the "clients". Include brands of campaigns the user was added to, not only owned ones.
  const names = new Map<string, string>();
  brands.forEach((b) => names.set(String(b.id), b.name));
  campaigns.forEach((c) => names.set(String(c.brand_id), c.brand_name));

  return {
    user: { name: me.name, email: me.email },
    clients: [...names].map(([id, name]) => ({ id, name, initials: initials(name) })),
    pendingReviews: dashboard.totals.pending_review,
  };
});

export const getDashboard = cache(async (): Promise<DashboardData> => {
  if (config.useMocks) return dashboardMock;
  const { brands, campaigns, dashboard } = await loadAll();
  const byId = new Map(campaigns.map((c) => [c.id, c]));

  // Pending pieces per campaign (only campaigns that have some), and the activity log of
  // campaigns the user owns (the backend only shows the log to owners).
  const withPending = dashboard.campaigns.filter((c) => c.counts.pending_review > 0);
  const owned = campaigns.filter((c) => c.my_role === "owner");
  const [pending, logs] = await Promise.all([
    Promise.all(withPending.map((c) => api<ContentPieceOut[]>(`/campaigns/${c.campaign_id}/content?status=pending_review`))),
    Promise.all(owned.map((c) => api<ActivityOut[]>(`/campaigns/${c.id}/activity`))),
  ]);

  const reviewQueue: ReviewItem[] = pending
    .flat()
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
    .slice(0, 6)
    .map((p) => {
      const c = byId.get(p.campaign_id);
      return {
        id: String(p.id),
        campaignId: String(p.campaign_id),
        platform: p.platform,
        clientName: c?.brand_name ?? "",
        campaign: c?.name ?? "",
        snippet: firstLine(p.current_version?.body ?? ""),
        status: p.status,
        version: p.current_version?.version_no ?? 1,
        updated: timeAgo(p.updated_at),
      };
    });

  const activity: ActivityItem[] = logs
    .flat()
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(0, 6)
    .map((a) => toActivity(a, byId.get(a.campaign_id)));

  const t = dashboard.totals;
  const total = sum(t);

  return {
    stats: { ...t, total },
    campaigns: dashboard.campaigns.map((cc): Campaign => {
      const c = byId.get(cc.campaign_id);
      return {
        id: String(cc.campaign_id),
        clientName: c?.brand_name ?? "",
        title: cc.name,
        stage: stage(cc.counts),
        myRole: c?.my_role ?? "creator",
        approved: cc.counts.approved,
        total: sum(cc.counts),
      };
    }),
    reviewQueue,
    activity,
    onboarding: [
      { label: "Add a client brand", href: "/clients", done: brands.length > 0 || campaigns.length > 0 },
      { label: "Create a campaign", href: "/campaigns/new", done: campaigns.length > 0 },
      { label: "Generate content", href: "/campaigns", done: total > 0 },
      { label: "Approve a post", href: "/reviews", done: t.approved > 0 },
    ],
  };
});

// ---------------------------------------------------------------- helpers
function sum(c: StatusCounts) {
  return c.draft + c.pending_review + c.approved + c.rejected;
}

function stage(c: StatusCounts): Stage {
  if (sum(c) === 0) return "Not started";
  if (c.pending_review > 0 || c.draft > 0) return "In review";
  return "Complete";
}

function initials(name: string) {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]!.toUpperCase()).join("") || "?";
}

function firstLine(body: string) {
  const line = body.split("\n").map((l) => l.replace(/^#+\s*/, "").trim()).find(Boolean) ?? "";
  return line.length > 120 ? `${line.slice(0, 117)}…` : line;
}

function timeAgo(iso: string) {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} hr ago`;
  if (s < 172800) return "Yesterday";
  return new Date(iso).toLocaleDateString("en", { month: "short", day: "numeric" });
}

function toActivity(a: ActivityOut, c: CampaignOut | undefined): ActivityItem {
  const who = a.user_name;
  const d = a.detail ?? {};
  const platform = typeof d.platform === "string" ? PLATFORM_LABEL[d.platform as keyof typeof PLATFORM_LABEL] : "post";
  const v = a.version_no ? ` · v${a.version_no}` : "";
  const where = `${c?.brand_name ?? ""}${c ? ` · ${c.name}` : ""}`;

  const map: Record<string, [string, ActivityItem["kind"]]> = {
    approved: [`${who} approved a post`, "approved"],
    rejected: [`${who} rejected a post`, "changes"],
    changes_requested: [`${who} requested changes`, "changes"],
    regenerated: ["A new version was generated", "generated"],
    generated: [`A ${platform} was generated`, "generated"],
    generation_requested: [`${who} started generation`, "generated"],
    generation_failed: ["Generation failed", "changes"],
    edited: [`${who} edited a post`, "other"],
    deleted: [`${who} deleted a post`, "other"],
    commented: [`${who} commented on a post`, "other"],
    campaign_created: [`${who} created the campaign`, "other"],
    member_added: [`${who} added ${d.member ?? "a member"}`, "other"],
    member_removed: [`${who} removed ${d.member ?? "a member"}`, "other"],
    brief_created: [`${who} wrote a brief${d.topic ? `: ${d.topic}` : ""}`, "other"],
    brief_updated: [`${who} updated a brief`, "other"],
  };
  const [text, kind] = map[a.action] ?? [`${who}: ${a.action.replaceAll("_", " ")}`, "other"];
  return { id: String(a.id), text, detail: `${where}${v}`, time: timeAgo(a.created_at), kind };
}
