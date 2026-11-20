# ContentFlow frontend (Next.js 16)

Sign-in is done with Supabase Auth (`@supabase/ssr`). Data comes from the FastAPI backend in `../backend`,
called with the user's Supabase access token.

## Setup

1. Set up Supabase and start the backend first (see `../backend/README.md`).
2. `cp .env.example .env.local` and fill in:
   - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (or the legacy `NEXT_PUBLIC_SUPABASE_ANON_KEY`): Supabase -> Project Settings -> API
     (the anon / publishable key, never the service_role / secret key).
   - `NEXT_PUBLIC_API_BASE_URL`: the backend, `http://localhost:8000` by default.
   - `NEXT_PUBLIC_USE_MOCKS=true` shows mock data with no Supabase or backend (UI work only).
3. In Supabase -> Authentication -> URL Configuration, set the Site URL to `http://localhost:3000` and add
   `http://localhost:3000/auth/callback` to the Redirect URLs (email confirmation, Google/LinkedIn sign-in).
4. `npm install && npm run dev`, then open http://localhost:3000.

## How it fits together

| File | Purpose |
|---|---|
| `src/proxy.ts` | Refreshes the session cookie; redirects signed-out users from app pages to `/login` |
| `src/lib/supabase/{client,server}.ts` | Supabase clients for the browser and the server |
| `src/app/auth/callback/route.ts` | Handles email confirmation and OAuth redirects |
| `src/lib/api/client.ts` | `api()` calls `/api/v1/...` with `Authorization: Bearer <token>` |
| `src/lib/api/dashboard.ts` | Builds the dashboard from `/me`, `/brands`, `/campaigns`, `/dashboard`, content and activity |
| `src/types/api.ts` | Backend response types (mirror `backend/app/schemas.py`) |
| `src/types/app.ts` | View models the components use |

`GET /me` is always called first: the first authenticated request creates the user's profile row in the
backend, which a campaign owner needs before adding that person by email.
