"use client";

import { useState } from "react";
import Link from "next/link";
import { Logo } from "@/components/logo";
import { site } from "@/lib/site";

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 px-4 pt-4">
      <nav className="mx-auto flex max-w-6xl items-center justify-between rounded-2xl border border-line bg-white/70 px-5 py-3 backdrop-blur-md">
        <Link href="/" aria-label={`${site.name} home`} className="text-ink">
          <Logo />
        </Link>

        <ul className="hidden items-center gap-8 md:flex">
          {site.nav.map((item) => (
            <li key={item.href}>
              <a href={item.href} className="text-sm font-medium text-muted transition-colors hover:text-ink">
                {item.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <Link href={site.loginHref} className="text-sm font-medium text-ink hover:text-brand">
            Log in
          </Link>
          <Link
            href={site.ctaHref}
            className="rounded-xl bg-ink px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand"
          >
            {site.ctaLabel}
          </Link>
        </div>

        <button
          type="button"
          className="md:hidden"
          aria-label="Toggle menu"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <span className="block h-0.5 w-6 bg-ink" />
          <span className="mt-1.5 block h-0.5 w-6 bg-ink" />
          <span className="mt-1.5 block h-0.5 w-6 bg-ink" />
        </button>
      </nav>

      {open && (
        <div className="mx-auto mt-2 max-w-6xl rounded-2xl border border-line bg-white p-5 md:hidden">
          <ul className="flex flex-col gap-4">
            {site.nav.map((item) => (
              <li key={item.href}>
                <a href={item.href} onClick={() => setOpen(false)} className="font-medium text-ink">
                  {item.label}
                </a>
              </li>
            ))}
            <li>
              <Link
                href={site.ctaHref}
                className="block rounded-xl bg-brand px-4 py-3 text-center font-semibold text-white"
              >
                {site.ctaLabel}
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}