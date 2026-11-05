import Link from "next/link";
import type { DashboardData } from "@/types/app";

export function StatCards({ stats }: { stats: DashboardData["stats"] }) {
  const items = [
    { label: "Approved", value: stats.approved, sub: `of ${stats.total} posts`, dot: "bg-green-500", pct: (stats.approved / stats.total) * 100 },
    { label: "In review", value: stats.inReview, sub: "waiting on feedback", dot: "bg-blue-500" },
    { label: "Changes requested", value: stats.changesRequested, sub: "need a revision", dot: "bg-amber-500" },
    { label: "Plans to approve", value: stats.plansToApprove, sub: "block post generation", dot: "bg-purple-500" },
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