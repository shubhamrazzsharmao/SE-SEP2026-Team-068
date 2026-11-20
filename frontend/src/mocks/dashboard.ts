// Used when NEXT_PUBLIC_USE_MOCKS=true (UI work without the backend or Supabase).
import type { DashboardData, Workspace } from "@/types/app";

export const workspaceMock: Workspace = {
  user: { name: "Shubham", email: "shubham@example.com" },
  clients: [
    { id: "1", name: "Nova Fitness", initials: "NF" },
    { id: "2", name: "Orchid Cafe", initials: "OC" },
    { id: "3", name: "Kite Analytics", initials: "KA" },
  ],
  pendingReviews: 3,
};

export const dashboardMock: DashboardData = {
  stats: { draft: 0, pending_review: 3, approved: 9, rejected: 2, total: 14 },
  campaigns: [
    { id: "1", clientName: "Nova Fitness", title: "Winter Challenge launch", stage: "In review", myRole: "owner", approved: 7, total: 10 },
    { id: "2", clientName: "Orchid Cafe", title: "Festive menu launch", stage: "Complete", myRole: "reviewer", approved: 2, total: 4 },
    { id: "3", clientName: "Kite Analytics", title: "Q4 product report", stage: "Not started", myRole: "creator", approved: 0, total: 0 },
  ],
  reviewQueue: [
    { id: "11", campaignId: "1", platform: "linkedin", clientName: "Nova Fitness", campaign: "Winter Challenge launch", snippet: "Most people quit by week 3. Here's how our challenge fixes that.", status: "pending_review", version: 2, updated: "12 min ago" },
    { id: "12", campaignId: "1", platform: "instagram", clientName: "Nova Fitness", campaign: "Winter Challenge launch", snippet: "Week 1 starts Monday. Are you in?", status: "pending_review", version: 1, updated: "1 hr ago" },
    { id: "13", campaignId: "1", platform: "facebook", clientName: "Nova Fitness", campaign: "Winter Challenge launch", snippet: "Bring a friend, double the streak.", status: "pending_review", version: 1, updated: "Yesterday" },
  ],
  activity: [
    { id: "a1", kind: "approved", text: "Dana approved a post", detail: "Nova Fitness · Winter Challenge launch · v3", time: "10 min ago" },
    { id: "a2", kind: "generated", text: "An Instagram post was generated", detail: "Nova Fitness · Winter Challenge launch · v1", time: "25 min ago" },
    { id: "a3", kind: "changes", text: "Dana requested changes", detail: "Nova Fitness · Winter Challenge launch · v1", time: "3 hr ago" },
    { id: "a4", kind: "other", text: "Shubham wrote a brief: Week 1 kickoff", detail: "Nova Fitness · Winter Challenge launch", time: "5 hr ago" },
  ],
  onboarding: [
    { label: "Add a client brand", href: "/clients", done: true },
    { label: "Create a campaign", href: "/campaigns/new", done: true },
    { label: "Generate content", href: "/campaigns", done: true },
    { label: "Approve a post", href: "/reviews", done: false },
  ],
};
