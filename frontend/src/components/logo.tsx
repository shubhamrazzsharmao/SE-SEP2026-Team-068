import { site } from "@/lib/site";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
        <rect x="1" y="1" width="11" height="11" rx="3" fill="currentColor" />
        <rect x="14" y="1" width="11" height="11" rx="3" fill="currentColor" />
        <rect x="1" y="14" width="11" height="11" rx="3" fill="currentColor" />
        <rect x="14" y="14" width="11" height="11" rx="3" className="fill-brand" />
      </svg>
      <span className="display text-xl" style={{ fontStretch: "110%" }}>
        {site.name}
      </span>
    </span>
  );
}