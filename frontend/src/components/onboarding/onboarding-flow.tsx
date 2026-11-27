"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const INK = "#251A14";
const ORANGE = "#FF4F26";
const CREAM = "#F9F4EE";

type Role = "freelancer" | "agency" | "inhouse";

const roles: { id: Role; number: string; title: string; tagline: string; detail: string; bg: string; fg: string }[] = [
	{ id: "freelancer", number: "01", title: "Freelancer", tagline: "Many clients, one brain.", detail: "A separate workspace and brand profile for every client.", bg: ORANGE, fg: "#fff" },
	{ id: "agency", number: "02", title: "Agency", tagline: "Clarity for clients, not chaos.", detail: "Roles for creators and reviewers, with every version on record.", bg: INK, fg: "#fff" },
	{ id: "inhouse", number: "03", title: "In-house team", tagline: "One voice, every channel.", detail: "Keep your brand voice and approvals in a single place.", bg: "#fff", fg: INK },
];

const goals = [
	"Turn one source into a month of posts",
	"Trust every claim, checked against my source",
	"Get client approvals without the chaos",
	"Keep every post in my client's voice",
	"Collaborate smoothly with my team",
	"Plan and organize content clearly",
];

function Logo() {
	return (
		<Link href="/" className="flex items-center gap-2.5" aria-label="Mosaiq home">
			<svg width="26" height="26" viewBox="0 0 28 28" aria-hidden>
				<rect x="1" y="1" width="12" height="12" rx="3.5" fill={INK} />
				<rect x="15" y="1" width="12" height="12" rx="3.5" fill={INK} />
				<rect x="1" y="15" width="12" height="12" rx="3.5" fill={INK} />
				<rect x="15" y="15" width="12" height="12" rx="3.5" fill={ORANGE} />
			</svg>
			<span className="font-display text-xl font-extrabold uppercase tracking-tight" style={{ color: INK }}>Mosaiq</span>
		</Link>
	);
}

export function OnboardingFlow() {
	const router = useRouter();
	const [step, setStep] = useState<1 | 2>(1);
	const [role, setRole] = useState<Role | null>(null);
	const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
	const [saving, setSaving] = useState(false);

	const canContinue = step === 1 ? role !== null : selectedGoals.length > 0;

	function toggleGoal(goal: string) {
		setSelectedGoals((current) =>
			current.includes(goal) ? current.filter((item) => item !== goal) : [...current, goal],
		);
	}

	async function next() {
		if (!canContinue) return;
		if (step === 1) {
			setStep(2);
			return;
		}

		setSaving(true);
		// TODO: persist { role, goals } through the planned PUT /api/v1/me/onboarding endpoint.
		console.log("onboarding", { role, goals: selectedGoals });
		router.push("/dashboard");
	}

	return (
		<main className="relative min-h-screen overflow-hidden" style={{ background: CREAM }}>
			<style>{`@keyframes ob-in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}`}</style>

			<div aria-hidden className="pointer-events-none absolute -right-6 -top-6 hidden grid-cols-4 gap-2 opacity-70 md:grid">
				{["#FF7A57", "#E8DCCB", "#8F9BDB", "#EFE4D4", "#EFE4D4", "#251A14", "#E8DCCB", "#FF4F26", "#E8DCCB", "#EFE4D4", "#B7B3CF", "#EFE4D4"].map((color, index) => (
					<span key={index} className="h-12 w-12 rounded-lg" style={{ background: color }} />
				))}
			</div>

			<header className="relative mx-auto flex max-w-[1000px] items-center justify-between px-6 pt-8">
				<Logo />
				<div className="flex items-center gap-3">
					<span className="text-[12px] uppercase tracking-[0.18em] text-[#6B5B4E]">Step {step} of 2</span>
					<span className="flex gap-1.5" aria-hidden>
						{[1, 2].map((number) => (
							<span key={number} className="h-1.5 w-8 rounded-full" style={{ background: number <= step ? ORANGE : "#E2D5C3" }} />
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
					<p className="mt-3 text-center text-[15px] text-[#6B5B5E]">
						{step === 1 ? "We'll set up your workspace to match." : "Pick as many as you like."}
					</p>

					{step === 1 ? (
						<div className="mt-10 grid gap-5 md:grid-cols-3">
							{roles.map((item) => {
								const selected = role === item.id;
								return (
									<button
										key={item.id}
										type="button"
										onClick={() => setRole(item.id)}
										aria-pressed={selected}
										className={`relative flex h-[300px] flex-col rounded-[24px] p-7 text-left shadow-[0_12px_30px_-14px_rgba(37,26,20,0.35)] transition duration-300 ${selected ? "-translate-y-2 ring-4 ring-[#251A14] ring-offset-4 ring-offset-[#F9F4EE]" : "hover:-translate-y-1"}`}
										style={{ background: item.bg, color: item.fg }}
									>
										{selected && (
											<span className="absolute right-4 top-4 flex h-7 w-7 items-center justify-center rounded-full bg-white text-[#FF4F26] shadow-md">✓</span>
										)}
										<span className="text-[11px] tracking-[0.2em] opacity-75">{item.number}</span>
										<span className="mt-2 font-display text-[26px] font-extrabold uppercase leading-none tracking-tight">{item.title}</span>
										<span className="mt-2 text-[15px] opacity-80">{item.tagline}</span>
										<span className="mt-auto border-t border-dashed border-current pt-4 text-[13px] leading-snug opacity-80">{item.detail}</span>
									</button>
								);
							})}
						</div>
					) : (
						<div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
							{goals.map((goal) => {
								const selected = selectedGoals.includes(goal);
								return (
									<button
										key={goal}
										type="button"
										onClick={() => toggleGoal(goal)}
										aria-pressed={selected}
										className={`relative flex h-[150px] flex-col items-center justify-center rounded-[20px] border-2 px-5 text-center text-[15px] font-medium leading-snug transition duration-200 ${selected ? "-translate-y-1 border-[#FF4F26] bg-white text-[#251A14] shadow-[0_14px_30px_-14px_rgba(255,79,38,0.55)]" : "border-transparent bg-white/60 text-[#251A14] hover:-translate-y-0.5 hover:bg-white"}`}
									>
										{goal}
										{selected && <span className="absolute right-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-[#FF4F26] text-xs text-white">✓</span>}
									</button>
								);
							})}
						</div>
					)}
				</div>

				<div className="mx-auto mt-10 flex max-w-[560px] items-center gap-3">
					{step === 2 && (
						<button type="button" onClick={() => setStep(1)} className="h-12 rounded-full border border-[#D9CBB8] px-6 text-[14px] font-semibold text-[#251A14] transition hover:border-[#251A14]">
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
				{step === 2 && selectedGoals.length > 0 && (
					<p className="mt-3 text-center text-[13px] text-[#6B5B4E]">{selectedGoals.length} selected</p>
				)}
			</section>
		</main>
	);
}
