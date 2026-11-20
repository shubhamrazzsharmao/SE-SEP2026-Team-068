"""
plan.py  --  Pipeline 1, step 5b: AI B (PLAN GENERATION)

JOB: turn the verified material from AI A plus the APPROVED schedule into a
     campaign plan (one entry per post). The work is split on purpose:

   CODE builds the slots (date + platform + length) from cadence.json
   AI   decides WHAT each post is about (topic, message, facts, CTA)
   CODE checks everything the AI wrote and rejects anything invalid

Every run saves a NEW VERSION (plan_versions/plan_v001.json, ...) and copies
the latest to plan.json. Nothing is ever overwritten. An approved plan is LOCKED.

COMMANDS (from the mosaic_ai folder):
  py pipeline1/plan.py                              generate a plan
  py pipeline1/plan.py --feedback "make it playful" regenerate the WHOLE plan
  py pipeline1/plan.py --only p03 p05 --feedback "..." regenerate ONLY those posts
  py pipeline1/plan.py --show                       print the current plan
  py pipeline1/plan.py --approve --by "Name"        approve and lock the plan
  py pipeline1/plan.py --reject "reason"            reject the plan (reason required)

INPUT : campaign_input.json, extracted.json, cadence.json (approved), prompts/planner_*.txt
OUTPUT: data/output/plan.json and data/output/plan_versions/
"""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS + IMPORTS (same pattern as the other pipeline scripts)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN_FILE = PROJECT_ROOT / "data" / "campaign_input.json"
EXTRACTED_FILE = PROJECT_ROOT / "data" / "output" / "extracted.json"
CADENCE_FILE = PROJECT_ROOT / "data" / "output" / "cadence.json"
PLAN_FILE = PROJECT_ROOT / "data" / "output" / "plan.json"
VERSIONS_DIR = PROJECT_ROOT / "data" / "output" / "plan_versions"
RAW_REPLY_FILE = PROJECT_ROOT / "data" / "output" / "planner_raw_reply.txt"

sys.path.insert(0, str(PROJECT_ROOT))
import config  # noqa: E402
from llm import call_llm, parse_json_response  # noqa: E402
# Reuse the helpers and the calendar builder from cadence.py (same folder).
from cadence import (  # noqa: E402
    build_calendar, fill, load_json_file, load_prompt, validate_cadence)

ROLE = "planner"   # the actual model is chosen in config.py

# Text fields every plan item must have (and must not be empty).
REQUIRED_TEXT_FIELDS = ["topic", "key_message", "cta", "format_note"]


# ===========================================================================
# PART 1: LOADING THE APPROVED SCHEDULE AND BUILDING SLOTS
# ===========================================================================

def load_approved_cadence(campaign: dict) -> dict:
    """Load cadence.json. Stop with a clear message unless it is valid AND approved."""
    cadence = load_json_file(CADENCE_FILE)
    errors = validate_cadence(cadence, campaign)
    if errors:
        raise SystemExit("[ERROR] cadence.json has problems:\n  - " + "\n  - ".join(errors))
    if not cadence.get("approved"):
        raise SystemExit("[ERROR] The schedule is not approved yet.\n"
                         "        Run:  py pipeline1/cadence.py --approve")
    return cadence


def build_slots(cadence: dict, campaign: dict) -> list:
    """
    One slot per post: slot_id, date, weekday, platform, length, week number.
    The slot ids (p01, p02, ...) follow date order, so they are stable as long
    as the schedule does not change.
    """
    rows = build_calendar(cadence, campaign)
    start = date.fromisoformat(campaign["start_date"])
    for number, row in enumerate(rows, start=1):
        row["slot_id"] = f"p{number:02d}"
        row["week"] = (date.fromisoformat(row["date"]) - start).days // 7 + 1
        row["length_rule"] = config.LENGTH_OPTIONS[row["platform"]][row["length"]]
    return rows


def signature(rows: list) -> list:
    """A comparable summary of a schedule (used to detect that it changed)."""
    return [(r["date"], r["platform"], r["length"]) for r in rows]


