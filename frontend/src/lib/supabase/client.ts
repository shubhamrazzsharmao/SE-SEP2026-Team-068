import { createBrowserClient } from "@supabase/ssr";
import { config } from "@/lib/config";

/** Supabase client for Client Components (login, signup, sign out). */
export function createClient() {
  return createBrowserClient(config.supabaseUrl, config.supabaseAnonKey);
}
