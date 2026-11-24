"""Status counts for the dashboard, and the database health check."""
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.enums import ContentStatus
from app.models import Campaign, CampaignMember, ContentPiece, User

Counts = dict[str, int]  # {"draft": 0, "pending_review": 3, "approved": 9, "rejected": 1}


def _empty() -> Counts:
    return {s.value: 0 for s in ContentStatus}


def counts_for_user(db: Session, user: User) -> tuple[Counts, list[tuple[int, str, Counts]]]:
    """Pieces per status over the user's campaigns: (totals, [(campaign_id, name, counts), ...])."""
    campaigns = db.execute(
        select(Campaign.id, Campaign.name)
        .join(CampaignMember, CampaignMember.campaign_id == Campaign.id)
        .where(CampaignMember.user_id == user.id, Campaign.deleted_at.is_(None))
        .order_by(Campaign.id)).all()
    rows = db.execute(
        select(ContentPiece.campaign_id, ContentPiece.status, func.count())
        .where(ContentPiece.campaign_id.in_([c.id for c in campaigns]), ContentPiece.deleted_at.is_(None))
        .group_by(ContentPiece.campaign_id, ContentPiece.status)).all()

    per = {c.id: _empty() for c in campaigns}
    totals = _empty()
    for cid, status, n in rows:
        per[cid][status.value] = n
        totals[status.value] += n
    return totals, [(c.id, c.name, per[c.id]) for c in campaigns]


def database_ok() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False
