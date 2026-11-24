"""Human-in-the-loop review: approve, reject, request changes. The state machine:

    pending_review --approve-----------> approved   (can go back to pending_review via edit)
    pending_review --reject------------> rejected   (final; history kept)
    pending_review --request_changes---> pending_review (one new 'regeneration' version)
    approved / pending_review --edit---> pending_review (one new 'human_edit' version)

Guards: only reviewers decide; nobody reviews a piece they created or a version they
wrote; decisions apply to the version that was actually reviewed.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.llm import LLMClient, LLMError
from app.core.errors import AppError
from app.enums import ContentStatus, JobStatus, ReviewDecision, VersionOrigin
from app.models import ContentPiece, ContentVersion, GenerationJob, Review, User, utcnow
from app.services import activity_service
from app.services.access import CAN_REVIEW, piece_for_member
from app.services.content_service import add_version, current_version, load
from app.services.generation_service import build_context


def _guard_reviewable(piece: ContentPiece, reviewer: User, version_no: Optional[int]) -> ContentVersion:
    if piece.status != ContentStatus.pending_review:
        msg = ("Rejected content is final." if piece.status == ContentStatus.rejected
               else f"Only pieces in pending_review can be reviewed (current status: {piece.status.value}).")
        raise AppError(409, "INVALID_STATE", msg)
    version = current_version(piece)
    if piece.created_by == reviewer.id or version.created_by == reviewer.id:
        raise AppError(403, "SELF_REVIEW_FORBIDDEN",
                       "You cannot review content you created or edited.")
    if version_no is not None and version_no != version.version_no:
        raise AppError(409, "STALE_VERSION",
                       f"You reviewed version {version_no}, but the current version is {version.version_no}.")
    return version


def _approve(db: Session, piece: ContentPiece, reviewer: User, version_no: Optional[int]) -> ContentPiece:
    version = _guard_reviewable(piece, reviewer, version_no)
    db.add(Review(version_id=version.id, reviewer_id=reviewer.id, decision=ReviewDecision.approved))
    piece.status = ContentStatus.approved
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=reviewer.id, action="approved",
                            piece_id=piece.id, version_no=version.version_no)
    db.commit()
    return piece


def _reject(db: Session, piece: ContentPiece, reviewer: User, reason: str,
           version_no: Optional[int]) -> ContentPiece:
    version = _guard_reviewable(piece, reviewer, version_no)
    db.add(Review(version_id=version.id, reviewer_id=reviewer.id,
                  decision=ReviewDecision.rejected, reason=reason))
    piece.status = ContentStatus.rejected
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=reviewer.id, action="rejected",
                            piece_id=piece.id, version_no=version.version_no, detail={"reason": reason})
    db.commit()
    return piece


def _request_changes(db: Session, piece: ContentPiece, reviewer: User, feedback: str,
                    version_no: Optional[int], llm: LLMClient) -> ContentPiece:
    version = _guard_reviewable(piece, reviewer, version_no)
    ctx = build_context(piece.brief, piece.platform)
    try:  # call the provider first: on failure nothing at all is saved
        out = llm.revise(ctx, version.body, feedback)
    except LLMError as exc:
        raise AppError(502, "GENERATION_FAILED",
                       f"The AI provider failed; no changes were saved. ({exc})")

    job = GenerationJob(brief_id=piece.brief_id, requested_by=reviewer.id, platform=piece.platform,
                        status=JobStatus.done, feedback_note=feedback, finished_at=utcnow())
    db.add(job)
    db.flush()
    db.add(Review(version_id=version.id, reviewer_id=reviewer.id,
                  decision=ReviewDecision.changes_requested, feedback=feedback))
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=reviewer.id, action="changes_requested",
                            piece_id=piece.id, version_no=version.version_no, detail={"feedback": feedback})
    new = add_version(db, piece, job_id=job.id, body=out.body,
                      creative_suggestion=out.creative_suggestion,
                      origin=VersionOrigin.regeneration, prompt_used=out.prompt,
                      model_name=out.model, created_by=None)
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=reviewer.id, action="regenerated",
                            piece_id=piece.id, version_no=new.version_no, detail={"job_id": job.id})
    db.commit()
    return piece


# ---------------------------------------------------------------- entry points (reviewer role only)
def approve(db: Session, piece_id: int, user: User, version_no: Optional[int]) -> ContentPiece:
    piece, _ = piece_for_member(db, piece_id, user, CAN_REVIEW)
    _approve(db, piece, user, version_no)
    return load(db, piece_id)


def reject(db: Session, piece_id: int, user: User, reason: str, version_no: Optional[int]) -> ContentPiece:
    piece, _ = piece_for_member(db, piece_id, user, CAN_REVIEW)
    _reject(db, piece, user, reason, version_no)
    return load(db, piece_id)


def request_changes(db: Session, piece_id: int, user: User, feedback: str, version_no: Optional[int],
                    llm: LLMClient) -> ContentPiece:
    piece, _ = piece_for_member(db, piece_id, user, CAN_REVIEW)
    _request_changes(db, piece, user, feedback, version_no, llm)
    return load(db, piece_id)
