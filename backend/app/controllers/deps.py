"""Request dependencies shared by all controllers: the database session and the signed-in user."""
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.logger import log
from app.core.security import decode_token
from app.models import User
from app.services import user_service

bearer = HTTPBearer(auto_error=False, scheme_name="BearerAuth",
                    description="Supabase Auth access token (JWT) from supabase-js `session.access_token`.")

DB = Annotated[Session, Depends(get_db)]


def get_current_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: DB,
) -> User:
    if creds is None:
        raise AppError(401, "UNAUTHORIZED", "Missing bearer token.")
    try:
        claims = decode_token(creds.credentials)
    except AppError as e:
        log.warning("Rejected token on %s %s: %s", request.method, request.url.path, e.message)
        raise
    user = user_service.get_or_create_from_claims(db, claims)
    request.state.user = user  # read by the request logger in main.py
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
