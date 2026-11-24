import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { config as appConfig } from "@/lib/config";

// Routes that need a signed-in user. Everything else (landing page, login, signup) is public.
const PROTECTED = ["/dashboard", "/clients", "/campaigns", "/calendar", "/reviews", "/ideas", "/library", "/settings", "/help"];
const AUTH_PAGES = ["/login", "/signup"];

const matches = (path: string, list: string[]) => list.some((p) => path === p || path.startsWith(`${p}/`));

/**
 * Refreshes the Supabase session cookie on every request and does an optimistic auth redirect.
 * The backend still verifies the token on every API call; this only decides which page to show.
 */
export async function proxy(request: NextRequest) {
  if (appConfig.useMocks) return NextResponse.next();

  let response = NextResponse.next({ request });
  const supabase = createServerClient(appConfig.supabaseUrl, appConfig.supabaseAnonKey, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll(cookiesToSet, headers) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        Object.entries(headers ?? {}).forEach(([k, v]) => response.headers.set(k, v));
      },
    },
  });

  // getClaims() verifies the JWT (and refreshes an expired session); don't run code between
  // createServerClient and this call.
  const { data } = await supabase.auth.getClaims();
  const signedIn = Boolean(data?.claims);
  const path = request.nextUrl.pathname;

  if (!signedIn && matches(path, PROTECTED)) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.search = "";
    return NextResponse.redirect(url);
  }
  if (signedIn && matches(path, AUTH_PAGES)) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    url.search = "";
    return NextResponse.redirect(url);
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)"],
};
