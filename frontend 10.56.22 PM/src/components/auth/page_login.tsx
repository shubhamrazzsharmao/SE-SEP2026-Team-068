import type { Metadata } from "next";
import { AuthCard } from "@/components/auth/auth-card";

export const metadata: Metadata = { title: "Log in · Mosaiq" };

export default function LoginPage() {
  return <AuthCard initialMode="login" />;
}
