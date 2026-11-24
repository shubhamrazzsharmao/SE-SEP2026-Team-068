"""Brands: a client and its voice (tone, preferred and avoided terms)."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JsonType, timestamp, utcnow


class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = (UniqueConstraint("owner_id", "name"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    tone: Mapped[str] = mapped_column(Text)
    preferred_terms: Mapped[list] = mapped_column(JsonType, default=list)
    avoided_terms: Mapped[list] = mapped_column(JsonType, default=list)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = timestamp()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
