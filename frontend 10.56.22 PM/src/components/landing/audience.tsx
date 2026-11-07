import { site } from "@/lib/site";

const a = site.audience;

export function Audience() {
  return (
    <section id="audience" className="fade-top bg-paper py-24 [--from:var(--color-tint)]">
      <div className="mx-auto max-w-6xl px-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-brand">{a.eyebrow}</p>
        <h2 className="display mt-3 max-w-3xl text-[clamp(2rem,4vw,3.4rem)]">{a.title}</h2>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {a.items.map((it, i) => (
            <div
              key={it.role}
              className={`drop-shadow-md transition-transform duration-200 hover:-translate-y-2 ${i === 1 ? "md:mt-8" : ""}`}
            >
              <div className={`ticket flex h-full min-h-[360px] flex-col rounded-3xl p-8 ${it.bg}`}>
                <p className="text-xs font-semibold uppercase tracking-widest opacity-70">0{i + 1}</p>
                <h3 className="display mt-3 text-3xl" style={{ fontStretch: "110%" }}>{it.role}</h3>
                <p className="mt-2 text-lg font-medium opacity-90">{it.line}</p>
                <ul className="mt-auto space-y-3 border-t border-dashed border-current/30 pt-6 text-sm">
                  {it.points.map((p) => (
                    <li key={p} className="flex gap-2">
                      <span aria-hidden>✓</span>
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}