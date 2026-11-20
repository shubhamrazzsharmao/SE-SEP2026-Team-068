import { Suspense } from "react";
import { AppShell } from "@/app/app-shell";
import { getWorkspace } from "@/lib/api/dashboard";

// Signed-out users are redirected to /login by src/proxy.ts before this renders.
// The workspace is read per request (session cookie), so it streams in behind Suspense.
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="min-h-screen bg-paper" />}>
      <Shell>{children}</Shell>
    </Suspense>
  );
}

async function Shell({ children }: { children: React.ReactNode }) {
  const workspace = await getWorkspace();
  return <AppShell workspace={workspace}>{children}</AppShell>;
}
