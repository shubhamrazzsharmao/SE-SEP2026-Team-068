"""Controller for the dashboard and health check.

HTTP only: validated input comes in (app.schemas), dashboard_service does the work, a view goes out.
"""
from fastapi import APIRouter

from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.schemas import CampaignCounts, DashboardOut, HealthOut, StatusCounts
from app.services import dashboard_service

router = APIRouter()


@router.get("/dashboard", response_model=DashboardOut, tags=["Dashboard"], responses=errs(401),
            openapi_extra={"x-user-stories": ["US10", "US6"]})
def dashboard(db: DB, user: CurrentUser):
    """Counts of draft / pending-review / approved / rejected pieces, in total and per campaign,
    over the campaigns the caller belongs to. The dashboard is the same for every role.

    **User stories:** US10 (track status), US6 (reviewers see what is pending).
    """
    totals, per_campaign = dashboard_service.counts_for_user(db, user)
    return DashboardOut(totals=StatusCounts(**totals), campaigns=[
        CampaignCounts(campaign_id=cid, name=name, counts=StatusCounts(**counts))
        for cid, name, counts in per_campaign])


@router.get("/health", response_model=HealthOut, tags=["Dashboard"],
            summary="Liveness and database connectivity check (no auth)")
def health():
    """Returns `database: true` when the backend can reach Postgres. Use it to verify the
    Supabase connection string."""
    if dashboard_service.database_ok():
        return HealthOut(status="ok", database=True)
    return HealthOut(status="degraded", database=False)
