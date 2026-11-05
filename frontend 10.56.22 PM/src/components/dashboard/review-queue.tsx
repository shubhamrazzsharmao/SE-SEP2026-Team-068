import Link from "next/link";
import { EmptyState } from "@/app/empty-state";
import { PlatformIcon } from "@/app/platform-icon";
import { StatusBadge } from "@/app/status-badge";
import type { ReviewItem } from "@/types/app";

export function ReviewQueue({ items }: { items: ReviewItem[] }) {
  return (
    <section className="rounded-3xl border border-line bg-white p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Needs your attention <span className="ml-1 rounded-full bg-brand px-2 py-0.5 text-xs font-bold text-white">{items.length}</span>
        </h2>
        <Link href="/reviews" className="text-sm font-semibold text-brand hover:underline">
          View all
        </Link>
      </div>

      <div className="mt-4 space-y-2">
        {items.length === 0 ? (
          <EmptyState title="All caught up" text="Posts waiting on you will appear here." />
        ) : (
          items.map((it) => (
            <Link
              key={it.id}
              href={`/campaigns/${it.campaign}/posts/${it.id}`}
              className="flex items-center gap-4 rounded-2xl border border-line p-3 transition-colors hover:border-ink/30 hover:bg-paper"
            >
              <PlatformIcon platform={it.platform} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{it.snippet}</p>
                <p className="truncate text-xs text-muted">
                  {it.clientName} · {it.campaign} · {it.updated}
                </p>
              </div>
              <StatusBadge status={it.status} />
            </Link>
          ))
        )}
      </div>
    </section>
  );
}