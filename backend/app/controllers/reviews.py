"""Controller for human-in-the-loop review.

HTTP only: validated input comes in (app.schemas), review_service does the work, a view goes out.
"""
from fastapi import APIRouter, Depends

from app.ai.llm import LLMClient, get_llm_client
from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.schemas import ApproveIn, ContentPieceOut, RejectIn, RequestChangesIn
from app.services import review_service

router = APIRouter(prefix="/content/{piece_id}", tags=["Review (human in the loop)"])


@router.post("/approve", response_model=ContentPieceOut,
             responses=errs(401, 403, 404, 409, 422), openapi_extra={"x-user-stories": ["US7"]})
def approve(piece_id: int, db: DB, user: CurrentUser, body: ApproveIn = ApproveIn()):
    """Approve a piece that is `pending_review`. The reviewer and timestamp are recorded.
    Approval does **not** publish anything.

    Roles: `reviewer` only (any other role gets 403). A reviewer cannot approve content they
    created or edited (403 `SELF_REVIEW_FORBIDDEN`). If `version_no` is sent and is no longer the
    current version, the call fails with 409 `STALE_VERSION`.

    **User stories:** US7 (approve content).
    """
    return review_service.approve(db, piece_id, user, body.version_no)


@router.post("/reject", response_model=ContentPieceOut,
             responses=errs(401, 403, 404, 409, 422), openapi_extra={"x-user-stories": ["US8"]})
def reject(piece_id: int, body: RejectIn, db: DB, user: CurrentUser):
    """Reject a `pending_review` piece with a mandatory reason (at least 10 characters).

    Rejection is **final**: the piece stays in history and can no longer be approved, edited or
    regenerated. The creator reads the reason in `rejection_reason`.

    Roles: `reviewer` only. Same self-review and stale-version guards as approve.

    **User stories:** US8 (reject content with a reason).
    """
    return review_service.reject(db, piece_id, user, body.reason, body.version_no)


@router.post("/request-changes", response_model=ContentPieceOut,
             responses=errs(401, 403, 404, 409, 422, 502), openapi_extra={"x-user-stories": ["US9"]})
def request_changes(piece_id: int, body: RequestChangesIn, db: DB, user: CurrentUser,
                    llm: LLMClient = Depends(get_llm_client)):
    """Ask for changes with a short feedback note (at least 5 characters).

    Produces exactly **one** revised version of **this piece only** (origin `regeneration`) and
    returns the piece to `pending_review`. Earlier versions are kept. If the AI provider
    fails, nothing is saved and the call returns 502.

    Roles: `reviewer` only. Same self-review and stale-version guards as approve.

    **User stories:** US9 (request changes of a piece).
    """
    return review_service.request_changes(db, piece_id, user, body.feedback, body.version_no, llm)
