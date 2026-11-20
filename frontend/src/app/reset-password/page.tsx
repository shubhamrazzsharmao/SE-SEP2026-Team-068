"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { AuthShell } from "../forgot-password/page";

// Reached from the reset email via /auth/callback, which signs the user in first.
export default function ResetPasswordPage() {
  const router = useRouter();
  const [state, setState] = useState<{ busy?: boolean; error?: string }>({});

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setState({ busy: true });
    const password = String(new FormData(e.currentTarget).get("password"));
    const { error } = await createClient().auth.updateUser({ password });
    if (error) return setState({ error: error.message });
    router.replace("/dashboard");
    router.refresh();
  }

  return (
    <AuthShell title="Choose a new password">
      <form onSubmit={onSubmit} className="space-y-3">
        <input name="password" type="password" required minLength={8} placeholder="New password (8+ characters)" autoComplete="new-password"
          className="h-12 w-full rounded-full border border-[#E6DCCD] bg-white px-5 text-sm outline-none focus:border-[#FF4F26]" />
        {state.error && <p className="text-sm text-red-700">{state.error}</p>}
        <button disabled={state.busy} className="h-12 w-full rounded-full bg-[#FF4F26] text-sm font-semibold text-white disabled:opacity-60">
          {state.busy ? "Saving…" : "Save password"}
        </button>
      </form>
    </AuthShell>
  );
}
