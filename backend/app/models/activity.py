"""Insert-only audit trail."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonType, timestamp
from app.models.user import User


class ActivityLog(Base):
    """Insert-only audit trail."""
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    piece_id: Mapped[Optional[int]] = mapped_column(ForeignKey("content_pieces.id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50))
    version_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[Optional[dict]] = mapped_column(JsonType, nullable=True)
    created_at: Mapped[datetime] = timestamp()
    user: Mapped[User] = relationship()

    @property
    def user_name(self) -> str:
        return self.user.name
