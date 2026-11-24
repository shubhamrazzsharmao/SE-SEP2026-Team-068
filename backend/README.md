# ContentFlow backend (Team 068, Sprint 1)

FastAPI + SQLAlchemy on Supabase (Postgres + Auth). AI generation with a human-in-the-loop review workflow.

```
app/            MVC + service layer (requests flow top to bottom)
  controllers/  C: FastAPI routers, one per resource. HTTP only: input -> service -> view
  schemas/      V: Pydantic request/response models (what the API accepts and returns)
  services/     business rules, permissions (access.py) and database queries
  models/       M: SQLAlchemy ORM models, one module per domain area
  core/         config, database session, JWT verification, errors, logging
  ai/llm.py     LLM interface: FakeLLMClient (default, no key) and GeminiClient
  enums.py      shared enums (statuses, roles, platforms)
  main.py       app factory: middleware, error handlers, router registration
supabase/schema.sql   run once in the Supabase SQL editor
tests/          pytest suite (134 tests, 162 recorded cases) + report recorder
docs/           openapi.yaml, test_report.md, test_cases.csv, schema-notes.md, first_run/
scripts/export_openapi.py
```

Rules that keep the layers clean: controllers never import SQLAlchemy or models (only `deps.py`
does, to provide the session and current user); services and models never import FastAPI;
a controller function is one service call plus building the response view.

## 1. Set up Supabase (one time, ~10 minutes)

1. Create a project at supabase.com.
2. **SQL Editor -> New query**, paste all of `supabase/schema.sql`, **Run**.
3. **Connect** (top bar) -> copy the **Session pooler** connection string into `.env` as `DATABASE_URL`.
   Change the scheme to `postgresql+psycopg://` and URL-encode special characters in the password.
4. Token verification: put your project URL in `SUPABASE_URL` (JWT signing keys, the current default), **or**
   the legacy JWT secret in `SUPABASE_JWT_SECRET`. See `.env.example`.
5. Keep `LLM_PROVIDER=fake` for the demo (no key needed).

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then edit it
uvicorn app.main:app --reload --port 8000
```

Check: `http://localhost:8000/api/v1/health` returns `{"status":"ok","database":true}`.
Interactive docs: `http://localhost:8000/docs` (use **Authorize** and paste an access token).

## 2. Calling it from the frontend

Users sign up / log in with `supabase-js`; the backend never sees passwords.

```ts
const { data: { session } } = await supabase.auth.getSession();
const res = await fetch("http://localhost:8000/api/v1/campaigns", {
  headers: { Authorization: `Bearer ${session!.access_token}` },
});
```

Call `GET /api/v1/me` once after login: it creates the user's profile row (needed before an
owner can add them to a campaign by email). Every error is `{"detail": "...", "code": "..."}`.

## 3. Roles (per campaign)

| Action | owner | creator | reviewer | brand_manager | non-member |
|---|:-:|:-:|:-:|:-:|:-:|
| See campaign, briefs, content, comments | yes | yes | yes | yes | 404 |
| Create/edit brief, generate content | yes | yes | 403 | 403 | 404 |
| Edit content text (new version) | yes | yes | yes | 403 | 404 |
| Approve / reject / request changes | 403 | 403 | **yes** | 403 | 404 |
| Delete content (needs `?confirm=true`) | yes | yes | 403 | 403 | 404 |
| Add/remove members, read campaign activity log | yes | 403 | 403 | 403 | 404 |
| Edit brand guidelines | brand owner or brand_manager | | | | |
| Comment on content | yes | yes | yes | yes | 404 |

A reviewer can never approve/reject a piece they created or a version they edited.

## 4. Status flow

```
generate -> pending_review --approve--------------> approved  --edit--> pending_review
                           --reject (reason>=10)--> rejected  (final)
                           --request changes------> pending_review + 1 new version (regeneration)
```

Versions are append-only. Nothing is published or approved automatically. If the AI call fails,
no piece is saved (502, job recorded as failed, brief back to `draft`).

## 5. Tests and the assignment deliverables

```bash
pytest                        # 134 tests; writes docs/test_report.md and docs/test_cases.csv
python scripts/export_openapi.py   # regenerates docs/openapi.yaml
```

| Deliverable | File |
|---|---|
| Swagger-compatible YAML (errors, user-story mapping, descriptions) | `docs/openapi.yaml` |
| Backend code | `app/` |
| Test cases with input / expected / actual output | `docs/test_report.md`, `docs/test_cases.csv` |
| pytest code | `tests/` |
| Case where actual differed from expected (testing improved the API) | `docs/first_run/` |

Tests run on SQLite by default. They can also run against a **local** Postgres
(`DATABASE_URL=postgresql+psycopg://...localhost...`); the suite refuses any non-local host because it
wipes all tables.

## 6. Client review (recommended for Sprint 2)

Sprint 1 has a **comment thread per content piece** (`/content/{id}/comments`) for reviewers,
creators and brand managers. For external clients without an account, add a **share link**: a
`share_links(token, piece_id/campaign_id, expires_at)` table, a public read-only
`GET /public/review/{token}` plus `POST .../comments` and approve/request-changes limited to that
token. The client's decision is stored as a normal `reviews` row with `reviewer_id` = the agency
user who issued the link, so the audit trail stays intact.

## 7. Not in Sprint 1

Source material upload (paste/PDF/TXT) and key-message extraction, post plan approve/lock/versioning,
variations (US4), ideas (US12), a campaign delete, pagination, background jobs (generation runs inside
the request, fine for 1-4 pieces). The Gemini client is implemented but has not been run against the live API.
