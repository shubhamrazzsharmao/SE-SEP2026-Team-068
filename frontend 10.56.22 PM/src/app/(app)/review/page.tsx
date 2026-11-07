import type { Metadata } from "next";
import { ApprovalsBoard } from "@/components/review/approvals-board";

export const metadata: Metadata = { title: "Pending approvals · Mosaiq" };

export default function ReviewsPage() {
  return <ApprovalsBoard />;
}