"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const INK = "#251A14";
const ORANGE = "#FF4F26";
const CREAM = "#F9F4EE";

/* ------------------------------ data ------------------------------ */

type Role = "freelancer" | "agency" | "inhouse";

const ROLES: {
  id: Role;
  n: string;
  title: string;
  tagline: string;
  detail: string;
  bg: string;
  fg: string;
  muted: string;
}[] = [
  {
    id: "freelancer",
    n: "01",
    title: "Freelancer",
    tagline: "Many clients, one brain.",
    detail: "A separate workspace and brand profile for every client.",
    bg: ORANGE,
    fg: "#fff",
    muted: "rgba(255,255,255,0.85)",
  },
  {
    id: "agency",
    n: "02",
    title: "Agency",
    tagline: "Clarity for clients, not chaos.",
    detail: "Roles for creators and reviewers, with every version on record.",
    bg: INK,
    fg: "#fff",
    muted: "rgba(255,255,255,0.75)",
  },
  {
    id: "inhouse",
    n: "03",
    title: "In-house team",
    tagline: "One voice, every channel.",
    detail: "Keep your brand voice and approvals in a single place.",
    bg: "#fff",
    fg: INK,
    muted: "#6B5B4E",
  },
];

type IconName = "spark" | "shield" | "check" | "wave" | "people" | "calendar";

const EXPECTATIONS: { id: string; label: string; icon: IconName }[] = [
  { id: "month", label: "Turn one source into a month of posts", icon: "spark" },
  { id: "claims", label: "Trust every claim, checked against my source", icon: "shield" },
  { id: "approvals", label: "Get client approvals without the chaos", icon: "check" },
  { id: "voice", label: "Keep every post in my client's voice", icon: "wave" },
  { id: "team", label: "Collaborate smoothly with my team", icon: "people" },
  { id: "plan", label: "Plan and organize content clearly", icon: "calendar" },
];

/* ------------------------------ bits ------------------------------ */

function Icon({ name }: { name: IconName }) {
  const p = {
    width: 34,
    height: 34,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (name) {
    case "spark":
      return (
        <svg {...p}>
          <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />
          <path d="M19 16v4M17 18h4" />
        </svg>
      );
    case "shield":
      return (
        <svg {...p}>
          <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      );
    case "check":
      return (
        <svg {...p}>
          <circle cx="12" cy="12" r="9" />
          <path d="m8 12 3 3 5-6" />
        </svg>
      );
    case "wave":
      return (
        <svg {...p}>
          <path d="M4 10v4M8 6v12M12 9v6M16 4v16M20 10v4" />
        </svg>
      );
    case "people":
      return (
        <svg {...p}>
          <circle cx="9" cy="8" r="3" />
          <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
          <circle cx="17" cy="9" r="2.5" />
          <path d="M17 14.5c2.5 0 4.5 2 4.5 4.5" />
        </svg>
      );
    case "calendar":
      return (
        <svg {...p}>
          <rect x="3" y="4" width="18" height="17" rx="3" />
          <path d="M8 2v4M16 2v4M3 10h18M8 15h3" />
        </svg>
      );
  }
}

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2.5" aria-label="Mosaiq home">
      <svg width="26" height="26" viewBox="0 0 28 28" aria-hidden>
        <rect x="1" y="1" width="12" height="12" rx="3.5" fill={INK} />
        <rect x="15" y="1" width="12" height="12" rx="3.5" fill={INK} />
        <rect x="1" y="15" width="12" height="12" rx="3.5" fill={INK} />
        <rect x="15" y="15" width="12" height="12" rx="3.5" fill={ORANGE} />
      </svg>
      <span className="font-display text-[20px] font-extrabold uppercase tracking-tight" style={{ color: INK }}>
        Mosaiq
      </span>
    </Link>
  );
}

function Tick() {
  return (
    <span className="absolute right-4 top-4 flex h-7 w-7 items-center justify-center rounded-full bg-white text-[#FF4F26] shadow-md">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m5 12 5 5 9-10" />
      </svg>
    </span>
  );
}

/* ----------------------------- steps ------------------------------ */

function RoleStep({ value, onChange }: { value: Role | null; onChange: (r: Role) => void }) {
  return (
    <div className="grid gap-5 md:grid-cols-3">
      {ROLES.map((r) => {
        const selected = value === r.id;
        return (
          <button
            key={r.id}
            type="button"
            onClick={() => onChange(r.id)}
            aria-pressed={selected}
            className={`relative flex h-[300px] flex-col rounded-[24px] p-7 text-left shadow-[0_12px_30px_-14px_rgba(37,26,20,0.35)] transition duration-300 ${
              selected ? "-translate-y-2 ring-4 ring-offset-4 ring-offset-[#F9F4EE]" : "hover:-translate-y-1"
            }`}
            style={{ background: r.bg, color: r.fg, ["--tw-ring-color" as string]: selected ? INK : undefined }}
          >
            {selected && <Tick />}
            <span className="text-[11px] tracking-[0.2em]" style={{ color: r.muted }}>
              {r.n}
            </span>
            <span className="mt-2 font-display text-[26px] font-extrabold uppercase leading-none tracking-tight">{r.title}</span>
            <span className="mt-2 text-[15px]" style={{ color: r.muted }}>
              {r.tagline}
            </span>

            {/* ticket divider with notches */}
            <span className="relative mt-auto block border-t border-dashed" style={{ borderColor: r.muted, opacity: 0.6 }}>
              <span className="absolute -left-[38px] -top-[11px] h-[22px] w-[22px] rounded-full" style={{ background: CREAM }} />
              <span className="absolute -right-[38px] -top-[11px] h-[22px] w-[22px] rounded-full" style={{ background: CREAM }} />
            </span>
            <span className="pt-4 text-[13px] leading-snug" style={{ color: r.muted }}>
              {r.detail}
            </span>
          </button>
        );
      })}
    </div>
  );
}

