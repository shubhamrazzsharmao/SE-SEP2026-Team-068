// View models used by the UI. Built from the backend types in ./api.ts by src/lib/api/dashboard.ts.
import type { ContentStatus, MemberRole, Platform, StatusCounts } from "./api";

export type { ContentStatus as Status, Platform } from "./api";
export type Stage = "Not started" | "In review" | "Complete";

export type Client = { id: string; name: string; initials: string };
export type Workspace = { user: { name: string; email: string }; clients: Client[]; pendingReviews: number };

export type Campaign = {
  id: string;
  clientName: string;
  title: string;
  stage: Stage;
  myRole: MemberRole;
  approved: number;
  total: number;
};
export type ReviewItem = {
  id: string;
  campaignId: string;
  platform: Platform;
  clientName: string;
  campaign: string;
  snippet: string;
  status: ContentStatus;
  version: number;
  updated: string;
};
export type ActivityItem = { id: string; text: string; detail: string; time: string; kind: "approved" | "generated" | "changes" | "other" };
export type OnboardingStep = { label: string; href: string; done: boolean };

export type DashboardData = {
  stats: StatusCounts & { total: number };
  campaigns: Campaign[];
  reviewQueue: ReviewItem[];
  activity: ActivityItem[];
  onboarding: OnboardingStep[];
};
