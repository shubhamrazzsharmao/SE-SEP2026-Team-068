"""Campaign and membership requests and views."""
import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.enums import MemberRole
from app.schemas.common import EMAIL_RE, ORM, Name150


class CampaignIn(BaseModel):
    brand_id: int
    name: Name150
    description: Optional[Annotated[str, StringConstraints(max_length=2000)]] = None


class CampaignOut(BaseModel):
    id: int
    brand_id: int
    brand_name: str
    name: str
    description: Optional[str]
    created_at: datetime
    my_role: MemberRole

    @classmethod
    def build(cls, campaign, role: MemberRole) -> "CampaignOut":
        """View of a Campaign model for a user with the given role."""
        return cls(id=campaign.id, brand_id=campaign.brand_id, brand_name=campaign.brand.name,
                   name=campaign.name, description=campaign.description,
                   created_at=campaign.created_at, my_role=role)


class MemberIn(BaseModel):
    email: str = Field(description="Email of a user who has signed in at least once.")
    member_role: MemberRole

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_RE.match(v) or len(v) > 255:
            raise ValueError("Not a valid email address.")
        return v


class MemberOut(ORM):
    user_id: uuid.UUID
    name: str
    email: str
    member_role: MemberRole
    joined_at: datetime
