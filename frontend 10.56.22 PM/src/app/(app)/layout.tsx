import { AppShell } from "@/app/app-shell";
import { getWorkspace } from "@/lib/api/dashboard";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const workspace = await getWorkspace();
  // Auth guard goes here later: redirect to /login if there is no session.
  return <AppShell workspace={workspace}>{children}</AppShell>;
}