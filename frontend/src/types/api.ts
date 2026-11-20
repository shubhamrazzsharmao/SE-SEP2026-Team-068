// Types mirroring the FastAPI backend (backend/app/schemas.py, backend/app/enums.py).
// Keep these in sync with backend/docs/openapi.yaml.

export type ContentStatus = "draft" | "pending_review" | "approved" | "rejected";
export type Platform = "blog" | "linkedin" | "facebook" | "instagram";
export type MemberRole = "owner" | "creator" | "reviewer" | "brand_manager";
export type UserRole = "user" | "admin";
export type VersionOrigin = "ai_generated" | "human_edit" | "variation" | "regeneration";
export type BriefStatus = "draft" | "generating" | "generated";

export type ApiError = { detail: string; code: string; errors?: unknown[]; job_id?: number };

export type UserOut = { id: string; name: string; email: string; role: UserRole };

export type BrandOut = {
  id: number;
  owner_id: string;
  name: string;
  tone: string;
  preferred_terms: string[];
  avoided_terms: string[];
  updated_by: string | null;
  created_at: string;
  updated_at: string;
};

export type CampaignOut = {
  id: number;
  brand_id: number;
  brand_name: string;
  name: string;
  description: string | null;
  created_at: string;
  my_role: MemberRole;
};

export type VersionOut = {
  id: number;
  version_no: number;
  body: string;
  creative_suggestion: string | null;
  origin: VersionOrigin;
  model_name: string | null;
  flags: Record<string, unknown> | null;
  created_by: string | null;
  created_at: string;
};

export type ContentPieceOut = {
  id: number;
  brief_id: number;
  campaign_id: number;
  platform: Platform;
  status: ContentStatus;
  created_by: string;
  created_at: string;
  updated_at: string;
  current_version: VersionOut | null;
  rejection_reason: string | null;
};

export type ActivityOut = {
  id: number;
  campaign_id: number;
  piece_id: number | null;
  user_id: string;
  user_name: string;
  action: string;
  version_no: number | null;
  detail: Record<string, unknown> | null;
  created_at: string;
};

export type StatusCounts = Record<ContentStatus, number>;

export type DashboardOut = {
  totals: StatusCounts;
  campaigns: { campaign_id: number; name: string; counts: StatusCounts }[];
};

export type ReviewDecision = "approved" | "rejected" | "changes_requested";

export type MemberOut = { user_id: string; name: string; email: string; member_role: MemberRole; joined_at: string };

export type BriefOut = {
  id: number;
  campaign_id: number;
  created_by: string;
  topic: string;
  objective: string;
  target_audience: string | null;
  key_messages: string | null;
  tone: string | null;
  effective_tone: string;
  platforms: Platform[];
  status: BriefStatus;
  created_at: string;
  updated_at: string;
};

export type ReviewOut = {
  id: number;
  version_no: number;
  reviewer_id: string;
  decision: ReviewDecision;
  reason: string | null;
  feedback: string | null;
  created_at: string;
};

export type ContentPieceDetail = ContentPieceOut & { brief: BriefOut; versions: VersionOut[]; reviews: ReviewOut[] };

export type CommentOut = { id: number; piece_id: number; user_id: string; author_name: string; body: string; created_at: string };

export type GenerateOut = { job: { id: number; status: string; error_message: string | null }; pieces: ContentPieceOut[] };
