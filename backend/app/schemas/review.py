"""Human-in-the-loop review requests and the review view."""
import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints

from app.enums import ReviewDecision
from app.schemas.common import ORM


class ReviewOut(ORM):
    id: int
    version_no: int
    reviewer_id: uuid.UUID
    decision: ReviewDecision
    reason: Optional[str]
    feedback: Optional[str]
    created_at: datetime


class ApproveIn(BaseModel):
    version_no: Optional[int] = Field(
        default=None, ge=1, description="If given, must equal the current version (guards against reviewing a stale draft).")


class RejectIn(BaseModel):
    reason: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=2000)]
    version_no: Optional[int] = Field(default=None, ge=1)


class RequestChangesIn(BaseModel):
    feedback: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=2000)]
    version_no: Optional[int] = Field(default=None, ge=1)
