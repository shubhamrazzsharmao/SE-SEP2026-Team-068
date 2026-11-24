"""Controller for the signed-in user's account.

HTTP only. The user is resolved (and their profile created on first sign-in) in deps.py.
"""
from fastapi import APIRouter

from app.controllers.deps import CurrentUser
from app.core.errors import errs
from app.schemas import UserOut

router = APIRouter(prefix="/me", tags=["Account"])


@router.get("", response_model=UserOut, responses=errs(401, 403),
            openapi_extra={"x-user-stories": ["US11"]})
def get_me(user: CurrentUser):
    """Return the signed-in user's profile.

    Users sign up and log in through Supabase Auth in the frontend. The first authenticated
    call creates the matching profile row (name and email are taken from the token), so
    the frontend should call this once after login. A user must have done so before a
    campaign owner can add them by email.

    **User stories:** US11 (access is organised per user).
    """
    return user
