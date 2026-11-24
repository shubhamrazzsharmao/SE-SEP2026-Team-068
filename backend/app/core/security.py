"""Verification of Supabase Auth access tokens.

The frontend signs users in with supabase-js and sends the access token as
`Authorization: Bearer <token>`. We never see passwords.
"""
from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.core.config import get_settings
from app.core.errors import AppError

AUDIENCE = "authenticated"
ASYMMETRIC_ALGS = ["ES256", "RS256"]


def _unauthorized(msg: str) -> AppError:
    return AppError(401, "UNAUTHORIZED", msg)


@lru_cache
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(f"{url.rstrip('/')}/auth/v1/.well-known/jwks.json", cache_keys=True)


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        alg = jwt.get_unverified_header(token).get("alg")
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise _unauthorized("Token algorithm not accepted.")
            return jwt.decode(token, settings.supabase_jwt_secret,
                              algorithms=["HS256"], audience=AUDIENCE)
        if alg in ASYMMETRIC_ALGS:
            if not settings.supabase_url:
                raise _unauthorized("Token algorithm not accepted.")
            key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token).key
            return jwt.decode(token, key, algorithms=ASYMMETRIC_ALGS, audience=AUDIENCE)
        raise _unauthorized("Token algorithm not accepted.")  # includes alg=none
    except AppError:
        raise
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired.")
    except jwt.PyJWTError:
        raise _unauthorized("Invalid token.")
    except Exception:  # e.g. JWKS endpoint unreachable
        raise _unauthorized("Token could not be verified.")
