"use client";

import { useState } from "react";
import { LuLightbulb } from "react-icons/lu";

export function IdeaCapture() {
  const [value, setValue] = useState("");
  const [saved, setSaved] = useState<string[]>([]);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text) return;
    // TODO: POST to the ideas endpoint once the backend exposes it
    setSaved((s) => [text, ...s].slice(0, 3));
    setValue("");
  }

  return (
    <section className="rounded-3xl bg-paper-hero/60 p-6">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <LuLightbulb size={18} className="text-brand" /> Quick idea
      </h2>
      <p className="mt-1 text-sm text-muted">Jot it down now. Turn it into a campaign later.</p>

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