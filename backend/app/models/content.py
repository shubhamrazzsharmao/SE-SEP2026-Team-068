"""Content pieces and their append-only versions."""
import uuid
from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import ContentStatus, Platform, ReviewDecision, VersionOrigin
from app.models.base import Base, JsonType, pgenum, timestamp, utcnow
from app.models.brief import Brief

if TYPE_CHECKING:  # avoids a circular import; SQLAlchemy resolves "Review" by name
    from app.models.review import Review


class ContentPiece(Base):
    __tablename__ = "content_pieces"
    __table_args__ = (UniqueConstraint("brief_id", "platform"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brief_id: Mapped[int] = mapped_column(ForeignKey("briefs.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    platform: Mapped[Platform] = mapped_column(pgenum(Platform, "platform_type"))
    status: Mapped[ContentStatus] = mapped_column(pgenum(ContentStatus, "content_status"),
                                                   default=ContentStatus.pending_review)
    # Circular FK to content_versions: declared in supabase/schema.sql only.
    current_version_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = timestamp()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    brief: Mapped[Brief] = relationship()
    versions: Mapped[list["ContentVersion"]] = relationship(
        back_populates="piece", order_by="ContentVersion.version_no")

    @property
    def current_version(self):
        for v in self.versions:
            if v.id == self.current_version_id:
                return v
        return None

    @property
    def reviews(self):
        return sorted((r for v in self.versions for r in v.reviews), key=lambda r: r.id)

    @property
    def rejection_reason(self) -> Optional[str]:
        for r in reversed(self.reviews):
            if r.decision == ReviewDecision.rejected:
                return r.reason
        return None


class ContentVersion(Base):
    """Append-only: rows are inserted, never updated."""
    __tablename__ = "content_versions"
    __table_args__ = (UniqueConstraint("piece_id", "version_no"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    piece_id: Mapped[int] = mapped_column(ForeignKey("content_pieces.id"))
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("generation_jobs.id"), nullable=True)
    version_no: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)
    creative_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin: Mapped[VersionOrigin] = mapped_column(pgenum(VersionOrigin, "version_origin"))
    prompt_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    flags: Mapped[Optional[dict]] = mapped_column(JsonType, nullable=True)
    attempt_no: Mapped[int] = mapped_column(Integer, default=1)
    check_outcome: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = timestamp()

    piece: Mapped[ContentPiece] = relationship(back_populates="versions")
    reviews: Mapped[list["Review"]] = relationship(back_populates="version")
    checks: Mapped[list["VersionCheck"]] = relationship(back_populates="version",
                                                         order_by="VersionCheck.created_at")


class VersionCheck(Base):
    """One code or LLM quality check executed for a content version."""
    __tablename__ = "version_checks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("content_versions.id"))
    check_name: Mapped[str] = mapped_column(String)
    check_type: Mapped[str] = mapped_column(String)
    passed: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric, nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = timestamp()

    version: Mapped[ContentVersion] = relationship(back_populates="checks")
