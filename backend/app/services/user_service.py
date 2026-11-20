"""User profiles. Supabase Auth owns accounts; we keep a profile row per user."""
import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.logger import log, who
from app.models import User


def get_or_create_from_claims(db: Session, claims: dict) -> User:
    """Return the profile for a verified token, creating it on the user's first request."""
    try:
        uid = uuid.UUID(str(claims.get("sub")))
    except ValueError:
        raise AppError(401, "UNAUTHORIZED", "Token has no valid subject.")

    user = db.get(User, uid)
    if user is None:
        email = (claims.get("email") or "").strip().lower()
        if not email:
            raise AppError(401, "UNAUTHORIZED", "Token has no email claim.")
        meta = claims.get("user_metadata") or {}
        name = (meta.get("full_name") or meta.get("name") or email.split("@")[0])[:100]
        user = User(id=uid, name=name, email=email)
        db.add(user)
        db.commit()
        log.info("First sign-in: created profile for %s", who(user))
    if not user.is_active:
        log.warning("Disabled account tried to use the API: %s", who(user))
        raise AppError(403, "FORBIDDEN", "This account is disabled.")
    return user
