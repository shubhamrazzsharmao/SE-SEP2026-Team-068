"use client";

import { motion } from "motion/react";

const mockPost = {
  platform: "LinkedIn",
  index: "Post 3 of 12",
  status: "Approved",
  hook: "Most campaigns don't fail at the idea. They fail at the repurposing.",
  tags: "#ContentStrategy #AgencyLife",
  claims: "3 claims checked against source",
  approvedCount: 7,
  totalCount: 12,
};

function Float({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      animate={{ y: [0, -8, 0] }}
      transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
    >
      {children}
    </motion.div>
  );
}

export function PostPreviewCard() {
  const pct = (mockPost.approvedCount / mockPost.totalCount) * 100;

  return (
    <div className="relative mx-auto mb-14 w-full max-w-sm">
      <Float className="absolute -left-2 -top-5 z-20 sm:-left-8">
        <div className="rounded-full border border-line bg-white px-4 py-2 text-sm font-semibold shadow-md">
          <span className="text-accent">✦</span> Brand voice 92/100
        </div>
      </Float>

      <div className="drop-shadow-xl">
        <div className="ticket rounded-3xl bg-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-md bg-accent text-xs font-bold text-white">
                in
              </span>
              <div className="leading-tight">
                <p className="text-sm font-semibold">{mockPost.platform}</p>
                <p className="text-xs text-muted">{mockPost.index}</p>
              </div>
            </div>
            <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
              ✓ {mockPost.status}
            </span>
          </div>

          <p className="mt-5 text-lg font-semibold leading-snug">{mockPost.hook}</p>
          <div className="mt-4 space-y-2">
            <div className="h-2 w-full rounded bg-line" />
            <div className="h-2 w-11/12 rounded bg-line" />
            <div className="h-2 w-2/3 rounded bg-line" />
          </div>
          <p className="mt-4 text-sm font-medium text-accent">{mockPost.tags}</p>

          <div className="mt-5 flex items-center gap-2 border-t border-dashed border-line pt-4 text-sm text-muted">
            <span className="text-green-600">●</span> {mockPost.claims}
          </div>

          <div className="mt-4">
            <div className="flex justify-between text-xs font-medium text-muted">
              <span>Campaign progress</span>
              <span>
                {mockPost.approvedCount} of {mockPost.totalCount} approved
              </span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-line">
              <div className="h-2 rounded-full bg-brand" style={{ width: `${pct}%` }} />
            </div>
          </div>
        </div>
      </div>

      <div className="absolute -bottom-6 left-6 z-10 rounded-2xl bg-brown px-5 py-3 text-paper">
        <p className="display text-lg" style={{ fontStretch: "110%" }}>
          1 source → 12 posts
        </p>
      </div>
        <Float className="absolute -bottom-12 right-0 z-20 sm:-right-6">
        <div className="rounded-2xl border border-line bg-white px-4 py-2 text-sm shadow-md">
          <span className="font-semibold">Dana (client)</span> approved ✓
        </div>
      </Float>
    </div>
  );
}