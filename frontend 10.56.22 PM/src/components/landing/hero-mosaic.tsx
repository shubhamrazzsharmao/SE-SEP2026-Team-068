"use client";

import { useRef, type PointerEvent as ReactPointerEvent } from "react";
import type { IconType } from "react-icons";
import { FaLinkedinIn, FaInstagram } from "react-icons/fa6";
import { LuPenLine, LuMail, LuFileText } from "react-icons/lu";

const COLS = 10;
const ROWS = 8;
const FADE_MODE: "corner" | "top" = "corner"; // switch to "top" to compare
const CENTER = { c: 6, r: 3.5 };
const RADIUS = 6.5;
const RIPPLE_RADIUS = 150;

const motionStyle = {
  transform: "translateY(calc(var(--p, 0) * -8px)) scale(calc(1 + var(--p, 0) * 0.06))",
  transition: "transform 160ms ease-out, opacity 160ms ease-out",
};

type Special = { icon: IconType; label: string; text: string; bg: string };

// key = "row-col"
const specials: Record<string, Special> = {
  "0-2": {
    icon: LuFileText,
    label: "Your source",
    text: "One blog, report or transcript goes in.",
    bg: "bg-brown",
  },
  "0-7": {
    icon: LuMail,
    label: "Newsletter",
    text: "Coming soon: long-form summaries.",
    bg: "bg-muted",
  },
  "2-9": {
    icon: FaLinkedinIn,
    label: "LinkedIn post",
    text: "Hook, body, hashtags and CTA, written in your client's voice.",
    bg: "bg-accent",
  },
  "5-9": {
    icon: FaInstagram,
    label: "Instagram caption",
    text: "Shorter, punchier, with alt text included.",
    bg: "bg-brand",
  },
  "7-6": {
    icon: LuPenLine,
    label: "Blog article",
    text: "A long-form piece built from the same facts.",
    bg: "bg-ink",
  },
};

function fillerClass(r: number, c: number) {
  const h = (c * 7 + r * 13 + c * r) % 11;
  if (h === 0) return "bg-brand/70";
  if (h === 3) return "bg-ink/70";
  if (h === 5) return "bg-accent/60";
  if (h <= 8) return "bg-ink/[0.05]";
  return "bg-white/50";
}

function fade(r: number, c: number) {
  if (FADE_MODE === "top") {
    return Math.max(0.06, 1 - Math.pow(r / (ROWS - 1), 1.2));
  }
  const dist = Math.hypot(COLS - 1 - c, r);
  const max = Math.hypot(COLS - 1, ROWS - 1);
  return Math.max(0.06, 1 - dist / (max * 0.85));
}

export function HeroMosaic() {
  const cells = Array.from({ length: COLS * ROWS }, (_, n) => ({
    r: Math.floor(n / COLS),
    c: n % COLS,
  }));
  const rootRef = useRef<HTMLDivElement>(null);
  const frame = useRef<number | null>(null);

  function onPointerMove(e: ReactPointerEvent<HTMLDivElement>) {
    const { clientX, clientY } = e;
    cancelAnimationFrame(frame.current ?? 0);
    frame.current = requestAnimationFrame(() => {
      const tiles = rootRef.current?.querySelectorAll<HTMLElement>("[data-tile]");
      tiles?.forEach((el) => {
        const rect = el.getBoundingClientRect();
        const d = Math.hypot(rect.left + rect.width / 2 - clientX, rect.top + rect.height / 2 - clientY);
        el.style.setProperty("--p", Math.max(0, 1 - d / RIPPLE_RADIUS).toFixed(3));
      });
    });
  }

  function onPointerLeave() {
    cancelAnimationFrame(frame.current ?? 0);
    rootRef.current?.querySelectorAll<HTMLElement>("[data-tile]").forEach((el) => {
      el.style.setProperty("--p", "0");
    });
  }

  return (
    <div className="absolute left-[55%] top-1/2 z-0 hidden w-[640px] -translate-x-1/2 -translate-y-1/2 lg:block">
      <div
        ref={rootRef}
        onPointerMove={onPointerMove}
        onPointerLeave={onPointerLeave}
        className="grid grid-cols-10 gap-2"
      >
        {cells.map(({ r, c }) => {
          const special = specials[`${r}-${c}`];

          if (special) {
            const Icon = special.icon;
            return (
              <div
                key={`${r}-${c}`}
                data-tile
                className={`group relative grid aspect-square place-items-center rounded-md text-paper transition-transform duration-200 hover:z-30 hover:-translate-y-1.5 hover:scale-110 ${special.bg}`}
                style={motionStyle}
              >
                <Icon size={18} />
                <div className="pointer-events-none absolute bottom-[115%] left-1/2 z-30 w-48 -translate-x-1/2 rounded-xl bg-ink p-3 text-left text-xs text-paper opacity-0 shadow-lg transition-opacity duration-200 group-hover:opacity-100">
                  <p className="font-semibold">{special.label}</p>
                  <p className="mt-1 text-paper/70">{special.text}</p>
                </div>
              </div>
            );
          }

          return (
            <div
              key={`${r}-${c}`}
              data-tile
              style={{ ["--o" as string]: fade(r, c), ...motionStyle }}
              className={`aspect-square rounded-md border border-ink/[0.07] transition-all duration-200 [opacity:var(--o)] hover:-translate-y-1 hover:scale-105 hover:bg-brand/40 hover:opacity-100 ${fillerClass(r, c)}`}
            />
          );
        })}
      </div>
    </div>
  );
}









































