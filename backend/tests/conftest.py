"""Test harness.

* Real FastAPI app + real routers + real JWT verification (HS256 test secret).
* SQLite file DB by default; optionally a LOCAL Postgres (see _guard_database).
* `api.check(...)` asserts AND records input / expected / actual for every case; at the end
  of the run the records are written to docs/test_report.md and docs/test_cases.csv.
"""
import csv
import json
import os
import re
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import jwt
import pytest

from tests.helpers import BRIEF, MISSING, PRESENT, TEST_SECRET, Contains  # noqa: E402

# ---- environment must be set before the app is imported --------------------------------
_TMP = tempfile.mkdtemp(prefix="contentflow-tests-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP}/test.db")
os.environ["SUPABASE_JWT_SECRET"] = TEST_SECRET
os.environ["SUPABASE_URL"] = ""
os.environ["LLM_PROVIDER"] = "fake"
os.environ["AUTO_CREATE_TABLES"] = "false"


def _guard_database(url: str) -> bool:
    """Tests wipe all tables. Only SQLite or a *local* Postgres is allowed - never Supabase."""
    if url.startswith("sqlite"):
        return False
    parsed = urlparse(url.replace("+psycopg", ""))
    host = parsed.hostname or ""
    local = host in ("", "localhost", "127.0.0.1", "::1") or host.startswith("/") or "host=/" in url
    if not local:
        raise RuntimeError(f"Refusing to run tests against non-local database host {host!r}: "
                           "the test suite deletes all data.")
    return True


USING_PG = _guard_database(os.environ["DATABASE_URL"])

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.ai.llm import LLMError, get_llm_client  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = Path(os.environ.get("TEST_REPORT_DIR", ROOT / "docs"))
CASES: list[dict] = []


# ------------------------------------------------------------------ helpers
@dataclass
class TUser:
    key: str
    name: str
    email: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def label(self) -> str:
        return f"{self.name} ({self.key})"


def _dig(obj, path):
    for part in path.split("."):
        try:
            obj = obj[int(part)] if isinstance(obj, list) else obj[part]
        except (KeyError, IndexError, TypeError, ValueError):
            return MISSING
    return obj


def _matches(actual, expected) -> bool:
    if expected is PRESENT:
        return actual is not MISSING and actual is not None
    if isinstance(expected, Contains):
        return isinstance(actual, str) and str(expected) in actual
    return actual == expected


def _show(v) -> str:
    if v is PRESENT:
        return "<present>"
    if isinstance(v, Contains):
        return f"contains '{v}'"
    return json.dumps(v, default=str)


def _compact(body, limit=420) -> str:
    s = json.dumps(body, default=str, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit] + " ...(truncated)"


