"""LLM access behind a small interface so the pipeline and the tests never depend on
a real provider. `fake` is the default and needs no API key."""
from dataclasses import dataclass
from typing import Optional, Protocol

import httpx

from app.core.config import get_settings
from app.enums import Platform


class LLMError(Exception):
    """Raised when the provider fails; callers must save nothing and surface a 502."""


@dataclass
class Context:
    platform: Platform
    topic: str
    objective: str
    audience: Optional[str]
    key_messages: Optional[str]
    tone: str
    preferred_terms: list
    avoided_terms: list


@dataclass
class Generated:
    body: str
    creative_suggestion: Optional[str]
    prompt: str
    model: str


class LLMClient(Protocol):
    def generate(self, ctx: Context) -> Generated: ...
    def revise(self, ctx: Context, previous_body: str, feedback: str) -> Generated: ...


# ---------------------------------------------------------------- prompts
_PLATFORM_RULES = {
    Platform.blog: "a long-form blog article (600-900 words) with a title, intro, 3-4 headed sections and a conclusion",
    Platform.linkedin: "a LinkedIn post (120-200 words), professional and insight-led, ending with a question",
    Platform.facebook: "a Facebook post (60-120 words), conversational, with a clear call to action",
    Platform.instagram: "an Instagram caption (under 150 words) with 3-5 relevant hashtags",
}


def build_prompt(ctx: Context, previous_body: Optional[str] = None, feedback: Optional[str] = None) -> str:
    lines = [
        f"Write {_PLATFORM_RULES[ctx.platform]}.",
        f"Topic: {ctx.topic}",
        f"Campaign objective: {ctx.objective}",
        f"Target audience: {ctx.audience or 'general'}",
        f"Key messages: {ctx.key_messages or 'none supplied'}",
        f"Brand tone: {ctx.tone}",
        f"Use these terms where natural: {', '.join(ctx.preferred_terms) or 'none'}",
        f"Never use these terms: {', '.join(ctx.avoided_terms) or 'none'}",
        "Do not invent statistics, quotes or claims that are not in the brief.",
    ]
    if ctx.platform == Platform.instagram:
        lines.append("After the caption add a line '---CREATIVE---' then a one-sentence visual suggestion.")
    if previous_body is not None:
        lines += ["", "Revise the previous draft below according to the reviewer's feedback. "
                  "Change only what the feedback asks for.",
                  f"Reviewer feedback: {feedback}", "Previous draft:", previous_body]
    return "\n".join(lines)


def _split_creative(text: str, platform: Platform):
    if platform == Platform.instagram and "---CREATIVE---" in text:
        body, creative = text.split("---CREATIVE---", 1)
        return body.strip(), creative.strip() or None
    return text.strip(), None


# ---------------------------------------------------------------- fake (default)
class FakeLLMClient:
    """Deterministic placeholder copy built from the brief and brand guidelines."""
    model = "fake-llm-v1"

    def _write(self, ctx: Context) -> tuple[str, Optional[str]]:
        terms = f" Key terms: {', '.join(ctx.preferred_terms)}." if ctx.preferred_terms else ""
        msgs = ctx.key_messages or ctx.objective
        aud = ctx.audience or "our audience"
        if ctx.platform == Platform.blog:
            return (f"# {ctx.topic}\n\nIntro: {ctx.objective}\n\n## Why it matters for {aud}\n{msgs}\n\n"
                    f"## What to do next\nTone: {ctx.tone}.{terms}\n\n## Conclusion\n{ctx.objective}", None)
        if ctx.platform == Platform.linkedin:
            return (f"{ctx.topic}: what {aud} should know.\n\n{msgs}\n\n"
                    f"{terms.strip()}\n\nWhat is your view?", None)
        if ctx.platform == Platform.facebook:
            return (f"{ctx.topic} - {msgs}{terms}\n\nLearn more today!", None)
        return (f"{ctx.topic} | {msgs}\n\n#{ctx.topic.split()[0].lower()} #brand #campaign",
                f"Bright, on-brand photo that shows: {ctx.topic}.")

    def generate(self, ctx: Context) -> Generated:
        body, creative = self._write(ctx)
        return Generated(body, creative, build_prompt(ctx), self.model)

    def revise(self, ctx: Context, previous_body: str, feedback: str) -> Generated:
        body, creative = self._write(ctx)
        body = f"{body}\n\n[Revised after feedback: {feedback}]"
        return Generated(body, creative, build_prompt(ctx, previous_body, feedback), self.model)


# ---------------------------------------------------------------- Gemini
class GeminiClient:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str):
        self.api_key, self.model = api_key, model

    def _call(self, prompt: str, platform: Platform) -> Generated:
        if not self.api_key:
            raise LLMError("GEMINI_API_KEY is not configured.")
        try:
            r = httpx.post(self.URL.format(model=self.model),
                           headers={"x-goog-api-key": self.api_key},
                           json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise LLMError(f"Gemini request failed: {exc.__class__.__name__}") from exc
        if not text.strip():
            raise LLMError("Gemini returned an empty response.")
        body, creative = _split_creative(text, platform)
        return Generated(body, creative, prompt, self.model)

    def generate(self, ctx: Context) -> Generated:
        return self._call(build_prompt(ctx), ctx.platform)

    def revise(self, ctx: Context, previous_body: str, feedback: str) -> Generated:
        return self._call(build_prompt(ctx, previous_body, feedback), ctx.platform)


def get_llm_client() -> LLMClient:
    """FastAPI dependency; tests override it."""
    s = get_settings()
    if s.llm_provider == "gemini":
        return GeminiClient(s.gemini_api_key, s.gemini_model)
    return FakeLLMClient()
