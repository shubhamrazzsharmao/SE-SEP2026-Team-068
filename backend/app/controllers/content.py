"""Controller for content pieces and comments.

HTTP only: validated input comes in (app.schemas), content_service does the work, a view goes out.
"""
from typing import Optional

from fastapi import APIRouter, Query

from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.enums import ContentStatus, Platform
from app.schemas import (
    ActivityOut,
    CommentIn,
    CommentOut,
    ContentPieceDetail,
    ContentPieceOut,
    EditIn,
    VersionOut,
)
from app.services import activity_service, content_service

router = APIRouter(tags=["Content"])


@router.get("/campaigns/{campaign_id}/content", response_model=list[ContentPieceOut],
            responses=errs(401, 404, 422), openapi_extra={"x-user-stories": ["US6", "US10"]})
def list_content(campaign_id: int, db: DB, user: CurrentUser,
                 status: Optional[ContentStatus] = Query(None, description="Filter by status."),
                 platform: Optional[Platform] = Query(None, description="Filter by platform.")):
    """List the content pieces of a campaign, newest first, with their current version.

    Use `?status=pending_review` for the reviewer's pending list and `?status=...` to
    track progress. Deleted pieces are never listed. Any campaign member can read.

    **User stories:** US6 (list pending content), US10 (track status and filter).
    """
    return content_service.list_for_campaign(db, campaign_id, user, status, platform)


@router.get("/content/{piece_id}", response_model=ContentPieceDetail, responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US6", "US8", "US10"]})
def get_content(piece_id: int, db: DB, user: CurrentUser):
    """One piece with its brief, every version and every review decision, so a reviewer sees
    the content next to its brief and a creator can read the rejection reason.

    **User stories:** US6, US8 (creator reads the reason), US10.
    """
    return content_service.get(db, piece_id, user)


@router.get("/content/{piece_id}/versions", response_model=list[VersionOut], responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US9", "US13"]})
def list_versions(piece_id: int, db: DB, user: CurrentUser):
    """Version history, oldest first. Versions are append-only and never deleted.

    **User stories:** US9, US13.
    """
    return content_service.list_versions(db, piece_id, user)


@router.patch("/content/{piece_id}", response_model=ContentPieceOut,
              responses=errs(401, 403, 404, 409, 422), openapi_extra={"x-user-stories": ["US6", "US13"]})
def edit_content(piece_id: int, body: EditIn, db: DB, user: CurrentUser):
    """Edit the text. Saves a **new** `human_edit` version (older versions are kept) and puts
    the piece back to `pending_review`, so an edited approved piece needs approval again.
    Rejected pieces are final (409).

    Roles: `owner`, `creator`, `reviewer`. A reviewer who edited a version cannot approve it.

    **User stories:** US6 (review and edit), US13 (edits are logged).
    """
    return content_service.edit(db, piece_id, user, body.body)


@router.delete("/content/{piece_id}", status_code=204, responses=errs(400, 401, 403, 404),
               openapi_extra={"x-user-stories": ["US11", "US13"]})
def delete_content(piece_id: int, db: DB, user: CurrentUser,
                   confirm: bool = Query(False, description="Must be true to confirm the deletion.")):
    """Delete a piece after a confirmation step: without `?confirm=true` the call is rejected
    (400 `CONFIRMATION_REQUIRED`). The piece is hidden, not erased - its versions, reviews and
    activity log stay in the database.

    Roles: `owner`, `creator`.

    **User stories:** US11, US13 (the deletion is logged).
    """
    content_service.delete(db, piece_id, user, confirm)


@router.get("/content/{piece_id}/comments", response_model=list[CommentOut], responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US6", "US8"]})
def list_comments(piece_id: int, db: DB, user: CurrentUser):
    """Discussion thread of a piece, oldest first (any member).

    **User stories:** US6, US8 (reviewer and creator can talk about a piece).
    """
    return content_service.list_comments(db, piece_id, user)


@router.post("/content/{piece_id}/comments", response_model=CommentOut, status_code=201,
             responses=errs(401, 404, 422), openapi_extra={"x-user-stories": ["US6", "US8"]})
def add_comment(piece_id: int, body: CommentIn, db: DB, user: CurrentUser):
    """Add a comment to a piece. Any campaign member can comment, whatever their role.

    **User stories:** US6, US8.
    """
    return content_service.add_comment(db, piece_id, user, body.body)


@router.get("/content/{piece_id}/activity", response_model=list[ActivityOut], responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US13"]})
def piece_activity(piece_id: int, db: DB, user: CurrentUser):
    """Read-only activity log of one piece (user, action, version, timestamp), oldest first.
    There is no endpoint that updates or deletes log entries.

    **User stories:** US13 (view an activity log).
    """
    return activity_service.for_piece(db, piece_id, user)
