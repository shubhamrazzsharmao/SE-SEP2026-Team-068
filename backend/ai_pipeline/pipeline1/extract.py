"""
extract.py  --  Pipeline 1, step 4: AI A (EXTRACTION)

JOB: send the chunks to the LLM and get back structured, source-linked
     material: key messages, facts, audience, angles and restrictions.
     This is the FIRST step that uses an LLM.

THE MOST IMPORTANT PART is verify_items(): LLMs sometimes invent facts or cite
the wrong chunk. So after the model answers, plain code checks that every fact's
"evidence" text really appears in the chunk the model said it came from.
Facts that fail the check are DROPPED. Every later step trusts these facts.

INPUT : data/output/chunks.json, data/campaign_input.json,
        prompts/extractor_system.txt, prompts/extractor_user.txt
OUTPUT: data/output/extracted.json

RUN   : from the mosaic_ai folder ->  py pipeline1/extract.py
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS + IMPORTS (same pattern as the other pipeline scripts)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "output" / "chunks.json"
CAMPAIGN_FILE = PROJECT_ROOT / "data" / "campaign_input.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "extracted.json"
RAW_REPLY_FILE = PROJECT_ROOT / "data" / "output" / "extractor_raw_reply.txt"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

sys.path.insert(0, str(PROJECT_ROOT))
import config  # noqa: E402
from llm import call_llm, parse_json_response  # noqa: E402

# The LLM ROLE this step uses. The actual model is chosen in config.py.
ROLE = "extractor"


# ---------------------------------------------------------------------------
# BUILDING THE PROMPT
# ---------------------------------------------------------------------------

def load_prompt(filename: str) -> str:
    """Read a prompt template from the prompts folder."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise SystemExit(f"[ERROR] Prompt file missing: {path}")
    return path.read_text(encoding="utf-8")


def build_campaign_context(campaign_input: dict) -> str:
    """Turn the campaign settings into a short text block for the prompt."""
    c = campaign_input["campaign"]
    goals = "\n".join(f"- {g}" for g in c["goals"])
    return (
        f"Campaign name: {c['name']}\n"
        f"Theme: {c['theme']}\n"
        f"Target audience: {c['target_audience']}\n"
        f"Platforms: {', '.join(c['platforms'])}\n"
        f"Goals:\n{goals}"
    )


