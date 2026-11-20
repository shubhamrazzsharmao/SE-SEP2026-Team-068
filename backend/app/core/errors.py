"""One error shape for the whole API: {"detail": str, "code": str, ...}."""
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import log


class ErrorResponse(BaseModel):
    detail: str
    code: str
    errors: Optional[list[dict]] = None  # field-level problems on 422
    job_id: Optional[int] = None         # set on 502 so the client can show/retry the failed job


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, **extra):
        self.status_code, self.code, self.message, self.extra = status_code, code, message, extra


def not_found(what: str) -> AppError:
    return AppError(404, "NOT_FOUND", f"{what} not found.")


_DESCRIPTIONS = {
    400: "Bad request (e.g. a required confirmation is missing).",
    401: "Missing, malformed, expired or forged bearer token.",
    403: "Authenticated, but the campaign role does not allow this action.",
    404: "Resource does not exist, or the caller is not a member of its campaign.",
    409: "Conflict with the current state (duplicate, locked brief, invalid status transition, stale version).",
    422: "Request body or parameters failed validation.",
    502: "The AI provider failed. Nothing was saved; the request can be retried.",
}


def errs(*codes: int) -> dict:
    """`responses=` helper so every route documents its error cases in the OpenAPI file."""
    return {c: {"model": ErrorResponse, "description": _DESCRIPTIONS[c]} for c in codes}


def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        body = {"detail": exc.message, "code": exc.code, **exc.extra}
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        def _field(loc):  # drop only the leading location marker ("body", "query", "path")
            parts = list(loc[1:] if loc and loc[0] in ("body", "query", "path", "header") else loc)
            return ".".join(str(x) for x in parts)

        errors = [{"field": _field(e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content={
            "detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": errors})

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(status_code=exc.status_code,
                            content={"detail": str(exc.detail), "code": code})

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        log.exception("Unhandled error")
        return JSONResponse(status_code=500, content={
            "detail": "Internal server error.", "code": "INTERNAL_ERROR"})
