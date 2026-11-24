"use client";

/**
 * Two-step onboarding wizard.
 *   Step 1: who the user is (freelancer, agency, in-house team).
 *   Step 2: what they want from the product (multi-select goals).
 *
 * TODO:
 * - Build the two steps (reference: components/onboarding/onboarding-flow.tsx in the old mock frontend).
 * - Save the answers with a server action in src/lib/actions.ts that calls the planned
 *   PUT /api/v1/me/onboarding endpoint (see backend/app/controllers/onboarding.py),
 *   then redirect to /dashboard.
 */
export function OnboardingFlow() {
  return null;
}
