"""Brief requests and views."""
import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

from app.enums import BriefStatus, Platform
from app.schemas.common import ORM, Text


def _dedupe_platforms(v):
    if v is None:
        return v
    return list(dict.fromkeys(v))


Topic = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class BriefIn(BaseModel):
    topic: Topic
    objective: Text
    platforms: list[Platform] = Field(min_length=1, description="At least one platform.")
    target_audience: Optional[Text] = None
    key_messages: Optional[Text] = None
    tone: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = Field(
        default=None, description="Optional override of the brand tone for this brief only.")
    _platforms = field_validator("platforms")(_dedupe_platforms)


class BriefUpdate(BaseModel):
    topic: Optional[Topic] = None
    objective: Optional[Text] = None
    platforms: Optional[list[Platform]] = Field(default=None, min_length=1)
    target_audience: Optional[Text] = None
    key_messages: Optional[Text] = None
    tone: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = None
    _platforms = field_validator("platforms")(_dedupe_platforms)

    @model_validator(mode="after")
    def _not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        for required in ("topic", "objective", "platforms"):
            if required in self.model_fields_set and getattr(self, required) is None:
                raise ValueError(f"{required} cannot be null.")
        return self


class BriefOut(ORM):
    id: int
    campaign_id: int
    created_by: uuid.UUID
    topic: str
    objective: str
    target_audience: Optional[str]
    key_messages: Optional[str]
    tone: Optional[str]
    effective_tone: str
    platforms: list[Platform]
    status: BriefStatus
    created_at: datetime
    updated_at: datetime
