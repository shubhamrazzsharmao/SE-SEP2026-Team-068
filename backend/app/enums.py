from enum import Enum


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class MemberRole(str, Enum):
    owner = "owner"
    creator = "creator"
    reviewer = "reviewer"
    brand_manager = "brand_manager"


class BriefStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    generated = "generated"


class SourceKind(str, Enum):
    pasted_text = "pasted_text"
    pdf = "pdf"
    txt = "txt"


class Platform(str, Enum):
    blog = "blog"
    linkedin = "linkedin"
    facebook = "facebook"
    instagram = "instagram"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class ContentStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class VersionOrigin(str, Enum):
    ai_generated = "ai_generated"
    human_edit = "human_edit"
    variation = "variation"
    regeneration = "regeneration"


class ReviewDecision(str, Enum):
    approved = "approved"
    rejected = "rejected"
    changes_requested = "changes_requested"
