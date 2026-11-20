"""
test_llm.py  --  checks that your key, config and wrapper all work.

It does two things:
  1. Lists the model IDs your Groq account can use (so you can fix any wrong
     IDs in config.py).
  2. Sends a tiny test message through every role in config.py.

RUN: from the mosaic_ai folder ->  py test_llm.py
"""

import time

import config
from llm import call_llm, get_client


def main():
    # PART 1: list the models available to your account.
    print("=== Models available on your account ===")
    try:
        models = sorted(m.id for m in get_client().models.list().data)
        for model_id in models:
            print("  ", model_id)
    except Exception as error:
        print(f"[ERROR] Could not list models: {error}")
        print("        Check your key in .env")
        return

    # PART 2: test every role.
    print("\n=== Testing each role from config.py ===")
    for role, settings in config.LLM_ROLES.items():
        # Warn if the configured model is not in the account's list.
        if settings["model"] not in models:
            print(f"[WARN] Role '{role}': model '{settings['model']}' is not in the "
                  f"list above. Fix it in config.py.")

        started = time.time()
        try:
            reply = call_llm(role, "Reply with exactly one word: OK")
            seconds = time.time() - started
            print(f"[OK] {role}: replied '{reply.strip()[:40]}' in {seconds:.1f}s")
        except Exception as error:
            print(f"[FAIL] {role}: {error}")


if __name__ == "__main__":
    main()