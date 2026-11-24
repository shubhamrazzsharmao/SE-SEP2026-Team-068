"use client";

import { createContext, startTransition, useActionState, useContext, useEffect, useRef } from "react";
import type { ActionState } from "@/lib/actions";

type Action = (state: ActionState, fd: FormData) => Promise<ActionState>;
const Pending = createContext(false);

/**
 * Form wired to a Server Action. Shows the backend's error or success message under the fields.
 * Inputs keep their values when the action fails, and are cleared on success if `reset` is set.
 */
export function ActionForm({
  action, children, className, reset = false, confirm,
}: {
  action: Action;
  children: React.ReactNode;
  className?: string;
  reset?: boolean;
  confirm?: string;
}) {
  const [state, run, pending] = useActionState(action, {});
  const ref = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state.ok && reset) ref.current?.reset();
  }, [state, reset]);

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (confirm && !window.confirm(confirm)) return;
    const fd = new FormData(e.currentTarget);
    startTransition(() => run(fd));
  }

  return (
    <form ref={ref} onSubmit={onSubmit} className={className}>
      <Pending value={pending}>{children}</Pending>
      {state.error && (
        <p role="alert" className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</p>
      )}
      {state.ok && state.message && (
        <p role="status" className="mt-3 rounded-xl bg-green-50 px-3 py-2 text-sm text-green-800">{state.message}</p>
      )}
    </form>
  );
}

const variants = {
  primary: "bg-brand text-white hover:bg-brand-hover",
  dark: "bg-ink text-white hover:bg-brand",
  outline: "border border-line bg-white hover:border-ink/30",
  danger: "border border-red-200 bg-white text-red-700 hover:bg-red-50",
  success: "bg-green-600 text-white hover:bg-green-700",
};

export function SubmitButton({
  children, variant = "primary", className = "", pendingText = "Working…",
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
  className?: string;
  pendingText?: string;
}) {
  const pending = useContext(Pending);
  return (
    <button
      type="submit"
      disabled={pending}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-60 ${variants[variant]} ${className}`}
    >
      {pending ? pendingText : children}
    </button>
  );
}
