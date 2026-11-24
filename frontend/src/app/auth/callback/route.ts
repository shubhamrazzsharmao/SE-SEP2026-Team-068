import type { EmailOtpType } from "@supabase/supabase-js";
import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";

/**
 * Landing URL for Supabase email confirmation links and OAuth (Google / LinkedIn) sign-in.
 * Add http://localhost:3000/auth/callback to Supabase -> Authentication -> URL Configuration.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");
  const tokenHash = searchParams.get("token_hash");
  const type = searchParams.get("type") as EmailOtpType | null;

  const supabase = await createClient();
  let result: { error: { message: string } | null; data: { user: { id: string; email?: string } | null } } | null = null;
  if (code) {
    result = await supabase.auth.exchangeCodeForSession(code);
  } else if (tokenHash && type) {
    result = await supabase.auth.verifyOtp({ token_hash: tokenHash, type });
  }
  const ok = Boolean(result && !result.error);
  const how = code ? "oauth/email link" : `email link (${type})`;
  if (ok && result?.data.user) {
    console.info(`[auth] ${new Date().toISOString()} LOGIN ${result.data.user.email} (${result.data.user.id}) method=${how}`);
  } else {
    console.warn(`[auth] ${new Date().toISOString()} LOGIN_FAILED via ${how}: ${result?.error?.message ?? "missing code"}`);
  }
  // Only same-site paths, so the link can't redirect to another website.
  const next = searchParams.get("next");
  const target = next?.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";
  return NextResponse.redirect(new URL(ok ? target : "/login?error=auth", origin));
}
