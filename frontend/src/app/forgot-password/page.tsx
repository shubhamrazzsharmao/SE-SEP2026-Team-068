"use client";

import Link from "next/link";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [state, setState] = useState<{ busy?: boolean; error?: string; sent?: boolean }>({});

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setState({ busy: true });
    const email = String(new FormData(e.currentTarget).get("email"));
    const { error } = await createClient().auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=/reset-password`,
    });
    setState(error ? { error: error.message } : { sent: true });
  }

  return (
    <AuthShell title="Reset your password">
      {state.sent ? (
        <p className="rounded-2xl bg-green-50 px-4 py-3 text-sm text-green-800">If that email has an account, a reset link is on its way.</p>
      ) : (
        <form onSubmit={onSubmit} className="space-y-3">
          <input name="email" type="email" required placeholder="Email address" autoComplete="email"
            className="h-12 w-full rounded-full border border-[#E6DCCD] bg-white px-5 text-sm outline-none focus:border-[#FF4F26]" />
          {state.error && <p className="text-sm text-red-700">{state.error}</p>}
          <button disabled={state.busy} className="h-12 w-full rounded-full bg-[#FF4F26] text-sm font-semibold text-white disabled:opacity-60">
            {state.busy ? "Sending…" : "Send reset link"}
          </button>
        </form>
      )}
      <Link href="/login" className="mt-4 block text-center text-sm text-[#6B5B4E] hover:underline">Back to log in</Link>
    </AuthShell>
  );
}

export function AuthShell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <main className="grid min-h-screen place-items-center px-4" style={{ background: "linear-gradient(135deg, #F3E9DC 0%, #E8D9C2 100%)" }}>
      <div className="w-full max-w-[400px] rounded-[28px] bg-[#F9F4EE] p-8 shadow-[0_20px_60px_-20px_rgba(37,26,20,0.3)]">
        <h1 className="mb-5 text-center font-display text-[28px] font-extrabold uppercase leading-none tracking-tight text-[#251A14]">{title}</h1>
        {children}
      </div>
    </main>
  );
}
