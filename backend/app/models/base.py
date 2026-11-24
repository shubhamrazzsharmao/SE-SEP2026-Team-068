"""Shared helpers for the ORM models.

The models mirror supabase/schema.sql (the source of truth in production); tests build the
same tables on SQLite from these classes.
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from app.core.database import Base

__all__ = ["Base", "JsonType", "utcnow", "pgenum", "timestamp"]

JsonType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def pgenum(enum_cls, name: str):
    # The Postgres types are created by supabase/schema.sql, never by SQLAlchemy.
    return SAEnum(enum_cls, name=name, create_type=False,
                  values_callable=lambda e: [m.value for m in e])


def timestamp():
    """`created_at`-style column filled with the current UTC time."""
    return mapped_column(DateTime(timezone=True), default=utcnow)
