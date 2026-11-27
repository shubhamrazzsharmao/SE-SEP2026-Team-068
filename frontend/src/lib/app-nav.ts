import type { IconType } from "react-icons";
import { LuClipboardCheck, LuFolderKanban, LuLayoutDashboard, LuUsers } from "react-icons/lu";

export type NavItem = { label: string; href: string; icon: IconType; badge?: "reviews" };

// Only sections the backend supports today. Calendar, Ideas, Library and Settings come back
// when their endpoints exist (see backend/README.md "Not in Sprint 1").
export const mainNav: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LuLayoutDashboard },
  { label: "Brand setup", href: "/clients", icon: LuUsers },
  { label: "Campaigns", href: "/campaigns", icon: LuFolderKanban },
  { label: "Reviews", href: "/reviews", icon: LuClipboardCheck, badge: "reviews" },
];

export const footerNav: NavItem[] = [];
