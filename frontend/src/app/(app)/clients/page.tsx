import type { Metadata } from "next";
import { BrandSetup } from "@/components/brand/brand-setup";

export const metadata: Metadata = { title: "Brand setup · Mosaiq" };

export default function BrandSetupPage() {
  return (
    <main className="mx-auto min-h-[calc(100vh-4rem)] w-full max-w-6xl">
      <BrandSetup />
    </main>
  );
}
