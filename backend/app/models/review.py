"""Review decisions and the comment thread on a piece."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import ReviewDecision
from app.models.base import Base, pgenum, timestamp
from app.models.content import ContentVersion
from app.models.user import User


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("content_versions.id"))
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[ReviewDecision] = mapped_column(pgenum(ReviewDecision, "review_decision"))
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = timestamp()

    version: Mapped[ContentVersion] = relationship(back_populates="reviews")

    @property
    def version_no(self) -> int:
        return self.version.version_no


class PieceComment(Base):
    __tablename__ = "piece_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    piece_id: Mapped[int] = mapped_column(ForeignKey("content_pieces.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = timestamp()
    user: Mapped[User] = relationship()

    @property
    def author_name(self) -> str:
        return self.user.name