def week_range(week: int, campaign: dict):
    start = date.fromisoformat(campaign["start_date"])
    end = date.fromisoformat(campaign["end_date"])
    week_start = start + timedelta(days=(week - 1) * 7)
    week_end = min(week_start + timedelta(days=6), end)
    return week_start.isoformat(), week_end.isoformat()


# ===========================================================================
# PART 2: BUILDING THE PROMPT (turning data into text blocks)
# ===========================================================================

def fmt_campaign(c: dict) -> str:
    goals = "\n".join(f"- {g}" for g in c["goals"])
    return (f"Campaign name: {c['name']}\nTheme: {c['theme']}\n"
            f"Target audience: {c['target_audience']}\n"
            f"Dates: {c['start_date']} to {c['end_date']}\n"
            f"Main CTA: {c['main_cta']}\nGoals:\n{goals}")


def fmt_brand(client: dict) -> str:
    b = client["brand_guidelines"]
    return (f"Client: {client['name']}\nTone: {b['tone']}\n"
            f"Preferred terms: {', '.join(b['preferred_terms'])}\n"
            f"Terms to AVOID: {', '.join(b['terms_to_avoid'])}")


def fmt_slots(slots: list) -> str:
    return "\n".join(f"{s['slot_id']} | {s['date']} ({s['weekday']}) | week {s['week']} | "
                     f"{s['platform']} | length: {s['length']} ({s['length_rule']})"
                     for s in slots)


def fmt_items(items: list) -> str:
    return "\n".join(f"{i['item_id']} | {i['date']} | {i['platform']} | "
                     f"topic: {i['topic']} | message: {i['key_message']}"
                     for i in items) or "(none)"


def fmt_key_dates(c: dict) -> str:
    return "\n".join(f"- {k['date']}: {k['event']}" for k in c.get("key_dates", [])) or "(none)"


def build_prompt(campaign, client, extracted, target, kept, feedback, current, whole, weeks_needed):
    """Fill the planner_user.txt template with everything the model needs."""
    if feedback:
        feedback_block = "=== HUMAN FEEDBACK (follow this) ===\n" + feedback
        if current:
            feedback_block += "\n\nThe previous version of the plan was:\n" + fmt_items(current["items"])
    else:
        feedback_block = ""

    if whole:
        header_task = ("Also write: a 2 to 3 sentence summary of the plan, a closing campaign CTA "
                       "in the brand's tone, and ONE short theme for each of these weeks: "
                       + ", ".join(str(w) for w in weeks_needed) + ".")
        header_fields = ('  "summary": "2 to 3 sentences describing the plan.",\n'
                         '  "campaign_cta": "The closing call to action.",\n'
                         '  "weekly_themes": [{"week": 1, "theme": "Short theme name"}],\n')
    else:
        header_task = "Only the slots listed above are being redone. Do not write a summary or themes."
        header_fields = ""

    return fill(load_prompt("planner_user.txt"), {
        "CAMPAIGN_CONTEXT": fmt_campaign(campaign),
        "BRAND": fmt_brand(client),
        "RESTRICTIONS": "\n".join(f"- {r['text']}" for r in extracted["restrictions"]) or "(none)",
        "KEY_MESSAGES": "\n".join(f"{m['id']}: {m['text']}" for m in extracted["key_messages"]),
        "FACTS": "\n".join(f"{f['id']} [{f['category']}] {f['text']}" for f in extracted["facts"]),
        "ANGLES": "\n".join(f"{a['id']}: {a['name']} - {a['why']}" for a in extracted["angles"]),
        "KEY_DATES": fmt_key_dates(campaign),
        "SLOTS": fmt_slots(target),
        "KEPT_ITEMS": fmt_items(kept) if kept else "(none, every post is being planned now)",
        "FEEDBACK_BLOCK": feedback_block,
        "HEADER_TASK": header_task,
        "HEADER_FIELDS": header_fields,
    })


# ===========================================================================
# PART 3: CHECKING THE MODEL'S REPLY
# ===========================================================================

