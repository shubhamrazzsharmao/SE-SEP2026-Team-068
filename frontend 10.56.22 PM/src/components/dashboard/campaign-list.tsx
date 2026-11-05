import Link from "next/link";
import { LuPlus } from "react-icons/lu";
import type { Campaign, Stage } from "@/types/app";

const stageCls: Record<Stage, string> = {
  Planning: "bg-slate-100 text-slate-700",
  Generating: "bg-brand/10 text-brand",
  "In review": "bg-blue-100 text-blue-700",
  Complete: "bg-green-100 text-green-700",
};

export function CampaignList({ campaigns }: { campaigns: Campaign[] }) {
  return (
    <section>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Active campaigns</h2>
        <Link href="/campaigns" className="text-sm font-semibold text-brand hover:underline">
          View all
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {campaigns.map((c) => (
          <Link
            key={c.id}
            href={`/campaigns/${c.id}`}
            className="rounded-3xl border border-line bg-white p-5 transition-transform duration-200 hover:-translate-y-1"
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">{c.clientName}</p>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${stageCls[c.stage]}`}>{c.stage}</span>
            </div>
            <h3 className="mt-2 text-lg font-semibold">{c.title}</h3>
            <div className="mt-5 flex justify-between text-xs font-medium text-muted">
              <span>
                {c.approved} of {c.total} approved
              </span>
              <span>Due {c.due}</span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-line">
              <div className="h-2 rounded-full bg-brand" style={{ width: `${(c.approved / c.total) * 100}%` }} />
            </div>
          </Link>
        ))}

        <Link
          href="/campaigns/new"
          className="grid min-h-[150px] place-items-center rounded-3xl border border-dashed border-ink/20 text-sm font-semibold text-muted transition-colors hover:border-brand hover:text-brand"
        >
          <span className="flex items-center gap-2">
            <LuPlus size={16} /> New campaign
          </span>
        </Link>
      </div>
    </section>
  );
}