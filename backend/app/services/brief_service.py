"""Briefs: what a campaign wants to say, and on which platforms."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.llm import LLMClient
from app.core.errors import AppError
from app.enums import BriefStatus
from app.models import Brief, ContentPiece, GenerationJob, User
from app.schemas import BriefIn, BriefUpdate
from app.services import activity_service, generation_service
from app.services.access import CAN_WRITE_BRIEFS, brief_for_member, campaign_for_member


def create(db: Session, campaign_id: int, user: User, data: BriefIn) -> Brief:
    campaign, _ = campaign_for_member(db, campaign_id, user, CAN_WRITE_BRIEFS)
    brief = Brief(campaign_id=campaign.id, created_by=user.id, topic=data.topic,
                  objective=data.objective, target_audience=data.target_audience,
                  key_messages=data.key_messages, tone=data.tone,
                  platforms=[p.value for p in data.platforms])
    db.add(brief)
    db.flush()
    activity_service.record(db, campaign_id=campaign.id, user_id=user.id, action="brief_created",
                            detail={"brief_id": brief.id, "topic": brief.topic})
    db.commit()
    return brief


def list_for_campaign(db: Session, campaign_id: int, user: User) -> list[Brief]:
    campaign_for_member(db, campaign_id, user)
    return list(db.scalars(select(Brief).where(Brief.campaign_id == campaign_id)
                           .order_by(Brief.created_at.desc(), Brief.id.desc())))


def get(db: Session, brief_id: int, user: User) -> Brief:
    brief, _, _ = brief_for_member(db, brief_id, user)
    return brief


def update(db: Session, brief_id: int, user: User, data: BriefUpdate) -> Brief:
    """Only while the brief is still a draft; generation locks it."""
    brief, campaign, _ = brief_for_member(db, brief_id, user, CAN_WRITE_BRIEFS)
    if brief.status != BriefStatus.draft:
        raise AppError(409, "BRIEF_LOCKED", "The brief can no longer be edited because generation has started.")
    changes = data.model_dump(exclude_unset=True)
    if "platforms" in changes:
        changes["platforms"] = [p.value for p in changes["platforms"]]
    for k, v in changes.items():
        setattr(brief, k, v)
    activity_service.record(db, campaign_id=campaign.id, user_id=user.id, action="brief_updated",
                            detail={"brief_id": brief.id, "fields": sorted(changes)})
    db.commit()
    return brief


def generate(db: Session, brief_id: int, user: User, llm: LLMClient) -> tuple[GenerationJob, list[ContentPiece]]:
    brief, _, _ = brief_for_member(db, brief_id, user, CAN_WRITE_BRIEFS)
    return generation_service.generate_for_brief(db, brief, user, llm)
