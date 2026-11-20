"use client";

import Link from "next/link";

// Shown when a backend call fails (backend down, misconfigured Supabase keys, etc.).
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="grid min-h-screen place-items-center bg-paper px-6">
      <div className="max-w-md rounded-3xl border border-line bg-white p-8 text-center">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted">{error.message || "The request failed."}</p>
        <div className="mt-6 flex justify-center gap-3">
          <button onClick={reset} className="rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-hover">
            Try again
          </button>
          <Link href="/login" className="rounded-xl border border-line px-4 py-2.5 text-sm font-semibold hover:border-ink/30">
            Back to login
          </Link>
        </div>
      </div>
    </main>
  );
}
