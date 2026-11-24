import type { Status } from "@/types/app";

const map: Record<Status, { label: string; cls: string }> = {
  draft: { label: "Draft", cls: "bg-slate-100 text-slate-700" },
  pending_review: { label: "Pending review", cls: "bg-blue-100 text-blue-700" },
  approved: { label: "Approved", cls: "bg-green-100 text-green-700" },
  rejected: { label: "Rejected", cls: "bg-red-100 text-red-700" },
};

export function StatusBadge({ status }: { status: Status }) {
  const s = map[status];
  return <span className={`whitespace-nowrap rounded-full px-3 py-1 text-xs font-semibold ${s.cls}`}>{s.label}</span>;
}
