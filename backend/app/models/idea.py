"""Personal ideas (API arrives in Sprint 2)."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, timestamp


class Idea(Base):
    __tablename__ = "ideas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    converted_brief_id: Mapped[Optional[int]] = mapped_column(ForeignKey("briefs.id"), nullable=True)
    created_at: Mapped[datetime] = timestamp()
