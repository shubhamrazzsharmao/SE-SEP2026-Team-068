import "server-only";
import { notFound } from "next/navigation";
import { config } from "@/lib/config";
import { createClient } from "@/lib/supabase/server";
import type { ApiError } from "@/types/api";

export class BackendError extends Error {
  constructor(public status: number, public code: string, detail: string) {
    super(detail);
    this.name = "BackendError";
  }
}

/**
 * Server-side call to the FastAPI backend (`/api/v1/...`) with the user's Supabase access token.
 * Every backend error has the shape `{ detail, code }`; it is thrown as a BackendError.
 */
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (!token) throw new BackendError(401, "UNAUTHORIZED", "You are not signed in.");

  let res: Response;
  try {
    res = await fetch(`${config.apiBaseUrl}/api/v1${path}`, {
      ...init,
      cache: "no-store",
      headers: { ...init.headers, Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    });
  } catch {
    throw new BackendError(503, "BACKEND_UNREACHABLE", `Can't reach the backend at ${config.apiBaseUrl}. Is it running?`);
  }

  // A page reading something that doesn't exist (or that the user can't see: the backend
  // answers 404 to non-members) shows the not-found page. Mutations get the error instead.
  if (res.status === 404 && (init.method ?? "GET") === "GET") notFound();

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiError | null;
    // 422 responses list field problems: show them, not just "Validation failed."
    const fields = Array.isArray(body?.errors)
      ? (body.errors as { field?: string; message?: string }[])
          .map((e) => (e.field ? `${e.field}: ${e.message}` : e.message))
          .join("; ")
      : "";
    const detail = body?.detail ?? `Request to ${path} failed (${res.status}).`;
    throw new BackendError(res.status, body?.code ?? "ERROR", fields ? `${detail} ${fields}` : detail);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}