def build_chunks_text(chunks: list) -> str:
    """Show every chunk to the model, each labelled with its ID."""
    parts = []
    for chunk in chunks:
        parts.append(f"[CHUNK {chunk['chunk_id']}]\n{chunk['text']}\n[END CHUNK]")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# CHECKING THE MODEL'S OUTPUT
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Make text comparable: lowercase, one space between words, and no leading
    or trailing quotes, dots or ellipses. Used only for the evidence check,
    so tiny spacing or capitalisation differences do not cause false alarms.
    """
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return text.strip(" .\u2026\"'")


def validate_structure(data: dict) -> None:
    """Make sure the JSON has all the expected parts. Raises ValueError if not."""
    for key in ("key_messages", "facts", "audience", "angles", "restrictions"):
        if key not in data:
            raise ValueError(f"missing key '{key}'")
    for key in ("key_messages", "facts", "angles", "restrictions"):
        if not isinstance(data[key], list):
            raise ValueError(f"'{key}' should be a list")
    if not isinstance(data["audience"], dict):
        raise ValueError("'audience' should be an object")
    data["audience"].setdefault("description", "")
    data["audience"].setdefault("insights", [])


def verify_items(items: list, chunk_lookup: dict, label: str):
    """
    For each item that claims a source (facts, restrictions, audience insights):
      1. the cited chunk must exist, and
      2. the "evidence" text must actually appear inside that chunk.
    Returns (kept_items, dropped_items). Dropped items carry a "reason".
    """
    kept, dropped = [], []
    for item in items:
        if not isinstance(item, dict):
            dropped.append({"item": item, "reason": "not an object"})
            continue

        chunk_id = item.get("source_chunk", "")
        evidence = item.get("evidence", "")

        if chunk_id not in chunk_lookup:
            dropped.append({"item": item, "reason": f"chunk '{chunk_id}' does not exist"})
        elif not evidence.strip():
            dropped.append({"item": item, "reason": "no evidence given"})
        elif normalize(evidence) not in normalize(chunk_lookup[chunk_id]):
            dropped.append({"item": item, "reason": "evidence not found in that chunk"})
        else:
            kept.append(item)

    if dropped:
        print(f"     [CHECK] {label}: dropped {len(dropped)} of {len(items)} "
              f"(unverified)")
    return kept, dropped


def process_reply(reply: str, chunk_lookup: dict) -> dict:
    """
    Parse the model's reply, validate it, verify the evidence, and renumber IDs.
    Raises ValueError if the reply is unusable (the caller will retry).
    """
    data = parse_json_response(reply)   # may raise ValueError / JSONDecodeError
    validate_structure(data)

    facts, dropped_facts = verify_items(data["facts"], chunk_lookup, "facts")
    restrictions, dropped_restr = verify_items(
        data["restrictions"], chunk_lookup, "restrictions")
    insights, dropped_insights = verify_items(
        data["audience"]["insights"], chunk_lookup, "audience insights")

    if len(facts) < config.EXTRACT_MIN_FACTS:
        raise ValueError(
            f"only {len(facts)} verified fact(s), need at least "
            f"{config.EXTRACT_MIN_FACTS}")

    # Renumber facts f1, f2, ... because some may have been dropped.
    # (These IDs are what plan items will point to later.)
    for number, fact in enumerate(facts, start=1):
        fact["id"] = f"f{number}"
    for number, msg in enumerate(data["key_messages"], start=1):
        msg["id"] = f"m{number}"
    for number, angle in enumerate(data["angles"], start=1):
        angle["id"] = f"a{number}"

    data["facts"] = facts
    data["restrictions"] = restrictions
    data["audience"]["insights"] = insights
    # Keep a record of what was dropped, so you can review it.
    data["_dropped"] = {
        "facts": dropped_facts,
        "restrictions": dropped_restr,
        "audience_insights": dropped_insights,
    }
    return data


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Load inputs.
    if not CHUNKS_FILE.exists():
        print(f"[ERROR] {CHUNKS_FILE} not found. Run chunk.py first.")
        return
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    campaign_input = json.loads(CAMPAIGN_FILE.read_text(encoding="utf-8"))

    # Quick lookup: chunk_id -> chunk text (used by the evidence check).
    chunk_lookup = {c["chunk_id"]: c["text"] for c in chunks}

    # 2. Build the prompts by filling the placeholders in the template files.
    system_prompt = load_prompt("extractor_system.txt")
    user_prompt = (
        load_prompt("extractor_user.txt")
        .replace("{{CAMPAIGN_CONTEXT}}", build_campaign_context(campaign_input))
        .replace("{{CHUNKS}}", build_chunks_text(chunks))
    )
    print(f"Sending {len(chunks)} chunk(s) to role '{ROLE}'...")

    # 3. Call the model, with retries if the output is unusable.
    result = None
    for attempt in range(1, config.EXTRACT_MAX_ATTEMPTS + 1):
        print(f"[Attempt {attempt}/{config.EXTRACT_MAX_ATTEMPTS}]")
        reply = call_llm(ROLE, user_prompt, system_prompt, json_mode=True)

        # Save the raw reply every time, so you can inspect it if things fail.
        RAW_REPLY_FILE.parent.mkdir(parents=True, exist_ok=True)
        RAW_REPLY_FILE.write_text(reply, encoding="utf-8")

        try:
            result = process_reply(reply, chunk_lookup)
            break   # success
        except ValueError as error:
            print(f"     [RETRY] Output unusable: {error}")

    if result is None:
        print(f"\n[FAILED] No usable output after {config.EXTRACT_MAX_ATTEMPTS} "
              f"attempts. The last raw reply is saved in:\n  {RAW_REPLY_FILE}")
        return

    # 4. Save.
    result["_meta"] = {"role": ROLE, "chunks_used": len(chunks)}
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # 5. Print a readable summary.
    print(f"\n[OK] Saved to {OUTPUT_FILE}")
    print(f"     {len(result['key_messages'])} key messages, "
          f"{len(result['facts'])} verified facts, "
          f"{len(result['angles'])} angles, "
          f"{len(result['restrictions'])} restriction(s)")

    print("\nKey messages:")
    for m in result["key_messages"]:
        print(f"  {m['id']}: {m['text']}")
    print("\nRestrictions:")
    for r in result["restrictions"]:
        print(f"  - {r['text']}   [{r['source_chunk']}]")
    print("\nFirst 5 facts:")
    for f in result["facts"][:5]:
        print(f"  {f['id']} [{f['category']}] {f['text']}   [{f['source_chunk']}]")


if __name__ == "__main__":
    main()