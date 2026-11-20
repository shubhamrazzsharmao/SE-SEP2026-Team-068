"""Campaign-scoped authorisation.

Rules (also in the README role matrix):
  * Not a member of the campaign  -> 404 (existence is not revealed)
  * Member, but role not allowed  -> 403
"""
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.core.errors import AppError, not_found
from app.enums import MemberRole as R
from app.models import Brief, Campaign, CampaignMember, ContentPiece, User

# Who may do what inside a campaign
CAN_WRITE_BRIEFS = {R.owner, R.creator}
CAN_EDIT_CONTENT = {R.owner, R.creator, R.reviewer}
CAN_DELETE_CONTENT = {R.owner, R.creator}
CAN_REVIEW = {R.reviewer}
CAN_MANAGE_MEMBERS = {R.owner}


def _forbidden(roles: Iterable[R]) -> AppError:
    names = ", ".join(sorted(r.value for r in roles))
    return AppError(403, "FORBIDDEN", f"This action requires one of these campaign roles: {names}.")


def campaign_for_member(db: Session, campaign_id: int, user: User,
                        roles: Optional[set[R]] = None) -> tuple[Campaign, CampaignMember]:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None or campaign.deleted_at is not None:
        raise not_found("Campaign")
    member = db.get(CampaignMember, (campaign_id, user.id))
    if member is None:
        raise not_found("Campaign")
    if roles is not None and member.member_role not in roles:
        raise _forbidden(roles)
    return campaign, member


def brief_for_member(db: Session, brief_id: int, user: User,
                     roles: Optional[set[R]] = None) -> tuple[Brief, Campaign, CampaignMember]:
    brief = db.get(Brief, brief_id)
    if brief is None:
        raise not_found("Brief")
    try:
        campaign, member = campaign_for_member(db, brief.campaign_id, user, roles)
    except AppError as e:
        if e.status_code == 404:
            raise not_found("Brief")
        raise
    return brief, campaign, member


def piece_for_member(db: Session, piece_id: int, user: User,
                     roles: Optional[set[R]] = None) -> tuple[ContentPiece, CampaignMember]:
    piece = db.get(ContentPiece, piece_id)
    if piece is None or piece.deleted_at is not None:
        raise not_found("Content piece")
    try:
        _, member = campaign_for_member(db, piece.campaign_id, user, roles)
    except AppError as e:
        if e.status_code == 404:
            raise not_found("Content piece")
        raise
    return piece, member
