"use server";

import { createClient } from "@/lib/supabase/server";

// Sign-in and sign-out happen in the browser (supabase-js), so the browser reports them here
// and they are printed in the `npm run dev` terminal. The user is read from the verified
// session cookie; anything the browser sends itself is marked "(reported by browser)".

export type AuthEvent = "login" | "logout" | "signup" | "login_failed" | "signup_failed";

export async function logAuthEvent(event: AuthEvent, info?: { email?: string; reason?: string; method?: string }) {
  const supabase = await createClient();
  const { data } = await supabase.auth.getClaims();
  const claims = data?.claims;
  const user = claims ? `${claims.email} (${claims.sub})` : `${info?.email ?? "unknown"} (reported by browser)`;
  const extra = [info?.method && `method=${info.method}`, info?.reason && `reason="${info.reason}"`].filter(Boolean).join(" ");
  const line = `[auth] ${new Date().toISOString()} ${event.toUpperCase()} ${user}${extra ? ` ${extra}` : ""}`;
  if (event.endsWith("_failed")) console.warn(line);
  else console.info(line);
}
