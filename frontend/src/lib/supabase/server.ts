import "server-only";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { connection } from "next/server";
import { config } from "@/lib/config";

/** Supabase client for Server Components and Route Handlers. Reads the session from cookies. */
export async function createClient() {
  // The Supabase client reads the clock while loading the session, which Cache Components only
  // allows at request time, not while prerendering.
  await connection();
  const cookieStore = await cookies();
  return createServerClient(config.supabaseUrl, config.supabaseAnonKey, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
        } catch {
          // Server Components can't set cookies. The proxy refreshes the session instead.
        }
      },
    },
  });
}
