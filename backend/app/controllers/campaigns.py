"""Controller for campaigns and members.

HTTP only: validated input comes in (app.schemas), campaign_service does the work, a view goes out.
"""
from fastapi import APIRouter

from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.enums import MemberRole
from app.schemas import ActivityOut, CampaignIn, CampaignOut, MemberIn, MemberOut
from app.services import activity_service, campaign_service

router = APIRouter(prefix="/campaigns", tags=["Campaigns & members"])


@router.post("", response_model=CampaignOut, status_code=201, responses=errs(401, 404, 422),
             openapi_extra={"x-user-stories": ["US11"]})
def create_campaign(body: CampaignIn, db: DB, user: CurrentUser):
    """Create a campaign under one of the caller's brands. The caller is added as `owner`.

    **User stories:** US11 (organise content by client and campaign).
    """
    campaign = campaign_service.create(db, user, body)
    return CampaignOut.build(campaign, MemberRole.owner)


@router.get("", response_model=list[CampaignOut], responses=errs(401),
            openapi_extra={"x-user-stories": ["US11"]})
def list_campaigns(db: DB, user: CurrentUser):
    """List the campaigns the caller belongs to, with the caller's role in each.
    Users only ever see their own campaigns.

    **User stories:** US11.
    """
    return [CampaignOut.build(c, role) for c, role in campaign_service.list_for_user(db, user)]


@router.get("/{campaign_id}", response_model=CampaignOut, responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US11"]})
def get_campaign(campaign_id: int, db: DB, user: CurrentUser):
    """Get one campaign. Non-members receive 404.

    **User stories:** US11.
    """
    campaign, role = campaign_service.get_for_member(db, campaign_id, user)
    return CampaignOut.build(campaign, role)


@router.post("/{campaign_id}/members", response_model=MemberOut, status_code=201,
             responses=errs(401, 403, 404, 409, 422), openapi_extra={"x-user-stories": ["US11"]})
def add_member(campaign_id: int, body: MemberIn, db: DB, user: CurrentUser):
    """Add a user to the campaign with one role (`owner`, `creator`, `reviewer`, `brand_manager`).

    Owner only. The person must have signed in at least once (see `GET /me`). One role per user
    per campaign.

    **User stories:** US11, US6 (reviewers must be added before they can review).
    """
    return campaign_service.add_member(db, campaign_id, user, body)


@router.get("/{campaign_id}/members", response_model=list[MemberOut], responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US11"]})
def list_members(campaign_id: int, db: DB, user: CurrentUser):
    """List campaign members and their roles. Any member can see the list.

    **User stories:** US11.
    """
    return campaign_service.list_members(db, campaign_id, user)


@router.delete("/{campaign_id}/members/{user_id}", status_code=204,
               responses=errs(401, 403, 404, 409), openapi_extra={"x-user-stories": ["US11"]})
def remove_member(campaign_id: int, user_id: str, db: DB, user: CurrentUser):
    """Remove a member. Owner only. A campaign always keeps at least one owner (409 otherwise).
    Content the member created stays in place.

    **User stories:** US11.
    """
    campaign_service.remove_member(db, campaign_id, user, user_id)


@router.get("/{campaign_id}/activity", response_model=list[ActivityOut], responses=errs(401, 403, 404),
            openapi_extra={"x-user-stories": ["US13"]})
def campaign_activity(campaign_id: int, db: DB, user: CurrentUser):
    """Read-only audit log for the whole campaign, newest first: who created, edited,
    regenerated, approved or rejected what.

    Visible to campaign owners and to global admins (admins need not be members).

    **User stories:** US13 (view an activity log).
    """
    return activity_service.for_campaign(db, campaign_id, user)
