import { cache } from "react";
import { config } from "@/lib/config";
import { dashboardMock, workspaceMock } from "@/mocks/dashboard";
import type { DashboardData, Workspace } from "@/types/app";

async function get<T>(path: string, mock: T): Promise<T> {
  if (config.useMocks) return mock;
  const res = await fetch(`${config.apiBaseUrl}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request to ${path} failed: ${res.status}`);
  return res.json();
}

// Endpoint paths are placeholders: agree on them with the backend team.
export const getWorkspace = cache(() => get<Workspace>("/api/workspace", workspaceMock));
export const getDashboard = cache(() => get<DashboardData>("/api/dashboard", dashboardMock));