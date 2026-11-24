"use client";

import { useState, useSyncExternalStore } from "react";
import { LuLightbulb } from "react-icons/lu";

// The backend has no ideas endpoint yet (Sprint 2), so ideas are kept in this browser.
const KEY = "ideas";
const subscribe = (cb: () => void) => {
  window.addEventListener("storage", cb);
  return () => window.removeEventListener("storage", cb);
};
const read = () => {
  try {
    return localStorage.getItem(KEY) ?? "[]";
  } catch {
    return "[]";
  }
};

export function IdeaCapture() {
  const [value, setValue] = useState("");
  const raw = useSyncExternalStore(subscribe, read, () => "[]");
  const saved: string[] = JSON.parse(raw);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text) return;
    try {
      localStorage.setItem(KEY, JSON.stringify([text, ...saved].slice(0, 5)));
      window.dispatchEvent(new StorageEvent("storage", { key: KEY }));
    } catch {}
    setValue("");
  }

  return (
    <section className="rounded-3xl bg-paper-hero/60 p-6">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <LuLightbulb size={18} className="text-brand" /> Quick idea
      </h2>
      <p className="mt-1 text-sm text-muted">Jot it down now. Saved in this browser for now.</p>

      <form onSubmit={onSubmit} className="mt-4 flex gap-2">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="A story, link or angle…"
          className="min-w-0 flex-1 rounded-xl border border-line bg-white px-4 py-2.5 text-sm outline-none focus:border-brand"
        />
        <button className="rounded-xl bg-ink px-4 text-sm font-semibold text-white transition-colors hover:bg-brand">Save</button>
      </form>

      {saved.length > 0 && (
        <ul className="mt-3 space-y-2 text-sm">
          {saved.map((s, i) => (
            <li key={`${s}-${i}`} className="rounded-lg bg-white px-3 py-2">
              💡 {s}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}