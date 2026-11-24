"""User profile view."""
import uuid

from app.enums import UserRole
from app.schemas.common import ORM


class UserOut(ORM):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
