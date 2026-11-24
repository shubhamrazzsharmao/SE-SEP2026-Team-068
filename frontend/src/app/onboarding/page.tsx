import { notFound } from "next/navigation";

/**
 * First-run onboarding, shown once after signup.
 *
 * TODO:
 * - Render <OnboardingFlow /> from src/components/onboarding/onboarding-flow.tsx.
 * - Add "/onboarding" to PROTECTED in src/proxy.ts (signed-in users only).
 * - Redirect here after the first login if the user has not finished onboarding.
 *
 * Returns 404 until the flow and its backend endpoint exist.
 */
export default function OnboardingPage() {
  notFound();
}
