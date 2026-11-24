"""Brand voice extraction: collect source text, ask the AI for a voice profile. NOT IMPLEMENTED YET (placeholder).

TODO:
- If a URL is given, fetch the page server-side and keep only its visible text. Limit size and
  timeout, allow only http(s), and block private/internal addresses (SSRF).
- Combine it with the pasted sample posts and call app.ai.voice_extractor.
- Raise a 502 AppError on provider failure; never write to the database.
"""
