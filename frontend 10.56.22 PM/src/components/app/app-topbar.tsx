"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

export type Brand = { id: string; name: string };

function initials(name: string) {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0]?.toUpperCase())
      .join("") || "CP"
  );
}

function Tile({ label }: { label: string }) {
  return (
    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#E8DCCB] text-[10px] font-bold text-[#6B5B4E]">
      {label}
    </span>
  );
}

function PlusIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

export function AppTopbar({ brands = [], activeId }: { brands?: Brand[]; activeId?: string }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  const active = brands.find((b) => b.id === activeId);
  const filtered = brands.filter((b) => b.name.toLowerCase().includes(q.toLowerCase()));

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <header className="relative z-30 flex h-16 items-center justify-between border-b border-[#E6DCCD] bg-[#F9F4EE]/80 px-4 backdrop-blur">
      <div ref={ref} className="relative flex items-center gap-3">
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          className="flex h-11 items-center gap-3 rounded-xl bg-white/70 pl-2 pr-3 text-[14px] font-medium text-[#251A14] transition hover:bg-white"
        >
          <Tile label={active ? initials(active.name) : "CP"} />
          <span>{active?.name ?? "Create profile"}</span>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={`transition-transform ${open ? "rotate-180" : ""}`}
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>
        <span className="rounded-full bg-[#E3E6F8] px-2.5 py-1 text-[11px] font-semibold text-[#4A55A8]">Beta</span>

        {open && (
          <div className="absolute left-0 top-[calc(100%+10px)] flex min-h-[380px] w-[340px] flex-col overflow-hidden rounded-2xl border border-[#E6DCCD] bg-white shadow-[0_24px_60px_-20px_rgba(37,26,20,0.35)]">
            <div className="flex items-center gap-2 border-b border-[#FF4F26] px-4 py-3">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8A7B6D" strokeWidth="2" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <path d="m20 20-3.5-3.5" />
              </svg>
              <input
                autoFocus
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search..."
                className="w-full bg-transparent text-[14px] text-[#251A14] outline-none placeholder:text-[#8A7B6D]"
              />
            </div>

            <div className="flex-1 px-4 pt-4">
              <p className="font-display text-[13px] font-extrabold uppercase tracking-tight text-[#251A14]">Brand profiles</p>
              {filtered.length === 0 ? (
                <p className="mt-3 text-[13px] text-[#8A7B6D]">No brand profiles found</p>
              ) : (
                <ul className="mt-2 space-y-1">
                  {filtered.map((b) => (
                    <li key={b.id}>
                      <Link
                        href={`/dashboard/brands/${b.id}`}
                        className="flex items-center gap-3 rounded-xl px-2 py-2 text-[14px] text-[#251A14] transition hover:bg-[#F3E9DC]"
                      >
                        <Tile label={initials(b.name)} />
                        {b.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="border-t border-[#EFE4D4] p-3">
              <Link
                href="/dashboard/brands/new"
                onClick={() => setOpen(false)}
                className="flex h-10 items-center justify-center gap-2 rounded-xl bg-[#FFE7DF] text-[13px] font-semibold text-[#D83A12] transition hover:bg-[#FFD9CC]"
              >
                <PlusIcon size={15} />
                Create brand profile
              </Link>
            </div>
          </div>
        )}
      </div>

      <Link
        href="/dashboard/brands/new"
        className="flex h-11 items-center gap-2 rounded-full bg-[#251A14] px-5 text-[14px] font-semibold text-white transition hover:bg-black"
      >
        <PlusIcon />
        New brand
      </Link>
    </header>
  );
}
