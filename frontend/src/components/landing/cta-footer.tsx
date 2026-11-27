import Link from "next/link";

import { Logo } from "@/components/logo";
import { site } from "@/lib/site";

/**
 * Landing page closing section: a final call to action followed by footer link columns.
 *
 * TODO:
 * - Add the copy to `site` in src/lib/site.ts (a `cta` block with title lines and a button,
 *   and a `footer` block with link columns) instead of hard-coding it here.
 * - Render <CtaFooter /> after <Faq /> in src/app/page.tsx.
 * - Reference design: components/landing/cta-footer.tsx in the old mock frontend.
 */
const tiles = ["bg-brand", "bg-paper/20", "bg-accent", "bg-paper/10", "bg-paper/30", "bg-brand/60", "bg-paper/10", "bg-paper/20"];

export function CtaFooter() {
  const { cta, footer } = site;

  return (
    <section className="relative overflow-hidden bg-brown text-paper">
      <div className="mx-auto max-w-6xl px-6 pb-12 pt-24">
        <div className="relative">
          <div aria-hidden className="mb-8 flex gap-2">
            {tiles.map((tile, index) => (
              <span key={index} className={`h-8 w-8 rounded-md ${tile}`} />
            ))}
          </div>
          <h2 className="display text-[clamp(2.4rem,6vw,5rem)]">
            {cta.title.map((line, index) => (
              <span key={line} className={`block ${index === cta.title.length - 1 ? "text-brand" : ""}`}>
                {line}
              </span>
            ))}
          </h2>
          <p className="mt-6 max-w-md text-lg text-paper/70">{cta.sub}</p>
          <Link
            href={site.ctaHref}
            className="mt-8 inline-flex items-center gap-3 rounded-xl bg-brand py-3 pl-6 pr-3 font-semibold text-white transition-colors hover:bg-brand-hover"
          >
            {site.ctaLabel}
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/20">↗</span>
          </Link>
        </div>

        <footer className="mt-24 grid gap-10 border-t border-paper/15 pt-10 md:grid-cols-[1.5fr_1fr_1fr]">
          <div>
            <Logo className="text-paper" />
            <p className="mt-4 max-w-xs text-sm text-paper/60">{footer.blurb}</p>
          </div>
          {footer.columns.map((column) => (
            <div key={column.title}>
              <p className="text-sm font-semibold">{column.title}</p>
              <ul className="mt-4 space-y-3 text-sm text-paper/60">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="transition-colors hover:text-brand">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </footer>

        <p className="mt-12 text-xs text-paper/40">
          © 2026 {site.name}. All rights reserved.
        </p>
      </div>
    </section>
  );
}
