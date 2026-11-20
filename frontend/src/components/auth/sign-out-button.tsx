"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { LuLogOut } from "react-icons/lu";
import { logAuthEvent } from "@/lib/auth-log";
import { createClient } from "@/lib/supabase/client";

export function SignOutButton() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function signOut() {
    setBusy(true);
    await logAuthEvent("logout"); // before signOut, while the session still says who it is
    await createClient().auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={signOut}
      disabled={busy}
      aria-label="Sign out"
      title="Sign out"
      className="ml-auto grid h-8 w-8 place-items-center rounded-lg text-paper/60 transition-colors hover:bg-white/10 hover:text-paper disabled:opacity-50"
    >
      <LuLogOut size={16} />
    </button>
  );
}
