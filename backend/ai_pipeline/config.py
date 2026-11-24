"""
config.py  --  ONE place for settings you may want to change.

Pipeline scripts import values from here instead of hard-coding them.
Later we will add model names and provider settings to this same file.
(API keys will NOT go here. They go in a separate .env file.)
"""

# ---------------------------------------------------------------------------
# CHUNKING SETTINGS
# ---------------------------------------------------------------------------

# Maximum words allowed in one chunk.
# We use a small value for the demo because the demo brief is short.
# For real, longer documents you would raise this to about 300-500.
CHUNK_MAX_WORDS = 150

# When one section has to be split into several chunks, the next chunk starts
# with the last few words of the previous one. This stops a fact from being
# cut in half at the boundary. Set to 0 to turn overlap off.
CHUNK_OVERLAP_WORDS = 25

# ---------------------------------------------------------------------------
# EMBEDDING SETTINGS
# ---------------------------------------------------------------------------

# Where embeddings are computed. Only "local" is built for now: a small model
# that runs on your own laptop, with no API key needed.
EMBEDDING_PROVIDER = "local"

# The local model. It is downloaded automatically the first time you run
# embed.py (about 90 MB), then cached on your machine.
# WARNING: vectors from different models cannot be compared. If you change
# this, you must re-run embed.py so ALL chunks are re-embedded.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# How many chunks are embedded at once. Higher is faster but uses more memory.
# 32 is safe for 8 GB RAM.
EMBEDDING_BATCH_SIZE = 32

# ---------------------------------------------------------------------------
# LLM SETTINGS
# This is the ONLY place that knows model names and provider details.
# Pipeline scripts ask for a ROLE (like "extractor"), never a model name.
# If a model breaks, change it here and no other file needs to change.
# ---------------------------------------------------------------------------

# Provider details. Groq speaks the OpenAI API format, so to switch provider
# later you change these three lines (and the key in .env).
LLM_PROVIDER_NAME = "groq"
LLM_BASE_URL = "https://api.groq.com/openai/v1"
LLM_API_KEY_ENV_VAR = "GROQ_API_KEY"   # the NAME of the variable inside .env

# One entry per role in the pipeline.
#   model          -> tried first
#   fallback_model -> tried if the main model fails (optional)
#   temperature    -> 0 = very consistent, 1 = more creative
#   max_tokens     -> maximum length of the reply
# NOTE: these model IDs are PLACEHOLDERS. Run test_llm.py to see the exact IDs
# your Groq account offers, then correct them here if needed.
LLM_ROLES = {
    # AI A: reads the document and extracts facts. Needs accuracy, not creativity.
    "extractor": {
        "model": "qwen/qwen3.8-27b",
        "fallback_model": "openai/gpt-oss-20b",
        "temperature": 0.1,
        "max_tokens": 4000,
    },
    # AI B: builds the campaign plan. A little creativity is useful here.
    # A different model family from the extractor on purpose.
    "planner": {
        "model": "openai/gpt-oss-120b",
        "fallback_model": "qwen/qwen3.8-27b",
        "temperature": 0.5,
        "max_tokens": 6000,
    },
}

# What to do when a call fails (for example the free-tier rate limit is hit).
LLM_MAX_RETRIES = 3            # tries per model before giving up on it
LLM_RETRY_WAIT_SECONDS = 5     # wait before retrying, doubles each time


# ---------------------------------------------------------------------------
# AI A (EXTRACTION) SETTINGS
# ---------------------------------------------------------------------------

# How many times to retry if the model returns broken or too-thin output.
EXTRACT_MAX_ATTEMPTS = 3

# If fewer than this many verified facts survive checking, the attempt counts
# as failed and is retried. The demo brief has plenty of facts.
EXTRACT_MIN_FACTS = 5

# ---------------------------------------------------------------------------
# POSTING SCHEDULE ("CADENCE") SETTINGS
# ---------------------------------------------------------------------------

# Maximum posts in one plan. Regenerating a plan does not count against this.
PLAN_MAX_POSTS = 10

# Retries if the AI's proposed schedule fails the checks.
CADENCE_MAX_ATTEMPTS = 3

# Allowed post lengths per platform, with what each one means.
# The AI must pick one name from each platform's list. Pipeline 2 will use the
# description as a rule when drafting. The word counts are starting points
# that you can change freely.
LENGTH_OPTIONS = {
    "blog":      {"short": "about 500 words",
                  "standard": "about 900 words",
                  "long": "1,500 words or more"},
    "linkedin":  {"short": "under 100 words",
                  "standard": "150 to 250 words"},
    "facebook":  {"short": "under 60 words",
                  "standard": "80 to 150 words"},
    "instagram": {"short": "caption under 50 words",
                  "standard": "caption of 80 to 150 words"},
}

# The role for the schedule proposal. Added here (not inside LLM_ROLES above)
# so you can paste it at the bottom. Change the model here any time.
LLM_ROLES["cadence"] = {
    "model": "openai/gpt-oss-20b",
    "fallback_model": "qwen/qwen3.8-27b",
    "temperature": 0.3,
    "max_tokens": 3000,
}

# ---------------------------------------------------------------------------
# AI B (PLAN GENERATION) SETTINGS
# ---------------------------------------------------------------------------

# Retries per AI call if the reply fails the checks.
PLAN_MAX_ATTEMPTS = 3

# Maximum fact IDs one plan item may cite.
PLAN_MAX_FACTS_PER_ITEM = 3

# Plan item fields a human may edit by hand in plan.json (checkpoint 2).
# Everything else in the plan is locked. Add or remove names here to change that.
PLAN_HUMAN_EDITABLE_FIELDS = ["topic", "key_message", "cta", "format_note"]