import { site } from "@/lib/site";

const f = site.features;

function Card({
  className = "",
  title,
  text,
  dark = false,
  children,
}: {
  className?: string;
  title: string;
  text: string;
  dark?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`flex flex-col justify-between gap-8 rounded-3xl border p-7 transition-transform duration-200 hover:-translate-y-1 ${
        dark ? "border-transparent text-paper" : "border-line bg-white"
      } ${className}`}
    >
      <div>{children}</div>
      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className={`mt-2 text-sm ${dark ? "text-paper/70" : "text-muted"}`}>{text}</p>
      </div>
    </div>
  );
}

function ScoreRing({ value }: { value: number }) {
  const r = 38;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative h-28 w-28">
      <svg viewBox="0 0 100 100" className="-rotate-90">
        <circle cx="50" cy="50" r={r} fill="none" stroke="currentColor" strokeOpacity="0.15" strokeWidth="10" />
        <circle
          cx="50" cy="50" r={r} fill="none" strokeWidth="10" strokeLinecap="round"
          className="stroke-brand" strokeDasharray={c} strokeDashoffset={c * (1 - value / 100)}
        />
      </svg>
      <span className="display absolute inset-0 grid place-items-center text-3xl">{value}</span>
    </div>
  );
}

export function Features() {
  return (
    <section id="features" className="bg-paper-hero/40 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-brand">{f.eyebrow}</p>
        <h2 className="display mt-3 max-w-3xl text-[clamp(2rem,4vw,3.4rem)]">{f.title}</h2>

        <div className="mt-12 grid gap-4 md:grid-cols-6">
          <Card className="md:col-span-4" {...f.items.source}>
            <p className="rounded-2xl bg-paper p-5 text-lg leading-relaxed">
              Delivery time dropped from 5 days to{" "}
              <mark className="rounded bg-green-100 px-1">2 days</mark> after launch.{" "}
              <mark className="rounded bg-amber-100 px-1">Customers love it 10x more.</mark>
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold">
              <span className="rounded-full bg-green-100 px-3 py-1 text-green-700">✓ Supported · source p.3</span>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-700">⚠ Not found in source</span>
            </div>
          </Card>

          <Card className="bg-brown md:col-span-2" dark {...f.items.voice}>
            <ScoreRing value={92} />
          </Card>

          <Card className="bg-brand md:col-span-2" dark {...f.items.client}>
            <div className="rounded-xl bg-white/15 p-3 text-sm">
              <p className="text-xs opacity-80">mosaiq.app/review/x7k2…</p>
              <p className="mt-2 font-semibold">Dana, 3 posts need your review</p>
              <div className="mt-3 flex gap-2 text-xs font-semibold">
                <span className="rounded-lg bg-white px-3 py-1.5 text-ink">Approve</span>
                <span className="rounded-lg bg-white/20 px-3 py-1.5">Request changes</span>
              </div>
            </div>
          </Card>

          <Card className="md:col-span-2" {...f.items.versions}>
            <ol className="space-y-2 text-sm">
              {["v3 · Dana approved ✓", "v2 · Edited by Maria", "v1 · AI draft"].map((t, i) => (
                <li key={t} className={`rounded-lg px-3 py-2 ${i === 0 ? "bg-green-100 font-semibold text-green-700" : "bg-paper"}`}>
                  {t}
                </li>
              ))}
            </ol>
          </Card>

          <Card className="md:col-span-2" {...f.items.ideas}>
            <div className="space-y-2 text-sm">
              <p className="rounded-lg bg-paper px-3 py-2">💡 Founder story for Diwali</p>
              <p className="flex items-center justify-between rounded-lg bg-paper px-3 py-2">
                🔗 Competitor report
                <span className="rounded-full bg-brand px-2 py-0.5 text-xs font-semibold text-white">Turn into campaign</span>
              </p>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}