function ExpectationsStep({ value, onToggle }: { value: string[]; onToggle: (id: string) => void }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {EXPECTATIONS.map((e) => {
        const selected = value.includes(e.id);
        return (
          <button
            key={e.id}
            type="button"
            onClick={() => onToggle(e.id)}
            aria-pressed={selected}
            className={`relative flex h-[150px] flex-col items-center justify-center gap-3 rounded-[20px] border-2 px-5 text-center text-[15px] font-medium leading-snug transition duration-200 ${
              selected
                ? "-translate-y-1 border-[#FF4F26] bg-white text-[#251A14] shadow-[0_14px_30px_-14px_rgba(255,79,38,0.55)]"
                : "border-transparent bg-white/60 text-[#251A14] hover:-translate-y-0.5 hover:bg-white"
            }`}
          >
            <span className={selected ? "text-[#FF4F26]" : "text-[#251A14]"}>
              <Icon name={e.icon} />
            </span>
            {e.label}
            {selected && (
              <span className="absolute right-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-[#FF4F26] text-white">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m5 12 5 5 9-10" />
                </svg>
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

/* ----------------------------- flow ------------------------------- */

export function OnboardingFlow() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [role, setRole] = useState<Role | null>(null);
  const [goals, setGoals] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  const canContinue = step === 1 ? role !== null : goals.length > 0;

  function toggleGoal(id: string) {
    setGoals((g) => (g.includes(id) ? g.filter((x) => x !== id) : [...g, id]));
  }

  async function next() {
    if (!canContinue) return;
    if (step === 1) {
      setStep(2);
      return;
    }
    setSaving(true);
    // TODO: save { role, goals } to your API, then continue.
    console.log("onboarding", { role, goals });
    router.push("/dashboard");
  }

  return (
    <main className="relative min-h-screen overflow-hidden" style={{ background: CREAM }}>
      <style>{`@keyframes ob-in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}`}</style>

      {/* decorative mosaic corner */}
      <div aria-hidden className="pointer-events-none absolute -right-6 -top-6 hidden grid-cols-4 gap-2 opacity-70 md:grid">
        {["#FF7A57", "#E8DCCB", "#8F9BDB", "#EFE4D4", "#EFE4D4", "#251A14", "#E8DCCB", "#FF4F26", "#E8DCCB", "#EFE4D4", "#B7B3CF", "#EFE4D4"].map((c, i) => (
          <span key={i} className="h-12 w-12 rounded-lg" style={{ background: c }} />
        ))}
      </div>

      <header className="relative mx-auto flex max-w-[1000px] items-center justify-between px-6 pt-8">
        <Logo />
        <div className="flex items-center gap-3">
          <span className="text-[12px] uppercase tracking-[0.18em] text-[#6B5B4E]">Step {step} of 2</span>
          <span className="flex gap-1.5" aria-hidden>
            {[1, 2].map((n) => (
              <span key={n} className="h-1.5 w-8 rounded-full transition-colors duration-500" style={{ background: n <= step ? ORANGE : "#E2D5C3" }} />
            ))}
          </span>
        </div>
      </header>

      <section className="relative mx-auto max-w-[1000px] px-6 pb-16 pt-14">
        <div key={step} style={{ animation: "ob-in 0.5s cubic-bezier(.2,.7,.2,1) both" }}>
          <p className="text-center text-[12px] font-semibold uppercase tracking-[0.2em]" style={{ color: ORANGE }}>
            {step === 1 ? "Welcome to Mosaiq" : "Almost there"}
          </p>
          <h1 className="mx-auto mt-3 max-w-[760px] text-center font-display text-[clamp(30px,5vw,52px)] font-extrabold uppercase leading-[1.02] tracking-tight" style={{ color: INK }}>
            {step === 1 ? "Who are you here as?" : "What do you want from Mosaiq?"}
          </h1>
          <p className="mt-3 text-center text-[15px] text-[#6B5B4E]">
            {step === 1 ? "We'll set up your workspace to match." : "Pick as many as you like."}
          </p>

          <div className="mt-10">
            {step === 1 ? <RoleStep value={role} onChange={setRole} /> : <ExpectationsStep value={goals} onToggle={toggleGoal} />}
          </div>
        </div>

        <div className="mx-auto mt-10 flex max-w-[560px] items-center gap-3">
          {step === 2 && (
            <button
              type="button"
              onClick={() => setStep(1)}
              className="h-12 rounded-full border border-[#D9CBB8] px-6 text-[14px] font-semibold text-[#251A14] transition hover:border-[#251A14]"
            >
              Back
            </button>
          )}
          <button
            type="button"
            disabled={!canContinue || saving}
            onClick={next}
            className="h-12 flex-1 rounded-full text-[14px] font-semibold transition disabled:cursor-not-allowed disabled:bg-[#E8DECF] disabled:text-[#A6988A] enabled:bg-[#FF4F26] enabled:text-white enabled:hover:bg-[#e8431d]"
          >
            {saving ? "Setting up…" : step === 1 ? "Continue" : "Finish setup"}
          </button>
        </div>
        {step === 2 && goals.length > 0 && (
          <p className="mt-3 text-center text-[13px] text-[#6B5B4E]">{goals.length} selected</p>
        )}
      </section>
    </main>
  );
}