def compile_banned(client: dict) -> list:
    """Whole-word, case-insensitive patterns for every 'term to avoid'."""
    terms = client["brand_guidelines"]["terms_to_avoid"]
    # \b makes it whole-word, so "cheap" does NOT match "cheapest".
    return [(t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)) for t in terms]


def find_banned(text: str, banned: list):
    for term, regex in banned:
        if regex.search(text):
            return term
    return None


def process_reply(reply: str, target: list, whole: bool, ctx: dict):
    """
    Parse and check the reply. Returns (header_or_None, items).
    Raises ValueError for anything wrong, which triggers a retry.
    """
    data = parse_json_response(reply)

    # ---- header (whole-plan runs only) ----
    header = None
    if whole:
        for key in ("summary", "campaign_cta"):
            if not str(data.get(key, "")).strip():
                raise ValueError(f"'{key}' is missing or empty")
        themes = {}
        raw_themes = data.get("weekly_themes")
        if not isinstance(raw_themes, list):
            raise ValueError("'weekly_themes' is missing or not a list")
        for entry in raw_themes:
            if isinstance(entry, dict) and str(entry.get("theme", "")).strip():
                try:
                    themes[int(entry.get("week"))] = str(entry["theme"]).strip()
                except (TypeError, ValueError):
                    continue
        missing_weeks = [w for w in ctx["weeks_needed"] if w not in themes]
        if missing_weeks:
            raise ValueError(f"'weekly_themes' is missing weeks: {missing_weeks}")
        header = {"summary": str(data["summary"]).strip(),
                  "campaign_cta": str(data["campaign_cta"]).strip(),
                  "weekly_themes": [{"week": w, "theme": themes[w]} for w in ctx["weeks_needed"]]}
        header_text = " ".join([header["summary"], header["campaign_cta"]] +
                               [t["theme"] for t in header["weekly_themes"]])
        bad = find_banned(header_text, ctx["banned"])
        if bad:
            raise ValueError(f"the summary, CTA or themes use the forbidden term '{bad}'")

    # ---- items ----
    raw_items = data.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("'items' is missing or not a list")

    slot_map = {s["slot_id"]: s for s in target}
    seen, result = set(), []

    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("an item is not an object")

        slot_id = raw.get("slot_id")
        if slot_id not in slot_map:
            raise ValueError(f"unknown slot_id '{slot_id}'. Valid ids: {', '.join(slot_map)}")
        if slot_id in seen:
            raise ValueError(f"slot_id '{slot_id}' is used twice")
        seen.add(slot_id)

        for field in REQUIRED_TEXT_FIELDS:
            if not str(raw.get(field, "")).strip():
                raise ValueError(f"{slot_id}: '{field}' is empty")

        # Fact IDs: unknown ones are dropped, duplicates removed, list capped.
        cited = raw.get("fact_ids", [])
        cited = cited if isinstance(cited, list) else []
        valid_facts = []
        for fid in cited:
            if fid in ctx["fact_ids"] and fid not in valid_facts:
                valid_facts.append(fid)
        valid_facts = valid_facts[:config.PLAN_MAX_FACTS_PER_ITEM]
        if not valid_facts:
            raise ValueError(f"{slot_id}: cites no valid fact IDs (use IDs from the facts list)")

        bad = find_banned(" ".join(str(raw[f]) for f in REQUIRED_TEXT_FIELDS), ctx["banned"])
        if bad:
            raise ValueError(f"{slot_id}: uses the forbidden term '{bad}'. "
                             "Do not use it at all, even to deny it.")

        # Date, platform and length are copied from the slot. The model cannot change them.
        slot = slot_map[slot_id]
        angle = raw.get("angle_id")
        result.append({
            "item_id": slot_id, "week": slot["week"], "date": slot["date"],
            "weekday": slot["weekday"], "platform": slot["platform"],
            "length": slot["length"], "length_rule": slot["length_rule"],
            "angle_id": angle if angle in ctx["angle_ids"] else None,
            "topic": str(raw["topic"]).strip(),
            "key_message": str(raw["key_message"]).strip(),
            "fact_ids": valid_facts,
            "cta": str(raw["cta"]).strip(),
            "format_note": str(raw["format_note"]).strip(),
        })

    missing = [s for s in slot_map if s not in seen]
    if missing:
        raise ValueError(f"missing items for slots: {', '.join(missing)}")
    result.sort(key=lambda item: item["item_id"])
    return header, result


