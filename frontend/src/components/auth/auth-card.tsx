"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthMosaic } from "./auth-mosaic";

type Mode = "login" | "signup";

const INK = "#251A14";
const ORANGE = "#FF4F26";
const CREAM = "#F9F4EE";

function MosaiqMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" aria-hidden>
      <rect x="1" y="1" width="12" height="12" rx="3.5" fill={INK} />
      <rect x="15" y="1" width="12" height="12" rx="3.5" fill={INK} />
      <rect x="1" y="15" width="12" height="12" rx="3.5" fill={INK} />
      <rect x="15" y="15" width="12" height="12" rx="3.5" fill={ORANGE} />
    </svg>
  );
}

function SocialButton({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      className="flex h-11 w-11 items-center justify-center rounded-full border border-[#E6DCCD] bg-white text-[#251A14] transition hover:-translate-y-0.5 hover:border-[#251A14]"
    >
      {children}
    </button>
  );
}

function Field(props: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  const { label, id, ...rest } = props;
  return (
    <label htmlFor={id} className="block">
      <span className="sr-only">{label}</span>
      <input
        id={id}
        {...rest}
        placeholder={label}
        className="h-12 w-full rounded-full border border-[#E6DCCD] bg-white/80 px-5 text-[14px] text-[#251A14] outline-none transition placeholder:text-[#8A7B6D] focus:border-[#FF4F26] focus:ring-4 focus:ring-[#FF4F26]/15"
      />
    </label>
  );
}

function SubmitButton({ children, loading }: { children: React.ReactNode; loading: boolean }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="mt-2 flex h-12 w-full items-center justify-center rounded-full bg-[#FF4F26] text-[14px] font-semibold text-white transition hover:bg-[#e8431d] disabled:opacity-60"
    >
      {loading ? "Please wait…" : children}
    </button>
  );
}

function LoginForm() {
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const data = new FormData(e.currentTarget);
    // TODO: call your auth API here.
    console.log("login", Object.fromEntries(data));
    setTimeout(() => setLoading(false), 600);
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-[340px] space-y-3">
      <h1 className="mb-1 text-center font-display text-[34px] font-extrabold uppercase leading-none tracking-tight text-[#251A14]">
        Welcome back.
      </h1>
      <p className="pb-3 text-center text-[14px] text-[#6B5B4E]">
        Your campaigns and approvals are right where you left them.
      </p>
      <div className="flex justify-center gap-3 pb-2">
        <SocialButton label="Continue with Google">
          <span className="text-[15px] font-bold">G</span>
        </SocialButton>
        <SocialButton label="Continue with LinkedIn">
          <span className="text-[14px] font-extrabold">in</span>
        </SocialButton>
      </div>
      <p className="text-center text-[12px] uppercase tracking-[0.14em] text-[#8A7B6D]">or use your email</p>
      <Field id="login-email" name="email" type="email" label="Email address" autoComplete="email" required />
      <Field id="login-password" name="password" type="password" label="Password" autoComplete="current-password" required />
      <div className="text-right">
        <Link href="/forgot-password" className="text-[13px] text-[#6B5B4E] underline-offset-4 hover:text-[#251A14] hover:underline">
          Forgot your password?
        </Link>
      </div>
      <SubmitButton loading={loading}>Log in</SubmitButton>
    </form>
  );
}

function SignupForm() {
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    const data = new FormData(e.currentTarget);
    // TODO: call your auth API here.
    console.log("signup", Object.fromEntries(data));
    setTimeout(() => setLoading(false), 600);
  }

  return (
    <form onSubmit={onSubmit} className="w-full max-w-[340px] space-y-3">
      <h1 className="mb-1 text-center font-display text-[34px] font-extrabold uppercase leading-none tracking-tight text-[#251A14]">
        Start creating.
      </h1>
      <p className="pb-3 text-center text-[14px] text-[#6B5B4E]">
        One source in. A whole campaign out.
      </p>
      <div className="flex justify-center gap-3 pb-2">
        <SocialButton label="Sign up with Google">
          <span className="text-[15px] font-bold">G</span>
        </SocialButton>
        <SocialButton label="Sign up with LinkedIn">
          <span className="text-[14px] font-extrabold">in</span>
        </SocialButton>
      </div>
      <p className="text-center text-[12px] uppercase tracking-[0.14em] text-[#8A7B6D]">or use your email</p>
      <Field id="signup-name" name="name" type="text" label="Full name" autoComplete="name" required />
      <Field id="signup-email" name="email" type="email" label="Work email" autoComplete="email" required />
      <Field id="signup-password" name="password" type="password" label="Password (8+ characters)" autoComplete="new-password" minLength={8} required />
      <SubmitButton loading={loading}>Create account</SubmitButton>
      <p className="pt-1 text-center text-[12px] text-[#8A7B6D]">
        By signing up you agree to our{" "}
        <Link href="/terms" className="underline underline-offset-2">Terms</Link> and{" "}
        <Link href="/privacy" className="underline underline-offset-2">Privacy Policy</Link>.
      </p>
    </form>
  );
}

