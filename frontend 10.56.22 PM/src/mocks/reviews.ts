import type { ReviewPost } from "@/types/review";

// Fake data until the API exists. Swap for a TanStack Query hook (useReviews).
export const MOCK_REVIEWS: ReviewPost[] = [
  {
    id: "p1",
    client: "Sunrise Coffee Co.",
    platform: "instagram",
    createdAt: "7.11.2026, 09:42",
    title: "Founder story for Diwali",
    body:
      "Twelve years ago we roasted our first batch in a garage in Pune. ☕\n\nThis Diwali, the same beans go into a limited gift box, hand-packed by the people who taught us the craft.\n\nPro tip: gift the box with a handwritten note. Customers tell us that is what they remember most. Order before 28 October for delivery in time for the festival.",
    version: 3,
    status: "internal",
    palette: ["#FF4F26", "#FF7A57", "#251A14", "#E8DCCB", "#8F9BDB"],
    comments: [
      { id: "c1", author: "Olivia", role: "team", time: "7.11.2026, 10:13", body: "Updated: tightened the hook and moved the tip up. Ready for another pass." },
      { id: "c2", author: "Sarah", role: "team", time: "7.11.2026, 10:20", body: "@Olivia Nguyen can we rework the second paragraph? The gift-note tip is the strongest angle and it's buried right now." },
    ],
  },
  {
    id: "p2",
    client: "Northwind Studio",
    platform: "linkedin",
    createdAt: "6.11.2026, 17:05",
    title: "Delivery time case study",
    body:
      "Delivery time dropped from 5 days to 2 days after launch.\n\nHere is what changed: one shared checklist, one owner per handoff, and every decision written down. No new tools, no extra headcount.\n\nWe wrote up the full process in the report linked below.",
    version: 2,
    status: "internal",
    palette: ["#8F9BDB", "#251A14", "#FF4F26", "#E8DCCB", "#B7B3CF"],
    comments: [
      { id: "c3", author: "Maria", role: "team", time: "6.11.2026, 17:30", body: "Claims checked against the source report, all supported." },
    ],
  },
  {
    id: "p3",
    client: "Bloom Dental",
    platform: "instagram",
    createdAt: "5.11.2026, 12:10",
    title: "Smile check reminder",
    body:
      "A quick reminder from the Bloom team: a check-up every six months keeps small problems small. 🦷\n\nBook yours this week and get a free whitening consult.",
    version: 2,
    status: "client",
    palette: ["#FF7A57", "#E8DCCB", "#8F9BDB", "#251A14", "#EFE4D4"],
    comments: [
      { id: "c4", author: "Olivia", role: "team", time: "5.11.2026, 12:40", body: "Internal approved v2. Sent to the client." },
      { id: "c5", author: "Dana (client)", role: "client", time: "6.11.2026, 09:02", body: "Looks lovely. Just checking the offer dates with the clinic before we sign off." },
    ],
  },
];