def call_with_retries(user_prompt: str, system_prompt: str, process):
    """Call the model; if process() raises ValueError, retry and say what was wrong."""
    extra = ""
    for attempt in range(1, config.PLAN_MAX_ATTEMPTS + 1):
        print(f"[Attempt {attempt}/{config.PLAN_MAX_ATTEMPTS}] asking role '{ROLE}'...")
        reply = call_llm(ROLE, user_prompt + extra, system_prompt, json_mode=True)

        # Save the raw reply every time, in case you need to inspect it.
        RAW_REPLY_FILE.parent.mkdir(parents=True, exist_ok=True)
        RAW_REPLY_FILE.write_text(reply, encoding="utf-8")

        try:
            return process(reply)
        except ValueError as error:   # broken JSON is a ValueError too
            print(f"   [RETRY] Rejected: {error}")
            extra = ("\n\n=== YOUR PREVIOUS ANSWER WAS REJECTED ===\n"
                     f"Reason: {error}\n"
                     "Fix this and answer again with the complete JSON.")
    raise SystemExit(f"[FAILED] No usable plan after {config.PLAN_MAX_ATTEMPTS} attempts. "
                     f"Last raw reply: {RAW_REPLY_FILE}")


def whole_plan_warnings(items: list, campaign: dict, facts: list) -> list:
    """Things worth a look, but not errors."""
    warnings, seen = [], {}
    for item in items:
        key = item["topic"].lower().strip()
        if key in seen:
            warnings.append(f"Same topic twice: '{item['topic']}' ({seen[key]} and {item['item_id']})")
        seen[key] = item["item_id"]

    date_fact_ids = {f["id"] for f in facts if f["category"] == "dates"}
    for kd in campaign.get("key_dates", []):
        on_day = [i for i in items if i["date"] == kd["date"]]
        if not on_day:
            warnings.append(f"No post is scheduled on key date {kd['date']} ({kd['event']})")
        elif not any(set(i["fact_ids"]) & date_fact_ids for i in on_day):
            warnings.append(f"Posts on {kd['date']} do not cite a date fact ({kd['event']})")
    return warnings


# ===========================================================================
# PART 4: VERSIONS AND SAVING
# ===========================================================================

def load_current_plan():
    """The latest plan, or None if there is none yet."""
    if not PLAN_FILE.exists():
        return None
    return load_json_file(PLAN_FILE)


def next_version_number() -> int:
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    numbers = [int(p.stem.split("_v")[-1]) for p in VERSIONS_DIR.glob("plan_v*.json")]
    return max(numbers, default=0) + 1


def write_plan(plan: dict) -> None:
    """Write plan.json (latest) AND this version's own file in plan_versions/."""
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(plan, indent=2, ensure_ascii=False)
    PLAN_FILE.write_text(text, encoding="utf-8")
    (VERSIONS_DIR / f"plan_v{plan['version']:03d}.json").write_text(text, encoding="utf-8")


# ===========================================================================
# HUMAN EDITS (checkpoint 2): edit plan.json by hand, then run --check
# ===========================================================================

PLAN_HOW_TO_EDIT = (
    "You may edit ONLY these text fields inside each item: "
    + ", ".join(config.PLAN_HUMAN_EDITABLE_FIELDS) + ". "
    "Facts (fact_ids), dates, platforms and lengths cannot be edited here. "
    "To change dates or the number of posts, edit and re-approve the schedule "
    "(cadence.json), then regenerate. To change facts, regenerate with --feedback. "
    "When you are done editing, run: py pipeline1/plan.py --check"
)


def load_latest_version():
    """The newest saved version file as a dict, or None if there is none."""
    if not VERSIONS_DIR.exists():
        return None
    files = sorted(VERSIONS_DIR.glob("plan_v*.json"),
                   key=lambda p: int(p.stem.split("_v")[-1]))
    return load_json_file(files[-1]) if files else None


