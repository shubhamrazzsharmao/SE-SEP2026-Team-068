"use client";

import Link from "next/link";
import { site } from "@/lib/site";
import { HeroMosaic } from "./hero-mosaic";

export function Hero() {
  const { hero } = site;
  const last = hero.headline.length - 1;

  return (
    <section className="paper relative -mt-20 overflow-x-clip pb-20 pt-20">
      <div className="mx-auto grid max-w-6xl items-center gap-16 px-6 pb-16 pt-14 lg:grid-cols-[1.2fr_1fr] lg:pt-20">
        <div>
          <p className="inline-block rounded-full border border-ink/15 bg-white/60 px-4 py-1.5 text-sm font-medium">
            {hero.eyebrow}
          </p>

          <h1 className="display mt-6 text-[clamp(2.4rem,5.2vw,4.6rem)]">
            {hero.headline.map((line, i) => (
              <span key={line} className={`block ${i === last ? "text-brand" : ""}`}>
                {line}
              </span>
            ))}
          </h1>

          <p className="mt-6 max-w-md text-lg text-ink/80">{hero.sub}</p>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Link
              href={site.ctaHref}
              className="inline-flex items-center gap-3 rounded-xl bg-brand py-3 pl-6 pr-3 font-semibold text-white transition-colors hover:bg-brand-hover"
            >
              {site.ctaLabel}
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/20">↗</span>
            </Link>
            <a href={hero.secondaryHref} className="font-semibold underline underline-offset-4 hover:text-brand">
              {hero.secondaryLabel}
            </a>
          </div>
        </div>

        <div className="relative min-h-[480px]">
          <HeroMosaic />
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 pb-16 pt-6">
        <div className="grid gap-6 border-t border-ink/15 pt-8 md:grid-cols-3">
          {hero.points.map((p) => (
            <div key={p.title}>
              <p className="font-semibold">{p.title}</p>
              <p className="mt-1 text-sm text-muted">{p.text}</p>
            </div>
          ))}
        </div>
      </div>
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-0 h-32"
        style={{ background: "linear-gradient(to bottom, transparent, var(--color-paper))" }}
      />
    </section>
  );
}