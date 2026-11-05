"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LuPlus, LuX, LuChevronsUpDown } from "react-icons/lu";
import { Logo } from "@/components/logo";
import { footerNav, mainNav, type NavItem } from "@/lib/app-nav";
import type { Workspace } from "@/types/app";

type Props = { workspace: Workspace; open: boolean; onClose: () => void };

export function Sidebar({ workspace, open, onClose }: Props) {
  const pathname = usePathname();
  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  const renderItem = (item: NavItem) => {
    const Icon = item.icon;
    const active = isActive(item.href);
    const count = item.badge === "reviews" ? workspace.pendingReviews : 0;
    return (
      <li key={item.href}>
        <Link
          href={item.href}
          onClick={onClose}
          className={`relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
            active ? "bg-white/10 text-white" : "text-paper/60 hover:bg-white/5 hover:text-paper"
          }`}
        >
          {active && <span className="absolute -left-4 top-2 h-6 w-1 rounded-r bg-brand" />}
          <Icon size={18} />
          {item.label}
          {count > 0 && (
            <span className="ml-auto rounded-full bg-brand px-2 py-0.5 text-xs font-bold text-white">{count}</span>
          )}
        </Link>
      </li>
    );
  };

  return (
    <>
      {open && <div className="fixed inset-0 z-40 bg-ink/40 lg:hidden" onClick={onClose} />}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-brown px-4 py-5 text-paper transition-transform duration-200 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-2">
          <Link href="/dashboard" className="text-paper" onClick={onClose}>
            <Logo />
          </Link>
          <button className="lg:hidden" onClick={onClose} aria-label="Close menu">
            <LuX size={20} />
          </button>
        </div>

        <details className="group relative mt-6">
          <summary className="flex cursor-pointer list-none items-center gap-3 rounded-xl bg-white/5 px-3 py-2.5 text-sm [&::-webkit-details-marker]:hidden">
            <span className="grid h-7 w-7 place-items-center rounded-md bg-paper text-xs font-bold text-brown">A</span>
            <span className="font-semibold">All clients</span>
            <LuChevronsUpDown className="ml-auto opacity-60" size={16} />
          </summary>
          <ul className="absolute left-0 right-0 top-full z-10 mt-2 rounded-xl bg-white p-2 text-ink shadow-xl">
            {workspace.clients.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/clients/${c.id}`}
                  onClick={onClose}
                  className="flex items-center gap-3 rounded-lg px-2 py-2 text-sm hover:bg-paper"
                >
                  <span className="grid h-7 w-7 place-items-center rounded-md bg-paper-hero text-xs font-bold">{c.initials}</span>
                  {c.name}
                </Link>
              </li>
            ))}
          </ul>
        </details>

        <Link
          href="/campaigns/new"
          onClick={onClose}
          className="mt-4 flex items-center justify-center gap-2 rounded-xl bg-brand py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-hover"
        >
          <LuPlus size={16} /> New campaign
        </Link>

        <nav className="mt-6 flex-1 overflow-y-auto">
          <ul className="space-y-1">{mainNav.map(renderItem)}</ul>
        </nav>

        <ul className="space-y-1 border-t border-white/10 pt-4">{footerNav.map(renderItem)}</ul>

        <div className="mt-4 flex items-center gap-3 rounded-xl bg-white/5 px-3 py-3">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-brand text-sm font-bold text-white">
            {workspace.user.name[0]}
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold">{workspace.user.name}</p>
            <p className="text-xs text-paper/50">{workspace.user.role}</p>
          </div>
        </div>
      </aside>
    </>
  );
}