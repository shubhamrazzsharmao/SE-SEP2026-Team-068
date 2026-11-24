"""Controller for first-run onboarding. NOT IMPLEMENTED YET (placeholder).

Planned endpoints:
    GET /api/v1/me/onboarding  -> OnboardingOut (has the caller finished onboarding, and their answers)
    PUT /api/v1/me/onboarding  -> save OnboardingIn, mark onboarding as done

TODO:
- Define `router = APIRouter(prefix="/me/onboarding", tags=["Account"])` and the two endpoints,
  delegating to app.services.onboarding_service.
- Register the router in ROUTERS (app/controllers/__init__.py).
- Re-export the OpenAPI file: python scripts/export_openapi.py
"""
