"""Comment requests and views."""
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.schemas.common import ORM


class CommentIn(BaseModel):
    body: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class CommentOut(ORM):
    id: int
    piece_id: int
    user_id: uuid.UUID
    author_name: str
    body: str
    created_at: datetime