def has_unsaved_edits(plan: dict) -> bool:
    """
    True if plan.json differs from the newest saved version, meaning someone
    edited it by hand and has not run --check yet.
    """
    base = load_latest_version()
    return base is not None and plan != base


def validate_human_edit(edited: dict, base: dict, banned: list) -> list:
    """
    Compare a hand-edited plan against the last saved version.
    Returns a list of problems (empty list = the edits are allowed).
    """
    errors = []
    editable = config.PLAN_HUMAN_EDITABLE_FIELDS

    # 1. Everything outside "items" must be untouched.
    for key in (set(base) | set(edited)) - {"items", "_how_to_edit"}:
        if edited.get(key) != base.get(key):
            errors.append(f"'{key}' was changed, but only item text fields can be edited by hand")

    # 2. The set of posts must be the same (no adding, removing or renaming).
    raw_items = edited.get("items")
    if not isinstance(raw_items, list):
        return errors + ["'items' is missing or not a list"]
    base_by_id = {i["item_id"]: i for i in base["items"]}
    ids = [i.get("item_id") for i in raw_items if isinstance(i, dict)]
    if len(ids) != len(raw_items) or sorted(map(str, ids)) != sorted(base_by_id):
        errors.append("posts were added, removed, duplicated or renamed. The number of "
                      "posts comes from the schedule (cadence.json), so change it there")
        return errors

    # 3. Check each post.
    for item in raw_items:
        label = item["item_id"]
        old = base_by_id[label]

        # Locked fields must be identical to the saved version.
        for key in (set(old) | set(item)) - set(editable):
            if item.get(key) != old.get(key):
                errors.append(f"{label}: '{key}' can't be edited by hand")

        # Editable fields must still be non-empty text.
        for field in editable:
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{label}: '{field}' must be non-empty text")

        # Edited text must not use a forbidden brand term.
        bad = find_banned(" ".join(str(item.get(f, "")) for f in editable), banned)
        if bad:
            errors.append(f"{label}: uses the forbidden term '{bad}'")
    return errors


def mode_check(campaign, client, extracted):
    """Validate hand edits in plan.json and save them as a new version."""
    plan = load_current_plan()
    base = load_latest_version()
    if not plan or not base:
        raise SystemExit("[ERROR] No plan yet. Run: py pipeline1/plan.py")

    if plan == base:
        print(f"[OK] No unsaved edits. Current plan is v{plan['version']} "
              f"(status: {plan['status']}).")
        return

    if base.get("locked"):
        raise SystemExit(f"[ERROR] Plan v{base['version']} is approved and locked, so edits "
                         "can't be saved.")

    errors = validate_human_edit(plan, base, compile_banned(client))
    if errors:
        print("[PROBLEMS] Fix these in plan.json, then run --check again:")
        for error in errors:
            print(f"  - {error}")
        return

    # Which posts did the human actually change?
    base_by_id = {i["item_id"]: i for i in base["items"]}
    fields = config.PLAN_HUMAN_EDITABLE_FIELDS
    changed = [i["item_id"] for i in plan["items"]
               if any(i[f] != base_by_id[i["item_id"]][f] for f in fields)]

    # Save as a NEW draft version (old versions are never touched).
    for item in plan["items"]:
        for f in fields:
            item[f] = item[f].strip()
    new_plan = dict(plan)
    for key in ("reject_reason", "rejected_at"):   # a rejected plan edited = fresh draft
        new_plan.pop(key, None)
    new_plan.update(
        _how_to_edit=PLAN_HOW_TO_EDIT,
        version=next_version_number(), status="draft", locked=False,
        created_at=datetime.now().isoformat(timespec="seconds"),
        created_by="human", feedback=None, regenerated=[],
        edited_items=changed, based_on_version=base["version"],
        warnings=whole_plan_warnings(plan["items"], campaign, extracted["facts"]),
    )
    write_plan(new_plan)
    print(f"[OK] Your edits are saved as plan v{new_plan['version']} (draft). "
          f"Edited posts: {', '.join(changed)}")
    print_plan(new_plan, campaign)


