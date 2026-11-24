"""Brand (client) requests and views."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import ORM, Name150, Text, clean_terms


class BrandIn(BaseModel):
    name: Name150
    tone: Text = Field(description="Brand voice, e.g. 'warm, practical, no jargon'.")
    preferred_terms: list[str] = Field(default_factory=list, description="Terms to use.")
    avoided_terms: list[str] = Field(default_factory=list, description="Terms never to use.")
    _terms = field_validator("preferred_terms", "avoided_terms")(clean_terms)


class BrandUpdate(BaseModel):
    name: Optional[Name150] = None
    tone: Optional[Text] = None
    preferred_terms: Optional[list[str]] = None
    avoided_terms: Optional[list[str]] = None
    _terms = field_validator("preferred_terms", "avoided_terms")(clean_terms)

    @model_validator(mode="after")
    def _not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null.")
        if "tone" in self.model_fields_set and self.tone is None:
            raise ValueError("tone cannot be null.")
        return self


class BrandOut(ORM):
    id: int
    owner_id: uuid.UUID
    name: str
    tone: str
    preferred_terms: list[str]
    avoided_terms: list[str]
    updated_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
