import Link from "next/link";
import type { DashboardData } from "@/types/app";

export function StatCards({ stats }: { stats: DashboardData["stats"] }) {
  const pct = stats.total ? (stats.approved / stats.total) * 100 : 0;
  const items = [
    { label: "Approved", value: stats.approved, sub: `of ${stats.total} posts`, dot: "bg-green-500", pct },
    { label: "Pending review", value: stats.pending_review, sub: "waiting on a reviewer", dot: "bg-blue-500" },
    { label: "Rejected", value: stats.rejected, sub: "closed with a reason", dot: "bg-red-500" },
    { label: "Drafts", value: stats.draft, sub: "not sent for review", dot: "bg-slate-400" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {items.map((it) => (
        <Link
          key={it.label}
          href="/reviews"
          className="rounded-2xl border border-line bg-white p-5 transition-transform duration-200 hover:-translate-y-1"
        >
          <p className="flex items-center gap-2 text-sm font-medium text-muted">
            <span className={`h-2 w-2 rounded-full ${it.dot}`} />
            {it.label}
          </p>
          <p className="display mt-3 text-4xl">{it.value}</p>
          <p className="mt-1 text-sm text-muted">{it.sub}</p>
          {it.pct !== undefined && (
            <div className="mt-3 h-1.5 rounded-full bg-line">
              <div className="h-1.5 rounded-full bg-green-500" style={{ width: `${it.pct}%` }} />
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