class Api:
    def __init__(self, client: TestClient, users: dict, request):
        self.c, self.users, self.request = client, users, request
        self.prefix = "/api/v1"

    # ---- calling
    def token(self, user: TUser, **claims) -> str:
        payload = {"sub": str(user.id), "email": user.email, "aud": "authenticated",
                   "role": "authenticated", "user_metadata": {"full_name": user.name},
                   "exp": int(time.time()) + 3600}
        payload.update(claims)
        return jwt.encode({k: v for k, v in payload.items() if v is not None}, TEST_SECRET, algorithm="HS256")

    def call(self, method, path, user=None, json=None, params=None, token=None):
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        elif user is not None:
            headers["Authorization"] = f"Bearer {self.token(user)}"
        resp = self.c.request(method, self.prefix + path if path.startswith("/") else path,
                              json=json, params=params, headers=headers)
        resp.call_info = {"method": method, "path": self.prefix + path, "json": json, "params": params,
                          "user": user.label() if user else ("custom token" if token else "no token")}
        return resp

    def get(self, path, user=None, **kw): return self.call("GET", path, user, **kw)
    def post(self, path, user=None, **kw): return self.call("POST", path, user, **kw)
    def patch(self, path, user=None, **kw): return self.call("PATCH", path, user, **kw)
    def delete(self, path, user=None, **kw): return self.call("DELETE", path, user, **kw)

    def _template(self, method, path) -> str:
        """Turn /api/v1/content/7/approve into /api/v1/content/{piece_id}/approve (from the OpenAPI paths)."""
        for template, ops in app.openapi()["paths"].items():
            if method.lower() in ops and re.fullmatch(re.sub(r"\{[^/]+\}", "[^/]+", template), path):
                return template
        return path

    # ---- asserting + recording
    def check(self, resp, status: int, /, whole=MISSING, **fields):
        info = resp.call_info
        try:
            actual_body = resp.json() if resp.content else None
        except ValueError:
            actual_body = resp.text
        expected_bits = [f"HTTP {status}"]
        problems = []
        if resp.status_code != status:
            problems.append(f"status {resp.status_code} != {status}")
        if whole is not MISSING:
            expected_bits.append(f"response body == {_show(whole)}")
            if actual_body != whole:
                problems.append("response body differs")
        for path, exp in fields.items():
            key = path.replace("__", ".")
            expected_bits.append(f"{key} = {_show(exp)}")
            got = _dig(actual_body, key) if actual_body is not None else MISSING
            if not _matches(got, exp):
                problems.append(f"{key}: got {_show(None if got is MISSING else got)}")
        marker = self.request.node.get_closest_marker("us")
        CASES.append({
            "test": self.request.node.name,
            "title": (self.request.node.function.__doc__ or self.request.node.name).strip().splitlines()[0],
            "stories": ", ".join(marker.args) if marker else "",
            "api": f"{info['method']} {self._template(info['method'], info['path'])}",
            "input": self._input_text(info),
            "expected": "; ".join(expected_bits),
            "actual": f"HTTP {resp.status_code}" + (f" {_compact(actual_body)}" if actual_body is not None else ""),
            "result": "FAIL" if problems else "PASS",
        })
        assert not problems, f"{info['method']} {info['path']}: " + "; ".join(problems) + f" | response: {_compact(actual_body)}"
        return actual_body

    def verify(self, title: str, actual, expected, api="database check"):
        ok = actual == expected
        CASES.append({
            "test": self.request.node.name, "title": title, "stories": "", "api": api,
            "input": "-", "expected": _show(expected), "actual": _show(actual),
            "result": "PASS" if ok else "FAIL"})
        assert ok, f"{title}: expected {expected!r}, got {actual!r}"

    @staticmethod
    def _input_text(info) -> str:
        bits = [f"as {info['user']}", f"path {info['path']}"]
        if info["params"]:
            bits.append(f"query {json.dumps(info['params'])}")
        if info["json"] is not None:
            bits.append(f"body {json.dumps(info['json'], ensure_ascii=False)}")
        return "; ".join(bits)


# ------------------------------------------------------------------ fixtures
def _reset_db():
    if USING_PG:
        with engine.begin() as conn:
            tables = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
            conn.execute(text(f"truncate {tables} restart identity cascade"))
            conn.execute(text("truncate auth.users cascade"))
    else:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def _fresh_db():
    _reset_db()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def users():
    spec = [("alice", "Alice Owner"), ("bob", "Bob Creator"), ("carol", "Carol Reviewer"),
            ("dave", "Dave BrandManager"), ("eve", "Eve Outsider"), ("frank", "Frank Reviewer")]
    made = {k: TUser(k, n, f"{k}@example.com") for k, n in spec}
    if USING_PG:  # stand-in for Supabase's auth.users rows
        with engine.begin() as conn:
            for u in made.values():
                conn.execute(text("insert into auth.users (id) values (:i)"), {"i": u.id})
    return SimpleNamespace(**made)


@pytest.fixture
def api(request, users):
    with TestClient(app, raise_server_exceptions=False) as client:
        yield Api(client, users, request)


@pytest.fixture
def db():
    s = SessionLocal()
    yield s
    s.close()


class FailingLLM:
    def generate(self, ctx):
        raise LLMError("simulated provider outage")

    def revise(self, ctx, previous_body, feedback):
        raise LLMError("simulated provider outage")


