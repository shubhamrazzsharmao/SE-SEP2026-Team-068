import type { DashboardData, Workspace } from "@/types/app";

export const workspaceMock: Workspace = {
  user: { name: "Shubham", role: "Agency Owner" },
  clients: [
    { id: "nova", name: "Nova Fitness", initials: "NF" },
    { id: "orchid", name: "Orchid Cafe", initials: "OC" },
    { id: "kite", name: "Kite Analytics", initials: "KA" },
  ],
  pendingReviews: 3,
};

export const dashboardMock: DashboardData = {
  stats: { approved: 9, total: 30, inReview: 3, changesRequested: 2, plansToApprove: 1 },
  campaigns: [
    { id: "c1", clientName: "Nova Fitness", title: "Winter Challenge launch", stage: "In review", approved: 7, total: 12, due: "Nov 18" },
    { id: "c2", clientName: "Orchid Cafe", title: "Festive menu launch", stage: "Generating", approved: 2, total: 8, due: "Nov 12" },
    { id: "c3", clientName: "Kite Analytics", title: "Q4 product report", stage: "Planning", approved: 0, total: 10, due: "Nov 25" },
  ],
  reviewQueue: [
    { id: "r1", platform: "linkedin", clientName: "Nova Fitness", campaign: "Winter Challenge launch", snippet: "Most people quit by week 3. Here's how our challenge fixes that.", status: "in_review", updated: "12 min ago" },
    { id: "r2", platform: "instagram", clientName: "Nova Fitness", campaign: "Winter Challenge launch", snippet: "Week 1 starts Monday. Are you in?", status: "in_review", updated: "1 hr ago" },
    { id: "r3", platform: "blog", clientName: "Orchid Cafe", campaign: "Festive menu launch", snippet: "The story behind every dish on our festive menu", status: "changes_requested", updated: "3 hr ago" },
    { id: "r4", platform: "instagram", clientName: "Orchid Cafe", campaign: "Festive menu launch", snippet: "Chai, but make it festive.", status: "in_review", updated: "Yesterday" },
  ],
  activity: [
    { id: "a1", kind: "approved", text: "Dana approved a LinkedIn post", detail: "Nova Fitness · v3", time: "10 min ago" },
    { id: "a2", kind: "generated", text: "Instagram post 4 generated", detail: "Orchid Cafe · v1", time: "25 min ago" },
    { id: "a3", kind: "changes", text: "Changes requested on a blog post", detail: "Orchid Cafe · v2", time: "3 hr ago" },
    { id: "a4", kind: "plan", text: "Plan v2 is waiting for approval", detail: "Kite Analytics", time: "5 hr ago" },
  ],
  onboarding: [
    { label: "Add a client", href: "/clients", done: true },
    { label: "Add a brand profile", href: "/clients", done: true },
    { label: "Upload a source", href: "/campaigns/new", done: false },
    { label: "Approve a plan", href: "/campaigns", done: false },
  ],
};