# Schema notes: changes from the Milestone 2 ER design

The source of truth for the database is `supabase/schema.sql`. It was applied to a real
PostgreSQL 18 and compared column-by-column with the SQLAlchemy models (no differences).

## What changed, and why

| Change | Reason |
|---|---|
| `users.id` is a **uuid equal to `auth.users.id`**; `password_hash` removed | Supabase Auth owns sign-up/login/passwords. All user foreign keys are uuid as a result. Other tables keep integer ids as in the ER. |
| `source_kind`: `docx` removed | Team decision: PDF + TXT only (plus pasted text). |
| New table `piece_comments` | Comment thread per content piece (reviewer <-> creator/client communication). |
| `content_pieces.deleted_at` added | "Delete only after confirmation" is implemented as a soft delete; versions, reviews and logs stay. |
| `brands.preferred_terms/avoided_terms` are `NOT NULL DEFAULT '[]'` | Avoids null checks in the generator. |
| `timestamp` -> `timestamptz` | Correct handling of time zones. |
| `briefs.platforms` has a CHECK (JSON array, at least one) | Enforces "at least one platform" in the database as well. |
| Row Level Security enabled on all tables, no policies | The backend connects as the database owner (bypasses RLS) and does all authorisation; Supabase's public REST API (anon key) can read nothing. |

## Gap in the ER design (needs a team decision for Sprint 2)

`design-of-component` describes a **post plan** (generated -> reviewed -> approved/locked ->
a change creates a new plan version needing its own approval), but the ER has no table for it.
Not built in Sprint 1. A minimal fit would be `post_plans(id, brief_id, version_no, core_message,
angle, key_points jsonb, status, approved_by, approved_at, created_at)` with `unique(brief_id, version_no)`.

## Authorisation decisions to confirm

* **Approve / reject / request changes: `reviewer` role only.** The campaign owner can not
  approve (matches "a non-Reviewer who tries to approve gets a 403"). To let owners review too,
  change `CAN_REVIEW` in `app/services/access.py`; the self-review guard still applies.
* **Self-review guard:** nobody can approve/reject a piece they created, or a version they wrote
  (a reviewer who edits a piece cannot approve their own edit).
* **Non-members get 404** (campaigns are invisible to outsiders); members with the wrong role get 403.
* **Rejected is final:** no approve, edit or regenerate afterwards. History stays.
* **Editing an approved piece** creates a new version and sends it back to `pending_review`.
