import type { IconType } from "react-icons";
import {
  LuLayoutDashboard, LuUsers, LuFolderKanban, LuCalendarDays,
  LuClipboardCheck, LuLightbulb, LuLibrary, LuSettings, LuLifeBuoy, LuPlus,
} from "react-icons/lu";

export type NavItem = { label: string; href: string; icon: IconType; badge?: "reviews" };

export const mainNav: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LuLayoutDashboard },
  { label: "Brand setup", href: "/brand-setup", icon: LuPlus },
  { label: "Clients", href: "/clients", icon: LuUsers },
  { label: "Campaigns", href: "/campaigns", icon: LuFolderKanban },
  { label: "Calendar", href: "/calendar", icon: LuCalendarDays },
  { label: "Reviews", href: "/reviews", icon: LuClipboardCheck, badge: "reviews" },
  { label: "Ideas", href: "/ideas", icon: LuLightbulb },
  { label: "Library", href: "/library", icon: LuLibrary },
];

export const footerNav: NavItem[] = [
  { label: "Settings", href: "/settings", icon: LuSettings },
  { label: "Help", href: "/help", icon: LuLifeBuoy },
];