"use client";

import { useState } from "react";
import { Sidebar } from "./sidebar";
import { TopBar } from "./topbar";
import type { Workspace } from "@/types/app";

export function AppShell({ workspace, children }: { workspace: Workspace; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-paper">
      <Sidebar workspace={workspace} open={open} onClose={() => setOpen(false)} />
      <div className="lg:pl-64">
        <TopBar onMenu={() => setOpen(true)} initial={workspace.user.name[0]} />
        <main className="px-6 pb-16 pt-8 lg:px-10">{children}</main>
      </div>
    </div>
  );
}