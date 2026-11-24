"""Briefs, their source material, and AI generation jobs."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import BriefStatus, JobStatus, Platform, SourceKind
from app.models.base import Base, JsonType, pgenum, timestamp, utcnow
from app.models.campaign import Campaign


class Brief(Base):
    __tablename__ = "briefs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    topic: Mapped[str] = mapped_column(String(255))
    objective: Mapped[str] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_messages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # per-brief override
    platforms: Mapped[list] = mapped_column(JsonType)
    status: Mapped[BriefStatus] = mapped_column(pgenum(BriefStatus, "brief_status"), default=BriefStatus.draft)
    created_at: Mapped[datetime] = timestamp()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    campaign: Mapped[Campaign] = relationship()

    @property
    def effective_tone(self) -> str:
        return self.tone or self.campaign.brand.tone


class SourceMaterial(Base):
    __tablename__ = "source_materials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(ForeignKey("briefs.id"))
    kind: Mapped[SourceKind] = mapped_column(pgenum(SourceKind, "source_kind"))
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = timestamp()


class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(ForeignKey("briefs.id"))
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[Optional[Platform]] = mapped_column(pgenum(Platform, "platform_type"), nullable=True)
    status: Mapped[JobStatus] = mapped_column(pgenum(JobStatus, "job_status"), default=JobStatus.queued)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = timestamp()
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
