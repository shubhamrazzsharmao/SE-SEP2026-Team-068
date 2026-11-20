import { site } from "@/lib/site";

const f = site.faq;

export function Faq() {
  return (
    <section id="faq" className="bg-paper-hero/40 py-24">
      <div className="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-[1fr_1.6fr]">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-brand">{f.eyebrow}</p>
          <h2 className="display mt-3 text-[clamp(2rem,4vw,3.4rem)]">{f.title}</h2>
        </div>

        <div className="space-y-3">
          {f.items.map((it, i) => (
            <details
              key={it.q}
              open={i === 0}
              className="group rounded-2xl border border-line bg-white p-5 open:border-brand open:shadow-md"
            >
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold [&::-webkit-details-marker]:hidden">
                {it.q}
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-paper text-lg transition-transform group-open:rotate-45 group-open:bg-brand group-open:text-white">
                  +
                </span>
              </summary>
              <p className="mt-3 pr-10 text-muted">{it.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}