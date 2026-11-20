import Link from "next/link";
import { LuChevronLeft } from "react-icons/lu";

export function PageHeader({
  title, eyebrow, description, back, actions,
}: {
  title: string;
  eyebrow?: string;
  description?: React.ReactNode;
  back?: { href: string; label: string };
  actions?: React.ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        {back && (
          <Link href={back.href} className="mb-2 inline-flex items-center gap-1 text-sm font-medium text-muted hover:text-ink">
            <LuChevronLeft size={16} /> {back.label}
          </Link>
        )}
        {eyebrow && <p className="text-xs font-semibold uppercase tracking-wide text-muted">{eyebrow}</p>}
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        {description && <div className="mt-1 text-muted">{description}</div>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </header>
  );
}

export function Card({ title, aside, children, className = "" }: {
  title?: React.ReactNode;
  aside?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-3xl border border-line bg-white p-6 ${className}`}>
      {(title || aside) && (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {aside}
        </div>
      )}
      {children}
    </section>
  );
}

export function LinkButton({ href, children, variant = "primary" }: {
  href: string;
  children: React.ReactNode;
  variant?: "primary" | "outline";
}) {
  const cls = variant === "primary"
    ? "bg-brand text-white hover:bg-brand-hover"
    : "border border-line bg-white hover:border-ink/30";
  return (
    <Link href={href} className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors ${cls}`}>
      {children}
    </Link>
  );
}

export function Pill({ children, className = "bg-paper text-ink" }: { children: React.ReactNode; className?: string }) {
  return <span className={`whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold ${className}`}>{children}</span>;
}
