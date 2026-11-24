import type { BriefStatus, MemberRole, Platform } from "@/types/api";

export const ROLE_LABEL: Record<MemberRole, string> = {
  owner: "Owner",
  creator: "Creator",
  reviewer: "Reviewer",
  brand_manager: "Brand manager",
};

export const PLATFORM_LABEL: Record<Platform, string> = {
  blog: "Blog",
  linkedin: "LinkedIn",
  facebook: "Facebook",
  instagram: "Instagram",
};

export const PLATFORMS: Platform[] = ["linkedin", "instagram", "facebook", "blog"];

export const BRIEF_STATUS: Record<BriefStatus, { label: string; cls: string }> = {
  draft: { label: "Draft", cls: "bg-slate-100 text-slate-700" },
  generating: { label: "Generating", cls: "bg-brand/10 text-brand" },
  generated: { label: "Generated", cls: "bg-green-100 text-green-700" },
};

export function formatDate(iso: string) {
  return new Date(iso).toLocaleString("en", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

export function snippet(body: string, max = 140) {
  const line = body.split("\n").map((l) => l.replace(/^#+\s*/, "").trim()).find(Boolean) ?? "";
  return line.length > max ? `${line.slice(0, max - 1)}…` : line;
}
