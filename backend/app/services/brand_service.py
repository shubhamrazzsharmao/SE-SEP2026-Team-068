"""Brands (clients): who can see them, who can edit them."""
from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError, not_found
from app.enums import MemberRole
from app.models import Brand, Campaign, CampaignMember, User
from app.schemas import BrandIn, BrandUpdate


def _member_brand_ids(user: User):
    return (select(Campaign.brand_id)
            .join(CampaignMember, CampaignMember.campaign_id == Campaign.id)
            .where(CampaignMember.user_id == user.id, Campaign.deleted_at.is_(None)))


def _can_edit(db: Session, brand: Brand, user: User) -> bool:
    if brand.owner_id == user.id:
        return True
    return bool(db.scalar(select(exists().where(
        Campaign.brand_id == brand.id, Campaign.deleted_at.is_(None),
        CampaignMember.campaign_id == Campaign.id, CampaignMember.user_id == user.id,
        CampaignMember.member_role == MemberRole.brand_manager))))


def create(db: Session, user: User, data: BrandIn) -> Brand:
    if db.scalar(select(Brand.id).where(Brand.owner_id == user.id, Brand.name == data.name)):
        raise AppError(409, "DUPLICATE", "You already have a brand with this name.")
    brand = Brand(owner_id=user.id, name=data.name, tone=data.tone,
                  preferred_terms=data.preferred_terms, avoided_terms=data.avoided_terms,
                  updated_by=user.id)
    db.add(brand)
    db.commit()
    return brand


def list_visible(db: Session, user: User) -> list[Brand]:
    """Brands the user owns or can see through a campaign membership."""
    return list(db.scalars(select(Brand).where(
        or_(Brand.owner_id == user.id, Brand.id.in_(_member_brand_ids(user)))
    ).order_by(Brand.name)))


def get_visible(db: Session, brand_id: int, user: User) -> Brand:
    """404 unless the user owns the brand or belongs to a campaign that uses it."""
    brand = db.scalar(select(Brand).where(
        Brand.id == brand_id,
        or_(Brand.owner_id == user.id, Brand.id.in_(_member_brand_ids(user)))))
    if brand is None:
        raise not_found("Brand")
    return brand


def update(db: Session, brand_id: int, user: User, data: BrandUpdate) -> Brand:
    brand = get_visible(db, brand_id, user)
    if not _can_edit(db, brand, user):
        raise AppError(403, "FORBIDDEN", "Only the brand owner or a brand manager can edit a brand.")
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes and changes["name"] != brand.name and db.scalar(
            select(Brand.id).where(Brand.owner_id == brand.owner_id, Brand.name == changes["name"])):
        raise AppError(409, "DUPLICATE", "A brand with this name already exists.")
    for k, v in changes.items():
        setattr(brand, k, v)
    brand.updated_by = user.id
    db.commit()
    return brand
