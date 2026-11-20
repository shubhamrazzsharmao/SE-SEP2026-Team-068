"""Audit trail: record what users do, and read it back."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.core.logger import log as logger
from app.core.logger import short, who
from app.enums import UserRole
from app.models import ActivityLog, Campaign, User
from app.services.access import CAN_MANAGE_MEMBERS, campaign_for_member, piece_for_member


def record(db: Session, *, campaign_id: int, user_id, action: str, piece_id: Optional[int] = None,
           version_no: Optional[int] = None, detail: Optional[dict] = None) -> None:
    """Add an audit row to the current transaction (the caller commits).

    Actions: campaign_created, member_added, member_removed, brief_created, brief_updated,
    generation_requested, generated, generation_failed, edited, changes_requested,
    regenerated, approved, rejected, commented, deleted.
    """
    user = db.get(User, user_id)  # already loaded for this request, no extra query
    logger.info("Activity: %s | %s | campaign=%s piece=%s version=%s detail=%s", who(user), action,
                campaign_id, piece_id, version_no, short(detail))
    db.add(ActivityLog(campaign_id=campaign_id, piece_id=piece_id, user_id=user_id,
                       action=action, version_no=version_no, detail=detail))


def for_campaign(db: Session, campaign_id: int, user: User) -> list[ActivityLog]:
    """Whole-campaign log, newest first. Campaign owners and global admins only."""
    if user.role != UserRole.admin:
        campaign_for_member(db, campaign_id, user, CAN_MANAGE_MEMBERS)
    elif db.get(Campaign, campaign_id) is None:
        raise not_found("Campaign")
    return list(db.scalars(select(ActivityLog).where(ActivityLog.campaign_id == campaign_id)
                           .order_by(ActivityLog.id.desc())))


def for_piece(db: Session, piece_id: int, user: User) -> list[ActivityLog]:
    """Log of one piece, oldest first. Any campaign member."""
    piece_for_member(db, piece_id, user)
    return list(db.scalars(select(ActivityLog).where(ActivityLog.piece_id == piece_id)
                           .order_by(ActivityLog.id)))
