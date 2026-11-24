export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  useMocks: process.env.NEXT_PUBLIC_USE_MOCKS === "true",
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
  // Supabase now calls this the "publishable" key; older projects call it the "anon" key. Either works.
  supabaseAnonKey: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
};
