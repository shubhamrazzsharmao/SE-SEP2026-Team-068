import { EmptyState } from "@/app/empty-state";
import type { ActivityItem } from "@/types/app";

const dot: Record<ActivityItem["kind"], string> = {
  approved: "bg-green-500",
  generated: "bg-brand",
  changes: "bg-amber-500",
  plan: "bg-purple-500",
};

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <section className="rounded-3xl border border-line bg-white p-6">
      <h2 className="text-lg font-semibold">Recent activity</h2>
      {items.length === 0 ? (
        <div className="mt-4">
          <EmptyState title="Nothing yet" text="Every comment, version and approval shows up here." />
        </div>
      ) : (
        <ol className="mt-5 space-y-5 border-l-2 border-line pl-5">
          {items.map((a) => (
            <li key={a.id} className="relative text-sm">
              <span className={`absolute -left-[27px] top-1 h-3 w-3 rounded-full ${dot[a.kind]}`} />
              <p className="font-medium">{a.text}</p>
              <p className="text-xs text-muted">
                {a.detail} · {a.time}
              </p>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}