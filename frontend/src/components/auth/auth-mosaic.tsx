"use client";

import { useEffect, useRef } from "react";

type Feature = {
  col: number;
  row: number;
  w?: number;
  h?: number;
  bg: string;
  icon?: "mail" | "doc" | "in" | "ig" | "pen";
};

// Hand-placed "hero" tiles (grid is 6 cols x 8 rows). Everything else is filler.
const FEATURES: Feature[] = [
  { col: 1, row: 1, bg: "#FF4F26", w: 2, h: 2, icon: "ig" },
  { col: 4, row: 1, bg: "#3A2C24", w: 2, icon: "mail" },
  { col: 5, row: 2, bg: "#8F9BDB", icon: "in" },
  { col: 1, row: 7, bg: "#FAF6F0", w: 2, h: 2, icon: "doc" },
  { col: 5, row: 7, bg: "#8F9BDB", w: 2, h: 2, icon: "pen" },
  { col: 4, row: 8, bg: "#FF7A57" },
  { col: 3, row: 7, bg: "#B7B3CF" },
];

const FILLERS = [
  "#4A3A30",
  "#3A2C24",
  "#4A3A30",
  "#6B5B4E",
  "#B7B3CF",
  "#3A2C24",
  "#8F9BDB",
  "#4A3A30",
  "#BBAE9C",
  "#3A2C24",
  "#FF7A57",
  "#4A3A30",
];

/* ------------------------------------------------------------------ */
/*  Cursor ripple                                                      */
/* ------------------------------------------------------------------ */

const RADIUS = 160; // px: how far the ripple reaches from the pointer
const MAX_LIFT = 10; // px: how far the closest tile rises
const MAX_SCALE = 0.1; // closest tile grows by 10%
const MAX_TINT = 0.75; // peak opacity of the orange tint
const EASE = 0.14; // 0-1: lower = softer, slower follow/fade

type TileState = { el: HTMLElement; tint: HTMLElement | null; base: number; cur: number };

function useMosaicRipple(rootRef: React.RefObject<HTMLDivElement | null>) {
  useEffect(() => {
    const root = rootRef.current;
    const host = root?.parentElement; // listen on the panel so overlay text doesn't block events
    if (!root || !host) return;

    // Skip on touch-only devices and for reduced-motion users
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (!window.matchMedia("(hover: hover)").matches) return;

    const tiles: TileState[] = Array.from(root.querySelectorAll<HTMLElement>("[data-tile]")).map((el) => ({
      el,
      tint: el.querySelector<HTMLElement>("[data-tint]"),
      base: parseFloat(el.dataset.base ?? "1"),
      cur: 0,
    }));

    let pointer: { x: number; y: number } | null = null;
    let raf = 0;

    const frame = () => {
      let active = false;

      for (const t of tiles) {
        let target = 0;
        if (pointer) {
          const r = t.el.getBoundingClientRect();
          const dx = r.left + r.width / 2 - pointer.x;
          const dy = r.top + r.height / 2 - pointer.y;
          const d = Math.hypot(dx, dy);
          // Smooth falloff: 1 at the cursor, 0 at RADIUS (ease-out curve)
          const k = Math.max(0, 1 - d / RADIUS);
          target = k * k * (3 - 2 * k); // smoothstep
        }

        t.cur += (target - t.cur) * EASE;
        if (Math.abs(target - t.cur) < 0.001) t.cur = target;
        if (t.cur > 0 || target > 0) active = true;

        const s = t.cur;
        t.el.style.transform = s
          ? `translate3d(0, ${(-s * MAX_LIFT).toFixed(2)}px, 0) scale(${(1 + s * MAX_SCALE).toFixed(3)})`
          : "";
        t.el.style.boxShadow = s ? `0 ${(s * 14).toFixed(1)}px ${(s * 24).toFixed(1)}px rgba(0,0,0,${(s * 0.35).toFixed(3)})` : "";
        t.el.style.opacity = String(t.base + (1 - t.base) * s);
        t.el.style.zIndex = s > 0.05 ? "1" : "";
        if (t.tint) t.tint.style.opacity = String(s * MAX_TINT);
      }

      raf = active ? requestAnimationFrame(frame) : 0;
    };

    const start = () => {
      if (!raf) raf = requestAnimationFrame(frame);
    };

    const onMove = (e: PointerEvent) => {
      pointer = { x: e.clientX, y: e.clientY };
      start();
    };
    const onLeave = () => {
      pointer = null;
      start(); // keep running so tiles ease back down
    };

    host.addEventListener("pointermove", onMove);
    host.addEventListener("pointerleave", onLeave);
    return () => {
      host.removeEventListener("pointermove", onMove);
      host.removeEventListener("pointerleave", onLeave);
      cancelAnimationFrame(raf);
    };
  }, [rootRef]);
}

/* ------------------------------------------------------------------ */

function Icon({ name }: { name: NonNullable<Feature["icon"]> }) {
  const common = {
    width: 26,
    height: 26,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (name) {
    case "mail":
      return (
        <svg {...common}>
          <rect x="3" y="5" width="18" height="14" rx="2" />
          <path d="m3 7 9 6 9-6" />
        </svg>
      );
    case "doc":
      return (
        <svg {...common}>
          <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
          <path d="M14 3v5h5M9 13h6M9 17h6" />
        </svg>
      );
    case "pen":
      return (
        <svg {...common}>
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z" />
        </svg>
      );
    case "ig":
      return (
        <svg {...common}>
          <rect x="3" y="3" width="18" height="18" rx="5" />
          <circle cx="12" cy="12" r="4" />
          <circle cx="17.5" cy="6.5" r="0.6" fill="currentColor" />
        </svg>
      );
    case "in":
      return <span className="text-[22px] font-extrabold leading-none tracking-tight">in</span>;
  }
}

export function AuthMosaic() {
  const rootRef = useRef<HTMLDivElement>(null);
  useMosaicRipple(rootRef);

  const occupied = FEATURES.reduce((n, f) => n + (f.w ?? 1) * (f.h ?? 1), 0);
  const fillerCount = 48 - occupied;

  return (
    <div
      ref={rootRef}
      aria-hidden
      className="absolute inset-0 isolate grid gap-2 p-4"
      style={{
        gridTemplateColumns: "repeat(6, 1fr)",
        gridTemplateRows: "repeat(8, 1fr)",
        gridAutoRows: 0,
      }}
    >
      {FEATURES.map((f, i) => (
        <div
          key={`f-${i}`}
          data-tile
          data-base="1"
          className="relative flex items-center justify-center rounded-xl will-change-transform"
          style={{
            gridColumn: `${f.col} / span ${f.w ?? 1}`,
            gridRow: `${f.row} / span ${f.h ?? 1}`,
            background: f.bg,
            color: f.bg === "#FAF6F0" ? "#251A14" : "#fff",
          }}
        >
          <span data-tint className="pointer-events-none absolute inset-0 rounded-xl bg-[#FF4F26] opacity-0" />
          {f.icon ? (
            <span className="relative">
              <Icon name={f.icon} />
            </span>
          ) : null}
        </div>
      ))}
      {Array.from({ length: fillerCount }).map((_, i) => {
        const base = 0.35 + ((i * 13) % 5) * 0.12;
        return (
          <div
            key={`t-${i}`}
            data-tile
            data-base={base}
            className="relative rounded-xl will-change-transform"
            style={{ background: FILLERS[(i * 7 + 3) % FILLERS.length], opacity: base }}
          >
            <span data-tint className="pointer-events-none absolute inset-0 rounded-xl bg-[#FF4F26] opacity-0" />
          </div>
        );
      })}
    </div>
  );
}
