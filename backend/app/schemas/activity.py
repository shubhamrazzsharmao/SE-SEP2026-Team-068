"""Activity (audit log) view."""
import uuid
from datetime import datetime
from typing import Any, Optional

from app.schemas.common import ORM


class ActivityOut(ORM):
    id: int
    campaign_id: int
    piece_id: Optional[int]
    user_id: uuid.UUID
    user_name: str
    action: str
    version_no: Optional[int]
    detail: Optional[dict[str, Any]]
    created_at: datetime
