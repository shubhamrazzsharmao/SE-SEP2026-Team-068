"""Campaigns and their members (one role per user per campaign)."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import MemberRole
from app.models.base import Base, pgenum, timestamp
from app.models.brand import Brand
from app.models.user import User


class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = timestamp()
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    brand: Mapped[Brand] = relationship()


class CampaignMember(Base):
    __tablename__ = "campaign_members"
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    member_role: Mapped[MemberRole] = mapped_column(pgenum(MemberRole, "member_role"))
    added_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    joined_at: Mapped[datetime] = timestamp()
    user: Mapped[User] = relationship(foreign_keys=[user_id])

    @property
    def name(self):
        return self.user.name

    @property
    def email(self):
        return self.user.email
