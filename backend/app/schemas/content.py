"""Content piece, version and generation views; the edit request."""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.enums import ContentStatus, JobStatus, Platform, VersionOrigin
from app.schemas.brief import BriefOut
from app.schemas.common import ORM, Text
from app.schemas.review import ReviewOut


class VersionOut(ORM):
    id: int
    version_no: int
    body: str
    creative_suggestion: Optional[str]
    origin: VersionOrigin
    model_name: Optional[str]
    flags: Optional[dict[str, Any]]
    created_by: Optional[uuid.UUID]
    created_at: datetime




class ContentPieceOut(ORM):
    id: int
    brief_id: int
    campaign_id: int
    platform: Platform
    status: ContentStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    current_version: Optional[VersionOut]
    rejection_reason: Optional[str] = Field(description="Reviewer's reason if the piece was rejected.")


class ContentPieceDetail(ContentPieceOut):
    brief: BriefOut
    versions: list[VersionOut]
    reviews: list[ReviewOut]


class JobOut(ORM):
    id: int
    brief_id: int
    platform: Optional[Platform]
    status: JobStatus
    error_message: Optional[str]
    feedback_note: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]


class GenerateOut(BaseModel):
    job: JobOut
    pieces: list[ContentPieceOut]


class EditIn(BaseModel):
    body: Text = Field(description="Full replacement text; saved as a new version.")