@pytest.fixture
def failing_llm():
    """Use as a context-free switch: call `failing_llm.on()` / `.off()`."""
    class Switch:
        def on(self): app.dependency_overrides[get_llm_client] = lambda: FailingLLM()
        def off(self): app.dependency_overrides.pop(get_llm_client, None)
    return Switch()


@pytest.fixture
def world(api, users):
    """alice owns a brand+campaign; bob=creator, carol/frank=reviewer, dave=brand_manager; eve is an outsider."""
    for u in vars(users).values():
        api.get("/me", u)  # first call creates each profile
    brand = api.post("/brands", users.alice, json={
        "name": "GreenLeaf Organics", "tone": "warm, practical, no jargon",
        "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"]}).json()
    campaign = api.post("/campaigns", users.alice, json={
        "brand_id": brand["id"], "name": "Spring Launch", "description": "Spring product launch"}).json()
    for u, role in ((users.bob, "creator"), (users.carol, "reviewer"),
                    (users.frank, "reviewer"), (users.dave, "brand_manager")):
        r = api.post(f"/campaigns/{campaign['id']}/members", users.alice,
                     json={"email": u.email, "member_role": role})
        assert r.status_code == 201, r.text
    return SimpleNamespace(brand_id=brand["id"], campaign_id=campaign["id"])


@pytest.fixture
def brief(api, users, world):
    """A saved (draft) brief created by bob."""
    r = api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json=BRIEF)
    assert r.status_code == 201, r.text
    return SimpleNamespace(id=r.json()["id"], campaign_id=world.campaign_id)


@pytest.fixture
def generated(api, users, world, brief):
    """The brief after generation: four pieces in pending_review, keyed by platform."""
    r = api.post(f"/briefs/{brief.id}/generate", users.bob)
    assert r.status_code == 201, r.text
    pieces = {p["platform"]: p["id"] for p in r.json()["pieces"]}
    return SimpleNamespace(brief_id=brief.id, campaign_id=world.campaign_id, pieces=pieces,
                           blog=pieces["blog"], linkedin=pieces["linkedin"],
                           facebook=pieces["facebook"], instagram=pieces["instagram"])


# ------------------------------------------------------------------ report
def pytest_sessionfinish(session, exitstatus):
    if not CASES:
        return
    cfg = session.config
    partial = bool(cfg.getoption("keyword") or cfg.getoption("markexpr")
                   or any(a.endswith(".py") or "::" in a for a in map(str, cfg.args)))
    if partial and not os.environ.get("TEST_REPORT"):
        return  # a subset run must not overwrite the full report (set TEST_REPORT=1 to force)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_DIR / "test_cases.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Case ID", "User story", "API under test", "Test case", "Input", "Expected output",
                    "Actual output", "Result"])
        for i, c in enumerate(CASES, 1):
            w.writerow([f"TC-{i:03d}", c["stories"], c["api"], c["title"], c["input"], c["expected"],
                        c["actual"], c["result"]])
    passed = sum(c["result"] == "PASS" for c in CASES)
    failed = len(CASES) - passed
    md = ["# ContentFlow API - test report", "",
          f"Cases recorded: **{len(CASES)}**  |  Passed: **{passed}**  |  Failed: **{failed}**", "",
          "Each case lists the request that was sent, what we expected and what the API actually returned.", ""]
    if failed:
        md += ["## Cases where actual output differed from expected", ""]
        for i, c in enumerate(CASES, 1):
            if c["result"] == "FAIL":
                md += [f"- **TC-{i:03d}** {c['api']} - {c['title']}"]
        md += [""]
    md += ["## All cases", ""]
    for i, c in enumerate(CASES, 1):
        md += [f"### TC-{i:03d} - {c['title']}  `{c['result']}`",
               f"- **API:** `{c['api']}`" + (f"  |  **User story:** {c['stories']}" if c["stories"] else ""),
               f"- **Input:** {c['input']}",
               f"- **Expected:** {c['expected']}",
               f"- **Actual:** {c['actual']}", ""]
    (REPORT_DIR / "test_report.md").write_text("\n".join(md), encoding="utf-8")
