export type Platform = "instagram" | "linkedin";

// internal = in team review, rework = changes requested, client = waiting on client, approved = signed off
export type ReviewStatus = "internal" | "rework" | "client" | "approved";

export type ReviewComment = {
  id: string;
  author: string;
  role: "team" | "client" | "system";
  time: string;
  body: string;
};

export type ReviewPost = {
  id: string;
  client: string;
  platform: Platform;
  createdAt: string;
  title: string;
  body: string;
  version: number;
  status: ReviewStatus;
  palette: string[];
  comments: ReviewComment[];
};
