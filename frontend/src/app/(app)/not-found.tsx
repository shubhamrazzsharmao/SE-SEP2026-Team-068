import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-md rounded-3xl border border-line bg-white p-8 text-center">
      <h1 className="text-xl font-semibold">Not found</h1>
      <p className="mt-2 text-sm text-muted">It doesn&apos;t exist, or you aren&apos;t a member of its campaign.</p>
      <Link href="/dashboard" className="mt-6 inline-block rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-hover">
        Back to dashboard
      </Link>
    </div>
  );
}
