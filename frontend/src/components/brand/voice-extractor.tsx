"use client";

/**
 * "Decode brand voice": the user gives a website URL and/or sample posts, the backend's AI
 * proposes tone, preferred terms and terms to avoid, and the user reviews them before saving.
 *
 * TODO:
 * - Inputs: website URL, sample posts or guidelines (at least one required).
 * - Call the planned POST /api/v1/brands/voice/extract endpoint
 *   (see backend/app/controllers/voice.py) and show progress while it runs.
 * - Prefill the brand form (tone, preferred_terms, avoided_terms) with the result; nothing is
 *   saved until the user submits the form.
 */
export function VoiceExtractor() {
  return null;
}
