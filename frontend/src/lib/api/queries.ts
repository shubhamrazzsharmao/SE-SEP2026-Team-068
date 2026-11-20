import "server-only";
import { cache } from "react";
import { api } from "@/lib/api/client";
import type {
  ActivityOut, BrandOut, BriefOut, CampaignOut, CommentOut, ContentPieceDetail, ContentPieceOut,
  ContentStatus, DashboardOut, MemberOut, UserOut,
} from "@/types/api";

// Read-only backend calls for Server Components. `cache` dedupes calls within one request.
export const getMe = cache(() => api<UserOut>("/me"));
export const listBrands = cache(() => api<BrandOut[]>("/brands"));
export const getBrand = cache((id: string) => api<BrandOut>(`/brands/${id}`));
export const listCampaigns = cache(() => api<CampaignOut[]>("/campaigns"));
export const getCampaign = cache((id: string) => api<CampaignOut>(`/campaigns/${id}`));
export const getDashboardCounts = cache(() => api<DashboardOut>("/dashboard"));
export const listMembers = cache((campaignId: string) => api<MemberOut[]>(`/campaigns/${campaignId}/members`));
export const listBriefs = cache((campaignId: string) => api<BriefOut[]>(`/campaigns/${campaignId}/briefs`));
export const campaignActivity = cache((campaignId: string) => api<ActivityOut[]>(`/campaigns/${campaignId}/activity`));
export const listContent = cache((campaignId: string, status?: ContentStatus) =>
  api<ContentPieceOut[]>(`/campaigns/${campaignId}/content${status ? `?status=${status}` : ""}`));
export const getContent = cache((pieceId: string) => api<ContentPieceDetail>(`/content/${pieceId}`));
export const listComments = cache((pieceId: string) => api<CommentOut[]>(`/content/${pieceId}/comments`));
