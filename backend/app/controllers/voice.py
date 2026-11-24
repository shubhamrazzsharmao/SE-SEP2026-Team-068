"""Controller for brand voice extraction. NOT IMPLEMENTED YET (placeholder).

Planned endpoint:
    POST /api/v1/brands/voice/extract  (VoiceExtractIn -> VoiceExtractOut)

Returns a *suggested* tone, preferred terms and terms to avoid. It saves nothing: the user
reviews the suggestion and then creates or updates the brand through the existing endpoints.
A provider failure returns 502, like generation.

TODO:
- Define the router and endpoint, delegating to app.services.voice_service.
- Register the router in ROUTERS (app/controllers/__init__.py).
- Re-export the OpenAPI file: python scripts/export_openapi.py
"""