export function AuthCard({ initialMode }: { initialMode: Mode }) {
  const [mode, setMode] = useState<Mode>(initialMode);
  const isSignup = mode === "signup";

  function switchTo(next: Mode) {
    setMode(next);
    window.history.replaceState(null, "", next === "login" ? "/login" : "/signup");
  }

  return (
    <main
      className="relative flex min-h-screen flex-col items-center justify-center px-4 py-10"
      style={{ background: `linear-gradient(135deg, #F3E9DC 0%, #E8D9C2 100%)` }}
    >
      <Link href="/" className="mb-6 flex items-center gap-2.5" aria-label="Mosaiq home">
        <MosaiqMark />
        <span className="font-display text-[22px] font-extrabold uppercase tracking-tight" style={{ color: INK }}>
          Mosaiq
        </span>
      </Link>

      {/* Desktop: sliding two-panel card */}
      <div
        className="relative hidden h-[640px] w-full max-w-[960px] overflow-hidden rounded-[32px] shadow-[0_30px_80px_-20px_rgba(37,26,20,0.35)] md:block"
        style={{ background: CREAM }}
      >
        {/* Login form (left) */}
        <div
          className={`absolute inset-y-0 left-0 flex w-1/2 items-center justify-center p-8 transition-all duration-700 ease-[cubic-bezier(.7,0,.2,1)] ${
            isSignup ? "pointer-events-none translate-x-full opacity-0" : "translate-x-0 opacity-100"
          }`}
        >
          <LoginForm />
        </div>

        {/* Signup form (right) */}
        <div
          className={`absolute inset-y-0 right-0 flex w-1/2 items-center justify-center p-8 transition-all duration-700 ease-[cubic-bezier(.7,0,.2,1)] ${
            isSignup ? "translate-x-0 opacity-100" : "pointer-events-none -translate-x-full opacity-0"
          }`}
        >
          <SignupForm />
        </div>

        {/* Sliding mosaic overlay */}
        <div
          className={`absolute inset-y-0 left-0 z-10 w-1/2 overflow-hidden transition-transform duration-700 ease-[cubic-bezier(.7,0,.2,1)] ${
            isSignup ? "translate-x-0" : "translate-x-full"
          }`}
          style={{ background: INK }}
        >
          <AuthMosaic />
          <div className="absolute inset-x-0 bottom-0 z-10 bg-gradient-to-t from-[#251A14] via-[#251A14]/90 to-transparent p-8 pt-24 text-center">
            <h2 className="font-display text-[30px] font-extrabold uppercase leading-[1.02] tracking-tight text-white">
              {isSignup ? "Already in the mosaiq?" : "New to Mosaiq?"}
            </h2>
            <p className="mx-auto mt-2 max-w-[280px] text-[14px] text-[#D9CBB8]">
              {isSignup
                ? "Log in to pick up your campaigns and approvals."
                : "Drop in one source and get a whole campaign, approved."}
            </p>
            <button
              type="button"
              onClick={() => switchTo(isSignup ? "login" : "signup")}
              className="mt-5 h-11 rounded-full border border-white/70 px-8 text-[14px] font-semibold text-white transition hover:bg-white hover:text-[#251A14]"
            >
              {isSignup ? "Log in" : "Sign up"}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile: single form with toggle */}
      <div className="w-full max-w-[420px] rounded-[28px] p-7 shadow-[0_20px_60px_-20px_rgba(37,26,20,0.3)] md:hidden" style={{ background: CREAM }}>
        <div className="mb-6 flex rounded-full bg-[#EFE4D4] p-1">
          {(["login", "signup"] as const).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => switchTo(m)}
              className={`h-10 flex-1 rounded-full text-[14px] font-semibold transition ${
                mode === m ? "bg-[#251A14] text-white" : "text-[#6B5B4E]"
              }`}
            >
              {m === "login" ? "Log in" : "Sign up"}
            </button>
          ))}
        </div>
        <div className="flex justify-center">{isSignup ? <SignupForm /> : <LoginForm />}</div>
      </div>
    </main>
  );
}
