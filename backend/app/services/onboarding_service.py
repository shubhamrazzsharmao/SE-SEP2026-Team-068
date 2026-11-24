"""Onboarding answers (role and goals) for the signed-in user. NOT IMPLEMENTED YET (placeholder).

TODO:
- Decide where the answers live: new columns on users (app/models/user.py) or a separate
  user_onboarding table. Either way it needs a migration in backend/supabase.
- get(db, user) -> current answers, or "not started".
- save(db, user, body: OnboardingIn) -> store answers and the completion timestamp.
"""
