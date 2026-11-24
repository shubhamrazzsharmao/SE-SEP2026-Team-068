import Link from "next/link";
import { LuCheck } from "react-icons/lu";
import type { OnboardingStep } from "@/types/app";

const tiles = ["bg-brand", "bg-paper/20", "bg-accent", "bg-paper/10", "bg-brand/60"];

export function GettingStarted({ steps }: { steps: OnboardingStep[] }) {
  const done = steps.filter((s) => s.done).length;
  if (done === steps.length) return null;

  return (
    <section className="relative overflow-hidden rounded-3xl bg-brown p-6 text-paper">
      <div aria-hidden className="absolute right-6 top-6 hidden gap-1.5 sm:flex">
        {tiles.map((t, i) => (
          <span key={i} className={`h-6 w-6 rounded ${t}`} />
        ))}
      </div>
      <p className="text-sm font-semibold text-brand">
        Getting started · {done} of {steps.length}
      </p>
      <h2 className="mt-1 text-xl font-semibold">Set up your first campaign</h2>
      <div className="mt-3 h-1.5 max-w-xs rounded-full bg-white/15">
        <div className="h-1.5 rounded-full bg-brand" style={{ width: `${(done / steps.length) * 100}%` }} />
      </div>

      <ol className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((s, i) => (
          <li key={s.label}>
            <Link
              href={s.href}
              className={`flex items-center gap-3 rounded-xl border p-3 text-sm font-medium transition-colors ${
                s.done ? "border-green-400/30 bg-green-400/10" : "border-white/15 hover:border-white/40"
              }`}
            >
              <span
                className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs font-bold ${
                  s.done ? "bg-green-500 text-white" : "bg-white/10"
                }`}
              >
                {s.done ? <LuCheck size={14} strokeWidth={3} /> : i + 1}
              </span>
              <span className={s.done ? "text-paper/60 line-through" : ""}>{s.label}</span>
            </Link>
          </li>
        ))}
      </ol>
    </section>
  );
}