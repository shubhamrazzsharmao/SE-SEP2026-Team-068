"use server";

import { refresh } from "next/cache";
import { redirect } from "next/navigation";
import { api, BackendError } from "@/lib/api/client";
import type { BrandOut, CampaignOut, GenerateOut, Platform } from "@/types/api";

// Every action returns ActionState so forms can show the backend's error message inline.
// Authorisation is enforced by the backend on every call (the user's token is sent with it).
export type ActionState = { ok?: boolean; error?: string; message?: string; at?: number };

async function run(fn: () => Promise<unknown>, message?: string): Promise<ActionState> {
  try {
    await fn();
  } catch (e) {
    if (e instanceof BackendError) return { error: e.message, at: Date.now() };
    throw e;
  }
  refresh();
  return { ok: true, message, at: Date.now() };
}

const str = (fd: FormData, key: string) => String(fd.get(key) ?? "").trim();
const optional = (fd: FormData, key: string) => str(fd, key) || null;
const terms = (fd: FormData, key: string) =>
  str(fd, key).split(/[,\n]/).map((t) => t.trim()).filter(Boolean);
const json = (body: unknown) => ({ body: JSON.stringify(body) });

// ---------------------------------------------------------------- brands (clients)
export async function createBrand(_: ActionState, fd: FormData): Promise<ActionState> {
  let id: number | undefined;
  const state = await run(async () => {
    const brand = await api<BrandOut>("/brands", {
      method: "POST",
      ...json({ name: str(fd, "name"), tone: str(fd, "tone"), preferred_terms: terms(fd, "preferred_terms"), avoided_terms: terms(fd, "avoided_terms") }),
    });
    id = brand.id;
  });
  if (state.ok && id) redirect(`/clients/${id}`);
  return state;
}

export async function updateBrand(brandId: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/brands/${brandId}`, {
    method: "PATCH",
    ...json({ name: str(fd, "name"), tone: str(fd, "tone"), preferred_terms: terms(fd, "preferred_terms"), avoided_terms: terms(fd, "avoided_terms") }),
  }), "Brand guidelines saved.");
}

// ---------------------------------------------------------------- campaigns and members
export async function createCampaign(_: ActionState, fd: FormData): Promise<ActionState> {
  let id: number | undefined;
  const state = await run(async () => {
    const c = await api<CampaignOut>("/campaigns", {
      method: "POST",
      ...json({ brand_id: Number(fd.get("brand_id")), name: str(fd, "name"), description: optional(fd, "description") }),
    });
    id = c.id;
  });
  if (state.ok && id) redirect(`/campaigns/${id}`);
  return state;
}

export async function addMember(campaignId: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/campaigns/${campaignId}/members`, {
    method: "POST",
    ...json({ email: str(fd, "email"), member_role: str(fd, "member_role") }),
  }), "Member added.");
}

export async function removeMember(campaignId: number, userId: string): Promise<ActionState> {
  return run(() => api(`/campaigns/${campaignId}/members/${userId}`, { method: "DELETE" }));
}

// ---------------------------------------------------------------- briefs and generation
export async function createBrief(campaignId: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/campaigns/${campaignId}/briefs`, {
    method: "POST",
    ...json({
      topic: str(fd, "topic"),
      objective: str(fd, "objective"),
      platforms: fd.getAll("platforms").map(String) as Platform[],
      target_audience: optional(fd, "target_audience"),
      key_messages: optional(fd, "key_messages"),
      tone: optional(fd, "tone"),
    }),
  }), "Brief saved. Generate content when you're ready.");
}

export async function generateContent(briefId: number): Promise<ActionState> {
  let count = 0;
  const state = await run(async () => {
    count = (await api<GenerateOut>(`/briefs/${briefId}/generate`, { method: "POST" })).pieces.length;
  });
  return state.ok ? { ...state, message: `Generated ${count} piece${count === 1 ? "" : "s"}. They're waiting for review.` } : state;
}

// ---------------------------------------------------------------- content
export async function editContent(pieceId: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/content/${pieceId}`, { method: "PATCH", ...json({ body: str(fd, "body") }) }),
    "Saved as a new version. It needs review again.");
}

export async function deleteContent(pieceId: number, campaignId: number): Promise<ActionState> {
  const state = await run(() => api(`/content/${pieceId}?confirm=true`, { method: "DELETE" }));
  if (state.ok) redirect(`/campaigns/${campaignId}`);
  return state;
}

export async function addComment(pieceId: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/content/${pieceId}/comments`, { method: "POST", ...json({ body: str(fd, "body") }) }));
}

// ---------------------------------------------------------------- review (reviewer role only)
export async function approve(pieceId: number, versionNo: number): Promise<ActionState> {
  return run(() => api(`/content/${pieceId}/approve`, { method: "POST", ...json({ version_no: versionNo }) }), "Approved.");
}

export async function reject(pieceId: number, versionNo: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/content/${pieceId}/reject`, { method: "POST", ...json({ version_no: versionNo, reason: str(fd, "reason") }) }), "Rejected.");
}

export async function requestChanges(pieceId: number, versionNo: number, _: ActionState, fd: FormData): Promise<ActionState> {
  return run(() => api(`/content/${pieceId}/request-changes`, { method: "POST", ...json({ version_no: versionNo, feedback: str(fd, "feedback") }) }),
    "Feedback sent. A revised version was generated.");
}
