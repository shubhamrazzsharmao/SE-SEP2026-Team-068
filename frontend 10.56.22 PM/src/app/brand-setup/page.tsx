import type { Metadata } from "next";
import { AppTopbar } from "@/components/app/app-topbar";
import { BrandSetup } from "@/components/brand/brand-setup";

export const metadata: Metadata = { title: "New brand profile · Mosaiq" };

const TILES = ["#FF7A57", "#E8DCCB", "#8F9BDB", "#EFE4D4", "#EFE4D4", "#251A14", "#E8DCCB", "#FF4F26", "#E8DCCB", "#EFE4D4", "#B7B3CF", "#EFE4D4"];

export default function NewBrandPage() {
  return (
    <main className="relative min-h-screen overflow-hidden" style={{ background: "linear-gradient(135deg, #F9F4EE 0%, #F1E6D6 100%)" }}>
      <div aria-hidden className="pointer-events-none absolute -right-6 top-14 hidden grid-cols-4 gap-2 opacity-60 lg:grid">
        {TILES.map((c, i) => (
          <span key={i} className="h-12 w-12 rounded-lg" style={{ background: c }} />
        ))}
      </div>
      {/* Brands come from your API later; empty list shows "No brand profiles found". */}
      <AppTopbar brands={[]} />
      <BrandSetup />
    </main>
  );
}