def print_plan(plan: dict, campaign: dict) -> None:
    lock = "  (LOCKED)" if plan.get("locked") else ""
    print(f"\nPlan v{plan['version']}  |  status: {plan['status']}{lock}")
    print(f"\nSummary: {plan['summary']}\nClosing CTA: {plan['campaign_cta']}\n\nWeekly themes:")
    for t in plan["weekly_themes"]:
        start, end = week_range(t["week"], campaign)
        print(f"  Week {t['week']} ({start} to {end}): {t['theme']}")
    print(f"\nPosts ({len(plan['items'])}):")
    for i in plan["items"]:
        print(f"\n  {i['item_id']} | {i['date']} {i['weekday']} | {i['platform']} | {i['length']}")
        print(f"      Topic:   {i['topic']}")
        print(f"      Message: {i['key_message']}")
        print(f"      Facts: {', '.join(i['fact_ids'])}   CTA: {i['cta']}   Format: {i['format_note']}")
    for warning in plan.get("warnings", []):
        print(f"\n  [WARN] {warning}")


# ===========================================================================
# PART 5: THE COMMANDS
# ===========================================================================

def mode_generate(campaign, client, extracted, feedback, only, force=False):
    cadence = load_approved_cadence(campaign)
    current = load_current_plan()
    if current and current.get("locked"):
        raise SystemExit(f"[ERROR] Plan v{current['version']} is approved and locked.")

    if current and not force and has_unsaved_edits(current):
        raise SystemExit("[ERROR] plan.json has edits that are not saved as a version yet.\n"
                         "        Run:  py pipeline1/plan.py --check   (validates and saves them)\n"
                         "        Or add --force to throw the edits away and regenerate anyway.")

    slots = build_slots(cadence, campaign)
    whole = not only

    if whole:
        target, kept = slots, []
    else:
        # Regenerating only some posts needs an existing plan on the SAME schedule.
        if not current:
            raise SystemExit("[ERROR] There is no plan yet. Run without --only first.")
        if signature(current["items"]) != signature(slots):
            raise SystemExit("[ERROR] The schedule changed since this plan was made, so single "
                             "posts can't be redone. Run without --only to regenerate everything.")
        unknown = [s for s in only if s not in {x["slot_id"] for x in slots}]
        if unknown:
            raise SystemExit(f"[ERROR] Unknown post id(s): {', '.join(unknown)}")
        target = [s for s in slots if s["slot_id"] in only]
        kept = [i for i in current["items"] if i["item_id"] not in only]

    ctx = {
        "fact_ids": {f["id"] for f in extracted["facts"]},
        "angle_ids": {a["id"] for a in extracted["angles"]},
        "banned": compile_banned(client),
        "weeks_needed": sorted({s["week"] for s in target}),
    }
    user_prompt = build_prompt(campaign, client, extracted, target, kept,
                               feedback, current, whole, ctx["weeks_needed"])
    system_prompt = load_prompt("planner_system.txt")

    print(f"Planning {len(target)} post(s)" + ("" if whole else f" (keeping {len(kept)} as they are)") + "...")
    header, new_items = call_with_retries(
        user_prompt, system_prompt, lambda r: process_reply(r, target, whole, ctx))

    # Whole run: new header. Partial run: keep the old header.
    if header is None:
        header = {k: current[k] for k in ("summary", "campaign_cta", "weekly_themes")}
    items = sorted(kept + new_items, key=lambda i: i["item_id"])

    plan = {
        "_how_to_edit": PLAN_HOW_TO_EDIT,
        "version": next_version_number(),
        "status": "draft",
        "locked": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "created_by": "ai",
        "feedback": feedback or None,
        "regenerated": "all" if whole else sorted(only),
        "based_on_version": current["version"] if current else None,
        "campaign": {"name": campaign["name"], "start_date": campaign["start_date"],
                     "end_date": campaign["end_date"]},
        "cadence_approved_at": cadence.get("approved_at"),
        **header,
        "items": items,
        "warnings": whole_plan_warnings(items, campaign, extracted["facts"]),
    }
    write_plan(plan)
    print(f"\n[OK] Saved plan v{plan['version']} (draft). Earlier versions are kept in {VERSIONS_DIR.name}/")
    print_plan(plan, campaign)
    print("\nNEXT: review the plan, then one of:\n"
          "  EDIT   open data/output/plan.json, change topic / key_message / cta / format_note,\n"
          "         then run:  py pipeline1/plan.py --check\n"
          '  REDO   py pipeline1/plan.py --feedback "what to change"\n'
          '  REDO A FEW   py pipeline1/plan.py --only p03 --feedback "what to change"\n'
          '  APPROVE   py pipeline1/plan.py --approve --by "Your Name"\n'
          '  REJECT   py pipeline1/plan.py --reject "reason"')


