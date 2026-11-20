import time

import jwt
import pytest

from app.models import User
from tests.helpers import TEST_SECRET, PRESENT


def test_request_without_token_is_rejected(api):
    """Request without a bearer token is rejected"""
    r = api.get("/me")
    api.check(r, 401, code="UNAUTHORIZED", detail="Missing bearer token.")


def test_malformed_token_is_rejected(api):
    """Malformed token is rejected"""
    r = api.get("/me", token="not.a.jwt")
    api.check(r, 401, code="UNAUTHORIZED", detail="Invalid token.")


def test_expired_token_is_rejected(api, users):
    """Expired token is rejected"""
    r = api.get("/me", token=api.token(users.alice, exp=int(time.time()) - 60))
    api.check(r, 401, code="UNAUTHORIZED", detail="Token has expired.")


def test_token_signed_with_wrong_secret_is_rejected(api, users):
    """Token signed with a different secret (forged) is rejected"""
    forged = jwt.encode({"sub": str(users.alice.id), "email": "alice@example.com", "aud": "authenticated",
                         "exp": int(time.time()) + 3600}, "attacker-secret-0123456789abcdef0123", algorithm="HS256")
    api.check(api.get("/me", token=forged), 401, code="UNAUTHORIZED", detail="Invalid token.")


def test_token_with_wrong_audience_is_rejected(api, users):
    """Token for a different audience is rejected"""
    api.check(api.get("/me", token=api.token(users.alice, aud="anon")), 401, code="UNAUTHORIZED")


def test_unsigned_alg_none_token_is_rejected(api, users):
    """Unsigned token (alg=none) is rejected"""
    unsigned = jwt.encode({"sub": str(users.alice.id), "email": "alice@example.com", "aud": "authenticated",
                           "exp": int(time.time()) + 3600}, None, algorithm="none")
    api.check(api.get("/me", token=unsigned), 401, code="UNAUTHORIZED", detail="Token algorithm not accepted.")


@pytest.mark.us("US11")
def test_first_call_creates_profile_from_token(api, users):
    """First authenticated call creates the profile from the token claims"""
    api.check(api.get("/me", users.alice), 200, name="Alice Owner", email="alice@example.com",
              role="user", id=str(users.alice.id))


def test_profile_name_falls_back_to_email(api, users):
    """Name falls back to the email prefix when the token has no name"""
    r = api.get("/me", token=api.token(users.bob, user_metadata=None))
    api.check(r, 200, name="bob", email="bob@example.com")


def test_new_user_token_without_email_is_rejected(api, users):
    """Token of an unknown user without an email claim is rejected"""
    r = api.get("/me", token=api.token(users.eve, email=None))
    api.check(r, 401, code="UNAUTHORIZED", detail="Token has no email claim.")


def test_disabled_account_is_forbidden(api, users, db):
    """Disabled account gets 403"""
    api.get("/me", users.alice)
    db.get(User, users.alice.id).is_active = False
    db.commit()
    api.check(api.get("/me", users.alice), 403, code="FORBIDDEN")


def test_health_needs_no_token(api):
    """Health check works without a token and reports the database"""
    api.check(api.get("/health"), 200, status="ok", database=True)


def test_unknown_route_returns_json_404(api, users):
    """Unknown URL returns the standard error body"""
    api.check(api.get("/nope", users.alice), 404, code="NOT_FOUND", detail=PRESENT)


def test_wrong_method_returns_405(api, users):
    """Wrong HTTP method returns 405 in the standard error body"""
    api.check(api.call("PUT", "/me", users.alice), 405, code="METHOD_NOT_ALLOWED")


# ---------------------------------------------------------------- asymmetric tokens (Supabase JWT signing keys)
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

from app.core.config import get_settings
from app.core.security import _jwks_client


@pytest.fixture
def jwks_key(monkeypatch):
    """Serve a JWKS document locally and point SUPABASE_URL at it; yields the matching private key."""
    key = ec.generate_private_key(ec.SECP256R1())
    jwk = json.loads(ECAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid="test-key", alg="ES256", use="sig")
    payload = json.dumps({"keys": [jwk]}).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            ok = self.path == "/auth/v1/.well-known/jwks.json"
            self.send_response(200 if ok else 404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload if ok else b"{}")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(get_settings(), "supabase_url", f"http://127.0.0.1:{server.server_port}")
    _jwks_client.cache_clear()
    yield key
    server.shutdown()
    _jwks_client.cache_clear()


def _es256_token(key, user, **claims):
    payload = {"sub": str(user.id), "email": user.email, "aud": "authenticated",
               "user_metadata": {"full_name": user.name}, "exp": int(time.time()) + 3600, **claims}
    return jwt.encode(payload, key, algorithm="ES256", headers={"kid": "test-key"})


def test_asymmetric_token_is_verified_through_jwks(api, users, jwks_key):
    """ES256 token signed with the project's signing key is accepted (JWKS verification)"""
    api.check(api.get("/me", token=_es256_token(jwks_key, users.alice)), 200, email="alice@example.com")


def test_asymmetric_token_from_other_key_is_rejected(api, users, jwks_key):
    """ES256 token signed with a different key (same key id) is rejected"""
    attacker = ec.generate_private_key(ec.SECP256R1())
    api.check(api.get("/me", token=_es256_token(attacker, users.alice)), 401, code="UNAUTHORIZED")
