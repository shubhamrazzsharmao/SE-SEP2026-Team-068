export type Status = "draft" | "in_review" | "changes_requested" | "approved" | "rejected" | "plan_changed";
export type Platform = "linkedin" | "instagram" | "blog";
export type Stage = "Planning" | "Generating" | "In review" | "Complete";

export type Client = { id: string; name: string; initials: string };
export type Workspace = { user: { name: string; role: string }; clients: Client[]; pendingReviews: number };

export type Campaign = { id: string; clientName: string; title: string; stage: Stage; approved: number; total: number; due: string };
export type ReviewItem = { id: string; platform: Platform; clientName: string; campaign: string; snippet: string; status: Status; updated: string };
export type ActivityItem = { id: string; text: string; detail: string; time: string; kind: "approved" | "generated" | "changes" | "plan" };
export type OnboardingStep = { label: string; href: string; done: boolean };

export type DashboardData = {
  stats: { approved: number; total: number; inReview: number; changesRequested: number; plansToApprove: number };
  campaigns: Campaign[];
  reviewQueue: ReviewItem[];
  activity: ActivityItem[];
  onboarding: OnboardingStep[];
};