def mode_show(campaign):
    plan = load_current_plan()
    if not plan:
        raise SystemExit("[ERROR] No plan yet. Run: py pipeline1/plan.py")
    print_plan(plan, campaign)


def mode_approve(campaign, by):
    plan = load_current_plan()
    if not plan:
        raise SystemExit("[ERROR] No plan to approve.")
    if has_unsaved_edits(plan):
        raise SystemExit("[ERROR] plan.json has unsaved edits. Run --check first "
                         "(it validates and saves them), then approve.")
    if plan["status"] == "approved":
        raise SystemExit(f"[INFO] Plan v{plan['version']} is already approved.")
    plan.update(status="approved", locked=True, approved_by=by,
                approved_at=datetime.now().isoformat(timespec="seconds"))
    write_plan(plan)   # updates plan.json and this version's own file
    print(f"[OK] Plan v{plan['version']} approved by {by} and locked.")


def mode_reject(reason):
    plan = load_current_plan()
    if not plan:
        raise SystemExit("[ERROR] No plan to reject.")
    if has_unsaved_edits(plan):
        raise SystemExit("[ERROR] plan.json has unsaved edits. Run --check first "
                         "(it validates and saves them), then approve.")
    if plan.get("locked"):
        raise SystemExit("[ERROR] An approved plan is locked and cannot be rejected.")
    if not reason.strip():
        raise SystemExit("[ERROR] A rejection needs a written reason.")
    plan.update(status="rejected", reject_reason=reason.strip(),
                rejected_at=datetime.now().isoformat(timespec="seconds"))
    write_plan(plan)
    print(f"[OK] Plan v{plan['version']} rejected. Generate a new one when ready.")


def main():
    parser = argparse.ArgumentParser(description="Generate, review and approve the campaign plan.")
    parser.add_argument("--feedback", default="", help="tell the AI what to change")
    parser.add_argument("--only", nargs="+", metavar="POST_ID", help="regenerate only these posts, e.g. p03 p05")
    parser.add_argument("--show", action="store_true", help="print the current plan")
    parser.add_argument("--check", action="store_true", help="validate your hand edits in plan.json and save them as a new version")
    parser.add_argument("--force", action="store_true", help="regenerate even if plan.json has unsaved edits (they are discarded)")
    parser.add_argument("--approve", action="store_true", help="approve and lock the current plan")
    parser.add_argument("--by", default="demo-reviewer", help="who is approving (used with --approve)")
    parser.add_argument("--reject", metavar="REASON", help="reject the current plan (reason required)")
    args = parser.parse_args()

    if args.reject is not None:
        mode_reject(args.reject)
        return

    campaign_file = load_json_file(CAMPAIGN_FILE)
    campaign, client = campaign_file["campaign"], campaign_file["client"]

    if args.show:
        mode_show(campaign)
    elif args.approve:
        mode_approve(campaign, args.by)
    elif args.check:
        mode_check(campaign, client, load_json_file(EXTRACTED_FILE))
    else:
        extracted = load_json_file(EXTRACTED_FILE)
        mode_generate(campaign, client, extracted, args.feedback, args.only, args.force)


if __name__ == "__main__":
    main()