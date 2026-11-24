import time

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.controllers import ROUTERS
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.errors import install_handlers
from app.core.logger import log, who
from app.core.logger import setup as setup_logging

DESCRIPTION = """
Backend for **ContentFlow** (Team 068): AI-assisted multi-channel content generation with a
human-in-the-loop review workflow.

**Authentication.** Users sign in with Supabase Auth in the frontend; every call (except
`/health`) sends `Authorization: Bearer <access_token>`.

**Authorisation.** Roles are per campaign: `owner`, `creator`, `reviewer`, `brand_manager`.
Non-members get `404` (campaigns are invisible to outsiders); members whose role does not allow
an action get `403`.

**Errors.** Every error has the shape `{"detail": "...", "code": "..."}`; validation errors add
an `errors` list; a failed AI call adds `job_id`.

**Status flow.** `pending_review` -> `approved` | `rejected` (final) | `pending_review` with a new
version after *request changes*. Versions are append-only. Nothing is published automatically.
"""

API_PREFIX = "/api/v1"
_VALIDATION_DESC = "Request body, query or path parameters failed validation."


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    app = FastAPI(title="ContentFlow API", version="1.0.0-sprint1", description=DESCRIPTION,
                  openapi_tags=[
                      {"name": "Account"}, {"name": "Brands"}, {"name": "Campaigns & members"},
                      {"name": "Briefs & generation"}, {"name": "Content"},
                      {"name": "Review (human in the loop)"}, {"name": "Dashboard"}])
    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    install_handlers(app)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """One line per API call: who, what, result, duration."""
        start = time.perf_counter()
        response = await call_next(request)
        ms = (time.perf_counter() - start) * 1000
        user = getattr(request.state, "user", None)
        path = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        level = "debug" if request.url.path.endswith("/health") or request.method == "OPTIONS" else "info"
        if response.status_code >= 500:
            level = "error"
        elif response.status_code >= 400:
            level = "warning"
        getattr(log, level)("%s %s -> %s (%.0f ms) by %s", request.method, path, response.status_code, ms, who(user))
        return response

    api = APIRouter(prefix=API_PREFIX)
    for router in ROUTERS:
        api.include_router(router)
    app.include_router(api)

    if settings.auto_create_tables:
        Base.metadata.create_all(engine)

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        spec = get_openapi(title=app.title, version=app.version, description=app.description,
                           routes=app.routes, tags=app.openapi_tags)
        # FastAPI auto-documents 422 with its own schema; our handler returns ErrorResponse.
        for ops in spec["paths"].values():
            for op in ops.values():
                r422 = op.get("responses", {}).get("422")
                if r422 and "HTTPValidationError" in str(r422):
                    op["responses"]["422"] = {
                        "description": _VALIDATION_DESC,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
        for name in ("HTTPValidationError", "ValidationError"):
            spec["components"]["schemas"].pop(name, None)
        app.openapi_schema = spec
        return spec

    app.openapi = custom_openapi
    return app


app = create_app()
