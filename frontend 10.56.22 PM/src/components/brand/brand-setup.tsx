"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const ORANGE = "#FF4F26";
const TONES = ["Warm", "Bold", "Playful", "Professional", "Witty", "Direct", "Calm", "Premium"];
const STEPS = ["Reading the website", "Learning tone and vocabulary", "Writing the voice guide"];

const inputCls =
  "h-12 w-full rounded-2xl border border-[#E6DCCD] bg-white px-4 text-[14px] text-[#251A14] outline-none transition placeholder:text-[#8A7B6D] focus:border-[#FF4F26] focus:ring-4 focus:ring-[#FF4F26]/15";
const areaCls =
  "w-full rounded-2xl border border-[#E6DCCD] bg-white px-4 py-3 text-[14px] text-[#251A14] outline-none transition placeholder:text-[#8A7B6D] focus:border-[#FF4F26] focus:ring-4 focus:ring-[#FF4F26]/15";

function isUrl(v: string) {
  try {
    const u = new URL(/^https?:\/\//i.test(v.trim()) ? v.trim() : `https://${v.trim()}`);
    return u.hostname.includes(".");
  } catch {
    return false;
  }
}

function Label({ children, optional }: { children: React.ReactNode; optional?: boolean }) {
  return (
    <span className="mb-1.5 flex items-center gap-2 text-[13px] font-medium text-[#251A14]">
      {children}
      {optional && <span className="text-[12px] font-normal text-[#8A7B6D]">optional</span>}
    </span>
  );
}

function LogoUpload({ file, onChange, disabled }: { file: File | null; onChange: (f: File | null) => void; disabled?: boolean }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function pick(f?: File) {
    if (!f) return;
    if (!/^image\/(png|jpe?g|svg\+xml|webp)$/.test(f.type)) return setError("Use a PNG, JPG, SVG or WebP file.");
    if (f.size > 2 * 1024 * 1024) return setError("Logo must be under 2 MB.");
    setError("");
    onChange(f);
  }

  return (
    <div>
      <Label optional>Brand logo</Label>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          if (!disabled) pick(e.dataTransfer.files?.[0]);
        }}
        className={`flex items-center gap-4 rounded-2xl border-2 border-dashed bg-white p-4 transition ${
          drag ? "border-[#FF4F26] bg-[#FFF3EE]" : "border-[#E6DCCD]"
        }`}
      >
        <div className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-[#F3E9DC] text-[#8A7B6D]">
          {preview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={preview} alt="Brand logo preview" className="h-full w-full object-contain" />
          ) : (
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="4" />
              <circle cx="9" cy="9" r="1.6" />
              <path d="m21 15-5-5L5 21" />
            </svg>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-[14px] font-medium text-[#251A14]">{file ? file.name : "Drop a logo here"}</p>
          <p className="text-[12px] text-[#8A7B6D]">PNG, JPG, SVG or WebP, up to 2 MB</p>
        </div>

        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
            className="h-9 rounded-full bg-[#251A14] px-4 text-[13px] font-semibold text-white transition hover:bg-black disabled:opacity-50"
          >
            {file ? "Replace" : "Upload"}
          </button>
          {file && (
            <button
              type="button"
              disabled={disabled}
              onClick={() => onChange(null)}
              className="h-9 rounded-full border border-[#E6DCCD] px-4 text-[13px] font-medium text-[#251A14] transition hover:border-[#251A14]"
            >
              Remove
            </button>
          )}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/svg+xml,image/webp"
          className="sr-only"
          onChange={(e) => {
            pick(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </div>
      {error && <p className="mt-1.5 text-[12px] text-[#D83A12]">{error}</p>}
    </div>
  );
}

export function BrandSetup() {
  const router = useRouter();
  const [logo, setLogo] = useState<File | null>(null);
  const [mode, setMode] = useState<"auto" | "manual">("auto");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [link, setLink] = useState<"idle" | "loading" | "ok">("idle");
  const [samples, setSamples] = useState("");
  const [tones, setTones] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [avoid, setAvoid] = useState("");
  const [step, setStep] = useState(-1); // -1 = not generating

  const canGenerate = name.trim().length > 0 && (isUrl(url) || samples.trim().length > 0);
  const canSave = name.trim().length > 0 && tones.length > 0;
  const generating = step >= 0;

  function fetchLink() {
    if (!isUrl(url)) return;
    setLink("loading");
    // TODO: ask your API to read the page and return a preview.
    setTimeout(() => setLink("ok"), 700);
  }

  function toggleTone(t: string) {
    setTones((x) => (x.includes(t) ? x.filter((y) => y !== t) : [...x, t]));
  }

  // Demo progress. Replace with a real API call that decodes the brand voice.
  useEffect(() => {
    if (step < 0) return;
    if (step >= STEPS.length) {
      console.log("generate", { name, url, samples });
      const t = setTimeout(() => router.push("/dashboard"), 600);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setStep((s) => s + 1), 1100);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step]);

  function saveManual() {
    if (!canSave) return;
    // TODO: save the manual profile to your API.
    console.log("manual", { name, tones, notes, avoid });
    router.push("/dashboard");
  }

  return (
    <section className="relative mx-auto w-full max-w-[560px] px-6 pb-24 pt-16">
      <p className="text-center text-[12px] font-semibold uppercase tracking-[0.2em]" style={{ color: ORANGE }}>
        New brand profile
      </p>
      <h1 className="mt-3 text-center font-display text-[clamp(28px,4.5vw,44px)] font-extrabold uppercase leading-[1.02] tracking-tight text-[#251A14]">
        {mode === "auto" ? "Decode your brand voice." : "Describe your brand voice."}
      </h1>
      <p className="mx-auto mt-4 max-w-[500px] text-center text-[15px] leading-relaxed text-[#6B5B4E]">
        {mode === "auto"
          ? "Share your client's website or a few sample posts. We'll learn their tone and vocabulary, then score every post we write against it. A website or samples are needed."
          : "Pick the tone words that fit, then add any guidelines. Every post will be scored against this."}
      </p>

      <div className="mt-10 space-y-5">
        <label className="block">
          <Label>Client or brand name</Label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Sunrise Coffee Co." className={inputCls} disabled={generating} />
        </label>

        <LogoUpload file={logo} onChange={setLogo} disabled={generating} />

        {mode === "auto" ? (
          <>
            <div>
              <Label>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                  <circle cx="12" cy="12" r="9" />
                  <path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18" />
                </svg>
                Website link
              </Label>
              <div className="flex gap-2">
                <input
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    setLink("idle");
                  }}
                  placeholder="Link to your client's website..."
                  className={inputCls}
                  disabled={generating}
                />
                <button
                  type="button"
                  onClick={fetchLink}
                  disabled={!isUrl(url) || link === "loading" || generating}
                  className="h-12 shrink-0 rounded-2xl px-5 text-[14px] font-semibold transition disabled:cursor-not-allowed disabled:bg-[#EDE3D3] disabled:text-[#A6988A] enabled:bg-[#251A14] enabled:text-white enabled:hover:bg-black"
                >
                  {link === "loading" ? "Checking…" : link === "ok" ? "Added ✓" : "Fetch link"}
                </button>
              </div>
            </div>

            <label className="block">
              <Label optional>Sample posts or guidelines</Label>
              <textarea
                value={samples}
                onChange={(e) => setSamples(e.target.value)}
                rows={4}
                placeholder="Paste a few posts they love, or their brand guidelines..."
                className={areaCls}
                disabled={generating}
              />
            </label>

            {generating ? (
              <div className="rounded-2xl border border-[#E6DCCD] bg-white p-5">
                <ul className="space-y-3">
                  {STEPS.map((s, i) => {
                    const done = step > i;
                    const current = step === i;
                    return (
                      <li key={s} className={`flex items-center gap-3 text-[14px] ${done || current ? "text-[#251A14]" : "text-[#A6988A]"}`}>
                        <span
                          className="flex h-6 w-6 items-center justify-center rounded-full text-white"
                          style={{ background: done ? "#16A34A" : current ? ORANGE : "#E6DCCD" }}
                        >
                          {done ? (
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round">
                              <path d="m5 12 5 5 9-10" />
                            </svg>
                          ) : current ? (
                            <span className="h-2 w-2 animate-pulse rounded-full bg-white" />
                          ) : null}
                        </span>
                        {s}
                      </li>
                    );
                  })}
                </ul>
              </div>
            ) : (
              <div className="space-y-3 pt-1">
                <button
                  type="button"
                  disabled={!canGenerate}
                  onClick={() => setStep(0)}
                  className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl text-[14px] font-semibold transition disabled:cursor-not-allowed disabled:bg-[#EDE3D3] disabled:text-[#A6988A] enabled:bg-[#FF4F26] enabled:text-white enabled:hover:bg-[#e8431d]"
                >
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />
                    <path d="M19 16v4M17 18h4" />
                  </svg>
                  Generate brand voice
                </button>
                <button
                  type="button"
                  onClick={() => setMode("manual")}
                  className="h-12 w-full rounded-2xl bg-[#EFE4D4] text-[14px] font-medium text-[#251A14] transition hover:bg-[#E8DCCB]"
                >
                  Fill manually
                </button>
              </div>
            )}
          </>
        ) : (
          <>
            <div>
              <Label>Tone of voice</Label>
              <div className="flex flex-wrap gap-2">
                {TONES.map((t) => {
                  const on = tones.includes(t);
                  return (
                    <button
                      key={t}
                      type="button"
                      onClick={() => toggleTone(t)}
                      aria-pressed={on}
                      className={`h-10 rounded-full border px-4 text-[14px] font-medium transition ${
                        on ? "border-[#FF4F26] bg-[#FF4F26] text-white" : "border-[#E6DCCD] bg-white text-[#251A14] hover:border-[#251A14]"
                      }`}
                    >
                      {t}
                    </button>
                  );
                })}
              </div>
            </div>

            <label className="block">
              <Label optional>Voice notes and guidelines</Label>
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={4} placeholder="How do they talk to customers? Any must-follow rules?" className={areaCls} />
            </label>

            <label className="block">
              <Label optional>Words or claims to avoid</Label>
              <input value={avoid} onChange={(e) => setAvoid(e.target.value)} placeholder="e.g. cheap, guaranteed, #1" className={inputCls} />
            </label>

            <div className="space-y-3 pt-1">
              <button
                type="button"
                disabled={!canSave}
                onClick={saveManual}
                className="h-12 w-full rounded-2xl text-[14px] font-semibold transition disabled:cursor-not-allowed disabled:bg-[#EDE3D3] disabled:text-[#A6988A] enabled:bg-[#FF4F26] enabled:text-white enabled:hover:bg-[#e8431d]"
              >
                Save brand profile
              </button>
              <button
                type="button"
                onClick={() => setMode("auto")}
                className="h-12 w-full rounded-2xl bg-[#EFE4D4] text-[14px] font-medium text-[#251A14] transition hover:bg-[#E8DCCB]"
              >
                Decode from a website instead
              </button>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
