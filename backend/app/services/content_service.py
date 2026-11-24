"""Content pieces: listing, reading, editing, deleting, and their comment threads."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.enums import ContentStatus, Platform, VersionOrigin
from app.models import ContentPiece, ContentVersion, PieceComment, User
from app.services import activity_service
from app.services.access import CAN_DELETE_CONTENT, CAN_EDIT_CONTENT, campaign_for_member, piece_for_member

_EAGER = (selectinload(ContentPiece.versions).selectinload(ContentVersion.reviews),)


# ---------------------------------------------------------------- version helpers
def current_version(piece: ContentPiece) -> ContentVersion:
    v = piece.current_version
    if v is None:  # cannot happen for pieces created by generation
        raise AppError(409, "INVALID_STATE", "Content piece has no version.")
    return v


def add_version(db: Session, piece: ContentPiece, **fields) -> ContentVersion:
    """Append a version (versions are never updated), make it current, send the piece to review."""
    next_no = (db.scalar(select(func.max(ContentVersion.version_no))
                         .where(ContentVersion.piece_id == piece.id)) or 0) + 1
    v = ContentVersion(piece_id=piece.id, version_no=next_no, **fields)
    db.add(v)
    db.flush()
    piece.current_version_id = v.id
    piece.status = ContentStatus.pending_review
    return v


def load(db: Session, piece_id: int) -> ContentPiece:
    """Fresh copy with versions, reviews and brief (populate_existing drops stale relationship lists)."""
    return db.scalar(select(ContentPiece).where(ContentPiece.id == piece_id).options(
        *_EAGER, selectinload(ContentPiece.brief)).execution_options(populate_existing=True))


# ---------------------------------------------------------------- pieces
def list_for_campaign(db: Session, campaign_id: int, user: User, status: Optional[ContentStatus] = None,
                      platform: Optional[Platform] = None) -> list[ContentPiece]:
    """Newest first; deleted pieces are never listed. Any campaign member."""
    campaign_for_member(db, campaign_id, user)
    q = select(ContentPiece).where(ContentPiece.campaign_id == campaign_id,
                                   ContentPiece.deleted_at.is_(None)).options(*_EAGER)
    if status is not None:
        q = q.where(ContentPiece.status == status)
    if platform is not None:
        q = q.where(ContentPiece.platform == platform)
    return list(db.scalars(q.order_by(ContentPiece.id.desc())))


def get(db: Session, piece_id: int, user: User) -> ContentPiece:
    piece_for_member(db, piece_id, user)
    return load(db, piece_id)


def list_versions(db: Session, piece_id: int, user: User) -> list[ContentVersion]:
    piece_for_member(db, piece_id, user)
    return list(db.scalars(select(ContentVersion).where(ContentVersion.piece_id == piece_id)
                           .order_by(ContentVersion.version_no)))


def edit(db: Session, piece_id: int, user: User, body: str) -> ContentPiece:
    """Save the text as a new human_edit version; the piece goes back to pending_review."""
    piece, _ = piece_for_member(db, piece_id, user, CAN_EDIT_CONTENT)
    if piece.status == ContentStatus.rejected:
        raise AppError(409, "INVALID_STATE", "Rejected content is final and cannot be edited.")
    prev = current_version(piece)
    new = add_version(db, piece, body=body, creative_suggestion=prev.creative_suggestion,
                      origin=VersionOrigin.human_edit, created_by=user.id)
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=user.id, action="edited",
                            piece_id=piece.id, version_no=new.version_no)
    db.commit()
    return load(db, piece_id)


def delete(db: Session, piece_id: int, user: User, confirm: bool) -> None:
    """Soft delete, only with explicit confirmation. Versions, reviews and logs stay."""
    piece, _ = piece_for_member(db, piece_id, user, CAN_DELETE_CONTENT)
    if not confirm:
        raise AppError(400, "CONFIRMATION_REQUIRED",
                       "Deleting content needs confirmation: repeat the request with ?confirm=true.")
    piece.deleted_at = datetime.now(timezone.utc)
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=user.id, action="deleted",
                            piece_id=piece.id,
                            version_no=piece.current_version.version_no if piece.current_version else None)
    db.commit()


# ---------------------------------------------------------------- comments
def list_comments(db: Session, piece_id: int, user: User) -> list[PieceComment]:
    piece_for_member(db, piece_id, user)
    return list(db.scalars(select(PieceComment).where(PieceComment.piece_id == piece_id)
                           .order_by(PieceComment.id)))


def add_comment(db: Session, piece_id: int, user: User, body: str) -> PieceComment:
    piece, _ = piece_for_member(db, piece_id, user)
    comment = PieceComment(piece_id=piece_id, user_id=user.id, body=body)
    db.add(comment)
    activity_service.record(db, campaign_id=piece.campaign_id, user_id=user.id, action="commented",
                            piece_id=piece_id)
    db.commit()
    return comment
