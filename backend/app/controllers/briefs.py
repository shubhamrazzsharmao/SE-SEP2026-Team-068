"""Controller for briefs and generation.

HTTP only: validated input comes in (app.schemas), brief_service does the work, a view goes out.
"""
from fastapi import APIRouter, Depends

from app.ai.llm import LLMClient, get_llm_client
from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.schemas import BriefIn, BriefOut, BriefUpdate, GenerateOut
from app.services import brief_service

router = APIRouter(tags=["Briefs & generation"])


@router.post("/campaigns/{campaign_id}/briefs", response_model=BriefOut, status_code=201,
             responses=errs(401, 403, 404, 422), openapi_extra={"x-user-stories": ["US1", "US3"]})
def create_brief(campaign_id: int, body: BriefIn, db: DB, user: CurrentUser):
    """Create a brief: topic, objective and platforms are required; audience, key messages
    and a tone override are optional. Without an override the brand tone is used
    (`effective_tone`).

    Roles: `owner`, `creator`.

    **User stories:** US1 (submit a campaign brief), US3.
    """
    return brief_service.create(db, campaign_id, user, body)


@router.get("/campaigns/{campaign_id}/briefs", response_model=list[BriefOut], responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US1", "US11"]})
def list_briefs(campaign_id: int, db: DB, user: CurrentUser):
    """List the briefs of a campaign (any member).

    **User stories:** US1, US11.
    """
    return brief_service.list_for_campaign(db, campaign_id, user)


@router.get("/briefs/{brief_id}", response_model=BriefOut, responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US1", "US6"]})
def get_brief(brief_id: int, db: DB, user: CurrentUser):
    """Get one brief (any member of its campaign).

    **User stories:** US1, US6 (reviewers read the brief next to the content).
    """
    return brief_service.get(db, brief_id, user)


@router.patch("/briefs/{brief_id}", response_model=BriefOut,
              responses=errs(401, 403, 404, 409, 422), openapi_extra={"x-user-stories": ["US1"]})
def update_brief(brief_id: int, body: BriefUpdate, db: DB, user: CurrentUser):
    """Edit a saved brief. Only possible while the brief is still `draft`; once generation
    has started it is locked (409 `BRIEF_LOCKED`).

    Roles: `owner`, `creator`.

    **User stories:** US1.
    """
    return brief_service.update(db, brief_id, user, body)


@router.post("/briefs/{brief_id}/generate", response_model=GenerateOut, status_code=201,
             responses=errs(401, 403, 404, 409, 502), openapi_extra={"x-user-stories": ["US3", "US6"]})
def generate(brief_id: int, db: DB, user: CurrentUser, llm: LLMClient = Depends(get_llm_client)):
    """Generate one content piece per platform in the brief, using the brief and the brand
    guidelines (tone, preferred and avoided terms).

    Every piece is saved as version 1 (`ai_generated`) with status `pending_review`. Nothing
    is ever published or approved automatically. Generation is all-or-nothing: if the AI
    provider fails for any platform, **no** piece is saved, the job is recorded as `failed`,
    the brief returns to `draft`, and the call returns 502 so the user can retry.

    Roles: `owner`, `creator`. A brief can be generated once (409 afterwards).

    **User stories:** US3 (generate platform-specific content from one brief), US6.
    """
    job, pieces = brief_service.generate(db, brief_id, user, llm)
    return GenerateOut(job=job, pieces=pieces)
