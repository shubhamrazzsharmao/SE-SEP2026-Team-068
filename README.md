# ContentFlow (Team 068)

AI-assisted content generation for agencies, with a human review step before anything is approved.

| Part | Stack | Folder | Runs on |
|---|---|---|---|
| Frontend | Next.js 16, React 19, Tailwind, Supabase Auth | [`frontend/`](frontend/) | http://localhost:3000 |
| Backend | FastAPI, SQLAlchemy, Python | [`backend/`](backend/) | http://localhost:8000 |
| Database + login | Supabase (Postgres + Auth) | [`backend/supabase/schema.sql`](backend/supabase/schema.sql) | supabase.com |

```
Browser ──login──▶ Supabase Auth
   │
   ▼
Next.js (frontend) ──Bearer token──▶ FastAPI (backend) ──▶ Supabase Postgres
```

Users sign up and log in with Supabase from the frontend. The frontend sends the user's access token
to the backend on every call; the backend verifies it and does all reads, writes and permission checks.

---

## 1. Prerequisites

- **Python 3.10 or newer** (`python3 --version`)
- **Node.js 20.9 or newer** (`node --version`)
- A free **Supabase** account: https://supabase.com

---

## 2. Set up the database (Supabase, one time)

Only one person on the team needs to do this; everyone else just needs the keys from step 2.4.

### 2.1 Create the project
1. Go to https://supabase.com/dashboard and click **New project**.
2. Choose a name, a **database password** (save it, you need it below) and a region close to you.

### 2.2 Create the tables
1. Open **SQL Editor -> New query**.
2. Paste the whole content of [`backend/supabase/schema.sql`](backend/supabase/schema.sql) and click **Run**.
3. Check **Table Editor**: you should see 13 tables (`users`, `brands`, `campaigns`, `briefs`, `content_pieces`, ...).

Run the script **once**. Running it again fails with `type "user_role" already exists`, which means the tables are already there.

### 2.3 Configure sign-in
1. **Authentication -> URL Configuration**
   - **Site URL:** `http://localhost:3000`
   - **Redirect URLs:** add `http://localhost:3000/auth/callback`
2. **Authentication -> Sign In / Providers**
   - Keep **Email** enabled.
   - Optional for local development: turn off **Confirm email**, so new users can log in right away.
     (Supabase's built-in email service only sends a few emails per hour.)
   - Google / LinkedIn buttons only work after you enable those providers here (needs your own OAuth client ID and secret). Not required.

### 2.4 Collect the values you need

| Value | Where in the Supabase dashboard | Used by |
|---|---|---|
| Database connection string | **Connect** (top bar) -> **Session pooler** | backend `DATABASE_URL` |
| Project URL (`https://<ref>.supabase.co`) | **Project Settings -> API** | backend `SUPABASE_URL`, frontend `NEXT_PUBLIC_SUPABASE_URL` |
| Publishable key (`sb_publishable_...`) or legacy anon key | **Project Settings -> API Keys** | frontend `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` |

Never use the **secret / service_role** key anywhere in this project.

---

## 3. Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres.<ref>:<db-password>@aws-0-<region>.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_JWT_SECRET=
LLM_PROVIDER=fake
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

- **DATABASE_URL:** paste the Session pooler string and put your database password in it. If the password contains special characters, URL-encode them (`@` -> `%40`, `#` -> `%23`, `/` -> `%2F`).
- **SUPABASE_JWT_SECRET:** leave empty for new projects (they sign tokens with JWT signing keys, checked through `SUPABASE_URL`). Only older projects that still use the **legacy JWT secret** need it filled in.
- **LLM_PROVIDER=fake** produces placeholder text and needs no API key. Set `gemini` plus `GEMINI_API_KEY` to use Google Gemini.

Start it:

```bash
uvicorn app.main:app --reload --port 8000
```

Check http://localhost:8000/api/v1/health. It must show `{"status":"ok","database":true}`.
Interactive API docs: http://localhost:8000/docs

---

## 4. Run the frontend

In a **second terminal**:

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCKS=false
```

Start it:

```bash
npm run dev
```

Open http://localhost:3000 and click **Sign up**.

Changes to `.env.local` are only picked up after restarting `npm run dev`.

---

## 5. Try the full workflow

A reviewer can never approve content they created or edited, so you need **two accounts**
(use a normal window for one and a private window for the other).

1. **User A** signs up, then goes to **Clients** and adds a client brand (tone, words to use / avoid).
2. User A creates a **campaign** for that client.
3. **User B** signs up once (this creates their profile).
4. User A opens the campaign, and under **Team** adds User B's email with the role **Reviewer**.
5. User A writes a **brief** (topic, objective, platforms) and clicks **Generate content**.
6. User B opens **Reviews**, picks a post and chooses **Approve**, **Request changes** (the AI writes a new version) or **Reject** (final, needs a reason).
7. Everyone in the campaign can comment; User A sees the full history under **Activity log**.

| Role | Can do |
|---|---|
| Owner | Everything in the campaign, manages the team, sees the activity log |
| Creator | Write briefs, generate, edit, delete content |
| Reviewer | Approve, reject, request changes, edit |
| Brand manager | Edit the client's brand guidelines |

---

## 6. Logs and tests

- **Backend terminal** (uvicorn): one line per API call with who made it, plus an `Activity:` line for each action (generated, approved, rejected, ...). Set `LOG_LEVEL=DEBUG` or `WARNING` in `backend/.env` to change the detail.
- **Frontend terminal** (`npm run dev`): `[auth]` lines for every login, logout and signup.
- **Backend tests** (use a local SQLite database, never Supabase):
  ```bash
  cd backend && source .venv/bin/activate && pytest
  ```
- **Frontend checks:** `cd frontend && npm run lint && npx tsc --noEmit`

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `/api/v1/health` shows `"database": false` | `DATABASE_URL` is wrong: use the **Session pooler** string, check the password, URL-encode special characters. |
| Browser error *"Your project's URL and Key are required to create a Supabase client"* | `frontend/.env.local` is missing `NEXT_PUBLIC_SUPABASE_URL` or the key. Fix it and restart `npm run dev`. |
| Page says *"Can't reach the backend at http://localhost:8000"* | Start the backend (step 3), or fix `NEXT_PUBLIC_API_BASE_URL`. |
| Logged in, but pages fail with *"Invalid token"* / 401 | Backend `SUPABASE_URL` doesn't match the frontend's project, or the project uses the legacy secret and `SUPABASE_JWT_SECRET` is empty. |
| Sign-up says *"check your inbox"* but no email arrives | Supabase's email rate limit. Turn off **Confirm email** (step 2.3) for local development. |
| Adding a team member says *"No user with that email"* | That person must sign up and open the app once first. |
| Reviewer sees *"another reviewer has to review it"* | They created or edited that version; use a different reviewer account. |
| `type "user_role" already exists` in the SQL editor | The schema was already applied. Nothing to do. |

---

## More detail

- [`backend/README.md`](backend/README.md): API design, role matrix, status flow, tests and deliverables.
- [`frontend/README.md`](frontend/README.md): how auth and the API client are wired.
- API reference: [`backend/docs/openapi.yaml`](backend/docs/openapi.yaml) or http://localhost:8000/docs when the backend is running.
