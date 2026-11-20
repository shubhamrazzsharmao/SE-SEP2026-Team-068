"""Campaigns and their members."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError, not_found
from app.enums import MemberRole
from app.models import Brand, Campaign, CampaignMember, User
from app.schemas import CampaignIn, MemberIn
from app.services import activity_service
from app.services.access import CAN_MANAGE_MEMBERS, campaign_for_member


def create(db: Session, user: User, data: CampaignIn) -> Campaign:
    """Create a campaign under one of the user's own brands; the user becomes its owner."""
    brand = db.scalar(select(Brand).where(Brand.id == data.brand_id, Brand.owner_id == user.id))
    if brand is None:
        raise not_found("Brand")
    campaign = Campaign(brand_id=brand.id, owner_id=user.id, name=data.name, description=data.description)
    db.add(campaign)
    db.flush()
    db.add(CampaignMember(campaign_id=campaign.id, user_id=user.id,
                          member_role=MemberRole.owner, added_by=user.id))
    activity_service.record(db, campaign_id=campaign.id, user_id=user.id, action="campaign_created",
                            detail={"name": campaign.name})
    db.commit()
    return campaign


def list_for_user(db: Session, user: User) -> list[tuple[Campaign, MemberRole]]:
    """The user's campaigns, newest first, with the user's role in each."""
    rows = db.execute(
        select(Campaign, CampaignMember.member_role)
        .join(CampaignMember, CampaignMember.campaign_id == Campaign.id)
        .where(CampaignMember.user_id == user.id, Campaign.deleted_at.is_(None))
        .order_by(Campaign.created_at.desc())).all()
    return [(c, r) for c, r in rows]


def get_for_member(db: Session, campaign_id: int, user: User) -> tuple[Campaign, MemberRole]:
    campaign, member = campaign_for_member(db, campaign_id, user)
    return campaign, member.member_role


def add_member(db: Session, campaign_id: int, user: User, data: MemberIn) -> CampaignMember:
    campaign_for_member(db, campaign_id, user, CAN_MANAGE_MEMBERS)
    target = db.scalar(select(User).where(User.email == data.email))
    if target is None:
        raise AppError(404, "USER_NOT_FOUND",
                       "No user with that email. Ask them to sign in to the app once first.")
    if db.get(CampaignMember, (campaign_id, target.id)):
        raise AppError(409, "ALREADY_MEMBER", "That user is already a member of this campaign.")
    member = CampaignMember(campaign_id=campaign_id, user_id=target.id,
                            member_role=data.member_role, added_by=user.id)
    db.add(member)
    activity_service.record(db, campaign_id=campaign_id, user_id=user.id, action="member_added",
                            detail={"member": target.email, "role": data.member_role.value})
    db.commit()
    return member


def list_members(db: Session, campaign_id: int, user: User) -> list[CampaignMember]:
    campaign_for_member(db, campaign_id, user)
    return list(db.scalars(select(CampaignMember).where(CampaignMember.campaign_id == campaign_id)
                           .order_by(CampaignMember.joined_at)))


def remove_member(db: Session, campaign_id: int, user: User, member_user_id: str) -> None:
    """Owner only. A campaign always keeps at least one owner."""
    campaign_for_member(db, campaign_id, user, CAN_MANAGE_MEMBERS)
    try:
        uid = uuid.UUID(member_user_id)
    except ValueError:
        raise not_found("Member")
    target = db.get(CampaignMember, (campaign_id, uid))
    if target is None:
        raise not_found("Member")
    if target.member_role == MemberRole.owner and db.scalar(
            select(func.count()).select_from(CampaignMember).where(
                CampaignMember.campaign_id == campaign_id,
                CampaignMember.member_role == MemberRole.owner)) <= 1:
        raise AppError(409, "LAST_OWNER", "A campaign must keep at least one owner.")
    email = target.user.email
    db.delete(target)
    activity_service.record(db, campaign_id=campaign_id, user_id=user.id, action="member_removed",
                            detail={"member": email})
    db.commit()
