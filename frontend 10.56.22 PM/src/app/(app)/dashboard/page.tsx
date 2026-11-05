import Link from "next/link";
import { LuPlus } from "react-icons/lu";
import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { CampaignList } from "@/components/dashboard/campaign-list";
import { GettingStarted } from "@/components/dashboard/getting-started";
import { Greeting } from "@/components/dashboard/greeting";
import { IdeaCapture } from "@/components/dashboard/idea-capture";
import { ReviewQueue } from "@/components/dashboard/review-queue";
import { StatCards } from "@/components/dashboard/stat-cards";
import { getDashboard, getWorkspace } from "@/lib/api/dashboard";

export default async function DashboardPage() {
  const [workspace, data] = await Promise.all([getWorkspace(), getDashboard()]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Greeting name={workspace.user.name} />
          <p className="mt-1 text-muted">Here's where your campaigns stand today.</p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/settings/team"
            className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold transition-colors hover:border-ink/30"
          >
            Invite teammate
          </Link>
          <Link
            href="/campaigns/new"
            className="flex items-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-hover"
          >
            <LuPlus size={16} /> New campaign
          </Link>
        </div>
      </header>

      <GettingStarted steps={data.onboarding} />
      <StatCards stats={data.stats} />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <ReviewQueue items={data.reviewQueue} />
          <CampaignList campaigns={data.campaigns} />
        </div>
        <div className="space-y-6">
          <IdeaCapture />
          <ActivityFeed items={data.activity} />
        </div>
      </div>
    </div>
  );
}