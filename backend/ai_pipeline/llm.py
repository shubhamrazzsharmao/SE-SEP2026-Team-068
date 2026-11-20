"""
llm.py  --  the LLM wrapper.

Every pipeline step calls ONE function from here:

    call_llm(role, user_prompt, system_prompt="", json_mode=False)

The wrapper looks up the role in config.py, picks the model, calls the
provider, retries on temporary errors, and falls back to a second model if
the first one is broken. Pipeline code never mentions a model or a key.

It also provides parse_json_response(), which safely turns the model's
reply into a Python dict (models sometimes wrap JSON in extra text).
"""

import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APIStatusError, RateLimitError

import config

# ---------------------------------------------------------------------------
# LOAD THE API KEY FROM .env
# .env sits in the same folder as this file (the project root).
# override=True means the .env value wins over any old value on your system.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

# The client is created once, on first use, then reused.
_client = None


def get_client() -> OpenAI:
    """Create (once) and return the client that talks to the provider."""
    global _client
    if _client is None:
        api_key = os.getenv(config.LLM_API_KEY_ENV_VAR)
        if not api_key:
            raise SystemExit(
                f"[ERROR] No API key found. Add a line to your .env file:\n"
                f"        {config.LLM_API_KEY_ENV_VAR}=your_key_here"
            )
        _client = OpenAI(api_key=api_key, base_url=config.LLM_BASE_URL)
    return _client


def call_llm(role: str, user_prompt: str, system_prompt: str = "",
             json_mode: bool = False) -> str:
    """
    Ask the model assigned to `role` and return its reply as text.

    role          : a key of config.LLM_ROLES, e.g. "extractor"
    user_prompt   : the main message (the task + the data)
    system_prompt : optional standing instructions ("You are a careful...")
    json_mode     : True asks the provider to return valid JSON only.
                    Note: some providers require the word "JSON" to appear
                    somewhere in your prompt when this is on.
    """
    # 1. Find the role's settings in config.py.
    if role not in config.LLM_ROLES:
        known = ", ".join(config.LLM_ROLES)
        raise ValueError(f"Unknown role '{role}'. Roles in config.py: {known}")
    settings = config.LLM_ROLES[role]

    # 2. Models to try, in order: main first, then the fallback if there is one.
    models_to_try = [settings["model"]]
    if settings.get("fallback_model"):
        models_to_try.append(settings["fallback_model"])

    # 3. Build the message list in the format the provider expects.
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    # 4. Try each model; for each model, retry on temporary problems.
    client = get_client()
    last_error = None

    for model in models_to_try:
        wait = config.LLM_RETRY_WAIT_SECONDS

        for attempt in range(1, config.LLM_MAX_RETRIES + 1):
            try:
                kwargs = dict(
                    model=model,
                    messages=messages,
                    temperature=settings["temperature"],
                    max_tokens=settings["max_tokens"],
                )
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = client.chat.completions.create(**kwargs)
                # content can be None if the model returned nothing.
                return response.choices[0].message.content or ""

            except (RateLimitError, APIConnectionError) as error:
                # Temporary: rate limit hit, or network hiccup. Wait and retry.
                last_error = error
                print(f"[LLM] {model}: temporary problem "
                      f"(try {attempt}/{config.LLM_MAX_RETRIES}), waiting {wait}s...")
                time.sleep(wait)
                wait *= 2   # wait longer each time

            except APIStatusError as error:
                # Permanent for this model: wrong model ID, bad request,
                # bad key... Retrying the same model will not help, so move
                # on to the fallback model.
                last_error = error
                print(f"[LLM] {model}: failed ({error.status_code}). Trying next model.")
                break

    raise RuntimeError(
        f"All models failed for role '{role}'. Last error: {last_error}"
    )


def parse_json_response(text: str) -> dict:
    """
    Turn the model's reply into a Python dict.
    Models sometimes wrap JSON in ```json fences or add a sentence before it.
    We cut out everything from the first '{' to the last '}'.
    """
    text = text.strip()
    # Remove markdown code fences if present.
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in the model's reply.")
    return json.loads(text[start:end + 1])