"""Brief -> content pieces. All-or-nothing: if any platform fails, no piece is saved."""
from sqlalchemy.orm import Session

from app.ai.llm import Context, LLMClient, LLMError
from app.core.errors import AppError
from app.enums import BriefStatus, ContentStatus, JobStatus, Platform, VersionOrigin
from app.models import Brief, ContentPiece, ContentVersion, GenerationJob, User, utcnow
from app.services import activity_service


def build_context(brief: Brief, platform) -> Context:
    brand = brief.campaign.brand
    return Context(
        platform=platform, topic=brief.topic, objective=brief.objective,
        audience=brief.target_audience, key_messages=brief.key_messages,
        tone=brief.effective_tone,
        preferred_terms=list(brand.preferred_terms or []),
        avoided_terms=list(brand.avoided_terms or []),
    )


def generate_for_brief(db: Session, brief: Brief, user: User, llm: LLMClient):
    if brief.status != BriefStatus.draft:
        raise AppError(409, "BRIEF_ALREADY_GENERATED",
                       f"Content was already generated for this brief (status: {brief.status.value}).")

    job = GenerationJob(brief_id=brief.id, requested_by=user.id, status=JobStatus.running)
    db.add(job)
    brief.status = BriefStatus.generating
    activity_service.record(db, campaign_id=brief.campaign_id, user_id=user.id, action="generation_requested",
                            detail={"brief_id": brief.id, "platforms": [p.value if hasattr(p, "value") else p
                                                                          for p in brief.platforms]})
    db.commit()  # persist the attempt even if the provider fails

    results = []
    try:
        for platform in brief.platforms:
            p = Platform(platform)
            results.append((p, llm.generate(build_context(brief, p))))
    except LLMError as exc:
        job.status = JobStatus.failed
        job.error_message = str(exc)
        job.finished_at = utcnow()
        brief.status = BriefStatus.draft  # editable and retryable again
        activity_service.record(db, campaign_id=brief.campaign_id, user_id=user.id, action="generation_failed",
                                detail={"job_id": job.id, "error": str(exc)})
        db.commit()
        raise AppError(502, "GENERATION_FAILED",
                       "The AI provider failed; nothing was saved. You can retry.", job_id=job.id)

    pieces = []
    for p, out in results:
        piece = ContentPiece(brief_id=brief.id, campaign_id=brief.campaign_id, platform=p,
                             status=ContentStatus.pending_review, created_by=user.id)
        db.add(piece)
        db.flush()
        version = ContentVersion(piece_id=piece.id, job_id=job.id, version_no=1, body=out.body,
                                 creative_suggestion=out.creative_suggestion,
                                 origin=VersionOrigin.ai_generated, prompt_used=out.prompt,
                                 model_name=out.model, created_by=None)
        db.add(version)
        db.flush()
        piece.current_version_id = version.id
        activity_service.record(db, campaign_id=brief.campaign_id, user_id=user.id, action="generated",
                                piece_id=piece.id, version_no=1, detail={"platform": p.value, "job_id": job.id})
        pieces.append(piece)

    job.status = JobStatus.done
    job.finished_at = utcnow()
    brief.status = BriefStatus.generated
    db.commit()
    return job, pieces