// "use client";
//
// import { useRef } from "react";
// import type { IconType } from "react-icons";
// import { FaLinkedinIn, FaInstagram } from "react-icons/fa6";
// import { LuPenLine, LuMail, LuFileText } from "react-icons/lu";
//
// const COLS = 10;
// const ROWS = 8;
// const CENTER = { c: 5.5, r: 3.5 };
// const FADE_RADIUS = 7; // in tiles: bigger = more of the grid stays visible
// const RIPPLE_RADIUS = 150; // in px: how far the cursor effect reaches
//
// type Big = {
//   c: number; // column (0-based)
//   r: number; // row (0-based)
//   w: number; // width in tiles
//   h: number; // height in tiles
//   bg: string;
//   icon?: IconType;
//   label?: string;
//   text?: string;
//   tip?: "top" | "bottom";
// };
//
// const bigs: Big[] = [
//   { c: 0, r: 1, w: 2, h: 2, bg: "bg-brown", icon: LuFileText, label: "Your source", text: "One blog, report or transcript goes in." },
//   { c: 3, r: 0, w: 2, h: 1, bg: "bg-muted", icon: LuMail, label: "Newsletter", text: "Coming soon: long-form summaries.", tip: "bottom" },
//   { c: 8, r: 0, w: 2, h: 2, bg: "bg-brand/80" },
//   { c: 7, r: 3, w: 2, h: 2, bg: "bg-accent", icon: FaLinkedinIn, label: "LinkedIn post", text: "Hook, body, hashtags and CTA, written in your client's voice." },
//   { c: 4, r: 5, w: 2, h: 2, bg: "bg-brand", icon: FaInstagram, label: "Instagram caption", text: "Shorter, punchier, with alt text included." },
//   { c: 8, r: 6, w: 2, h: 1, bg: "bg-ink", icon: LuPenLine, label: "Blog article", text: "A long-form piece built from the same facts." },
//   { c: 1, r: 5, w: 2, h: 1, bg: "bg-ink/70" },
// ];
//
// // Cells covered by the big tiles, so fillers skip them
// const occupied = new Set<string>();
// bigs.forEach((b) => {
//   for (let r = b.r; r < b.r + b.h; r++) {
//     for (let c = b.c; c < b.c + b.w; c++) occupied.add(`${r}-${c}`);
//   }
// });
//
// const fillers: { r: number; c: number }[] = [];
// for (let r = 0; r < ROWS; r++) {
//   for (let c = 0; c < COLS; c++) {
//     if (!occupied.has(`${r}-${c}`)) fillers.push({ r, c });
//   }
// }
//
// function fillerClass(r: number, c: number) {
//   const h = (c * 7 + r * 13 + c * r) % 11;
//   if (h === 0) return "bg-brand/70";
//   if (h === 3) return "bg-ink/70";
//   if (h === 5) return "bg-accent/60";
//   if (h <= 8) return "bg-ink/[0.05]";
//   return "bg-white/50";
// }
//
// function baseOpacity(r: number, c: number) {
//   const dist = Math.hypot(c - CENTER.c, r - CENTER.r);
//   return Math.max(0.06, 1 - dist / FADE_RADIUS);
// }
//
// // --p (0 to 1) is set per tile by the pointer handler below
// const motionStyle = {
//   transform: "translateY(calc(var(--p, 0) * -8px)) scale(calc(1 + var(--p, 0) * 0.06))",
//   transition: "transform 160ms ease-out, opacity 160ms ease-out",
// };
//
// const tint = (
//   <span
//     className="pointer-events-none absolute inset-0 rounded-md bg-brand"
//     style={{ opacity: "calc(var(--p, 0) * 0.55)" }}
//   />
// );
//
// export function HeroMosaic() {
//   const rootRef = useRef<HTMLDivElement>(null);
//   const frame = useRef(0);
//
//   function onPointerMove(e: React.PointerEvent) {
//     const { clientX, clientY } = e;
//     cancelAnimationFrame(frame.current);
//     frame.current = requestAnimationFrame(() => {
//       const tiles = rootRef.current?.querySelectorAll<HTMLElement>("[data-tile]");
//       tiles?.forEach((el) => {
//         const b = el.getBoundingClientRect();
//         const d = Math.hypot(b.left + b.width / 2 - clientX, b.top + b.height / 2 - clientY);
//         el.style.setProperty("--p", Math.max(0, 1 - d / RIPPLE_RADIUS).toFixed(3));
//       });
//     });
//   }
//
//   function onPointerLeave() {
//     cancelAnimationFrame(frame.current);
//     rootRef.current?.querySelectorAll<HTMLElement>("[data-tile]").forEach((el) => {
//       el.style.setProperty("--p", "0");
//     });
//   }
//
//   return (
//     <div className="absolute left-[55%] top-1/2 z-0 hidden w-[640px] -translate-x-1/2 -translate-y-1/2 lg:block">
//       <div
//         ref={rootRef}
//         onPointerMove={onPointerMove}
//         onPointerLeave={onPointerLeave}
//         className="grid gap-2"
//         style={{
//           gridTemplateColumns: `repeat(${COLS}, 1fr)`,
//           gridTemplateRows: `repeat(${ROWS}, 1fr)`,
//           aspectRatio: `${COLS} / ${ROWS}`,
//         }}
//       >
//         {fillers.map(({ r, c }) => {
//           const o = baseOpacity(r, c);
//           return (
//             <div
//               key={`f-${r}-${c}`}
//               data-tile
//               className={`relative rounded-md border border-ink/[0.07] ${fillerClass(r, c)}`}
//               style={{
//                 gridColumn: c + 1,
//                 gridRow: r + 1,
//                 ...motionStyle,
//                 opacity: `calc(${o} + (1 - ${o}) * var(--p, 0))`,
//               }}
//             >
//               {tint}
//             </div>
//           );
//         })}
//
//         {bigs.map((b, i) => {
//           const Icon = b.icon;
//           return (
//             <div
//               key={`b-${i}`}
//               data-tile
//               className={`group relative grid place-items-center rounded-md text-paper hover:z-30 ${b.bg}`}
//               style={{
//                 gridColumn: `${b.c + 1} / span ${b.w}`,
//                 gridRow: `${b.r + 1} / span ${b.h}`,
//                 ...motionStyle,
//               }}
//             >
//               {!Icon && tint}
//               {Icon && <Icon size={b.w * b.h >= 4 ? 26 : 18} />}
//               {b.label && (
//                 <div
//                   className={`pointer-events-none absolute left-1/2 z-30 w-48 -translate-x-1/2 rounded-xl bg-ink p-3 text-left text-xs text-paper opacity-0 shadow-lg transition-opacity duration-200 group-hover:opacity-100 ${
//                     b.tip === "bottom" ? "top-[115%]" : "bottom-[115%]"
//                   }`}
//                 >
//                   <p className="font-semibold">{b.label}</p>
//                   <p className="mt-1 text-paper/70">{b.text}</p>
//                 </div>
//               )}
//             </div>
//           );
//         })}
//       </div>
//     </div>
//   );
// }