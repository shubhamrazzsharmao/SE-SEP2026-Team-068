"""Dashboard and health views."""

from pydantic import BaseModel


class StatusCounts(BaseModel):
    draft: int = 0
    pending_review: int = 0
    approved: int = 0
    rejected: int = 0


class CampaignCounts(BaseModel):
    campaign_id: int
    name: str
    counts: StatusCounts


class DashboardOut(BaseModel):
    totals: StatusCounts
    campaigns: list[CampaignCounts]


class HealthOut(BaseModel):
    status: str
    database: bool
