"""Users (profile rows keyed by the Supabase auth user id)."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import UserRole
from app.models.base import Base, pgenum, timestamp


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)  # = auth.users.id
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[UserRole] = mapped_column(pgenum(UserRole, "user_role"), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = timestamp()
