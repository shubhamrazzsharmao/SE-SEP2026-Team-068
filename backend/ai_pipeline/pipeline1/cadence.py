"""
cadence.py  --  Pipeline 1, step 5a: THE POSTING SCHEDULE ("CADENCE")

JOB: the AI proposes how many posts each platform gets and on which dates.
     A human can then edit the dates in a JSON file and APPROVE the schedule.
     Only an approved schedule can be turned into a plan (that is plan.py,
     the next step).

WHAT A HUMAN MAY EDIT: only the number of posts per platform and their dates.
     (To change anything else, regenerate with --feedback.)

FOUR WAYS TO RUN IT (from the mosaic_ai folder):
  py pipeline1/cadence.py                      AI proposes a schedule
  py pipeline1/cadence.py --feedback "text"    AI proposes again, using your feedback
  py pipeline1/cadence.py --check              check your edited file, show the calendar
  py pipeline1/cadence.py --approve            check, then lock in the schedule

INPUT : data/campaign_input.json, prompts/cadence_*.txt
OUTPUT: data/output/cadence.json
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS + IMPORTS (same pattern as the other pipeline scripts)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN_FILE = PROJECT_ROOT / "data" / "campaign_input.json"
CADENCE_FILE = PROJECT_ROOT / "data" / "output" / "cadence.json"
RAW_REPLY_FILE = PROJECT_ROOT / "data" / "output" / "cadence_raw_reply.txt"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

sys.path.insert(0, str(PROJECT_ROOT))
import config  # noqa: E402
from llm import call_llm, parse_json_response  # noqa: E402

ROLE = "cadence"   # the actual model is chosen in config.py
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# Written into cadence.json so anyone opening the file knows the rules.
HOW_TO_EDIT = (
    "You may edit ONLY the dates under each platform. "
    "To add a post, add a date (YYYY-MM-DD) to that platform's list. "
    "To remove a post, delete its date. "
    "To remove a platform completely, delete its whole entry. "
    f"The total across all platforms must not exceed {config.PLAN_MAX_POSTS}. "
    "Then run: py pipeline1/cadence.py --check   and   py pipeline1/cadence.py --approve"
)


# ===========================================================================
# SMALL HELPERS
# ===========================================================================

def load_json_file(path: Path) -> dict:
    """Read a JSON file. If a human made a typo, explain WHERE instead of crashing."""
    if not path.exists():
        raise SystemExit(f"[ERROR] File not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"[ERROR] {path.name} is not valid JSON (line {error.lineno}): {error.msg}\n"
            "        Common causes: a missing comma between items, a comma after "
            "the LAST item in a list, or a missing quote.")


def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise SystemExit(f"[ERROR] Prompt file missing: {path}")
    return path.read_text(encoding="utf-8")


def fill(template: str, values: dict) -> str:
    """Replace every {{PLACEHOLDER}} in a template with its value."""
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


def parse_date(text):
    """Turn 'YYYY-MM-DD' into a date, or None if it is not a valid date."""
    try:
        return date.fromisoformat(str(text))
    except ValueError:
        return None


def save_cadence(cadence: dict) -> None:
    CADENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CADENCE_FILE.write_text(json.dumps(cadence, indent=2, ensure_ascii=False),
                            encoding="utf-8")


# ===========================================================================
# CHECKING A SCHEDULE (used for AI output AND for human edits)
# ===========================================================================

def validate_cadence(cadence: dict, campaign: dict) -> list:
    """
    Check a schedule against the hard rules. Returns a list of error messages
    (an empty list means the schedule is valid).
    """
    errors = []
    start = date.fromisoformat(campaign["start_date"])
    end = date.fromisoformat(campaign["end_date"])
    allowed_platforms = [p.lower() for p in campaign["platforms"]]

    platforms = cadence.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        return ["'platforms' is missing or empty"]

    total = 0
    for name, entry in platforms.items():
        if name not in allowed_platforms:
            errors.append(f"'{name}' is not a campaign platform "
                          f"(allowed: {', '.join(allowed_platforms)}, lowercase)")
            continue
        if not isinstance(entry, dict):
            errors.append(f"{name}: should be an object with length and dates")
            continue

        options = config.LENGTH_OPTIONS.get(name, {})
        if entry.get("length") not in options:
            errors.append(f"{name}: length must be one of: {', '.join(options)}")

        dates = entry.get("dates")
        if not isinstance(dates, list) or not dates:
            errors.append(f"{name}: needs at least one date "
                          "(delete the platform if it should get no posts)")
            continue
        if len(set(dates)) != len(dates):
            errors.append(f"{name}: the same date is listed twice")

        for d in dates:
            parsed = parse_date(d)
            if parsed is None:
                errors.append(f"{name}: '{d}' is not a valid date (use YYYY-MM-DD)")
            elif not (start <= parsed <= end):
                errors.append(f"{name}: {d} is outside the campaign ({start} to {end})")
        total += len(dates)

    if total > config.PLAN_MAX_POSTS:
        errors.append(f"{total} posts is over the limit of {config.PLAN_MAX_POSTS}")
    return errors


def cadence_warnings(cadence: dict, campaign: dict) -> list:
    """Things worth a look, but not errors."""
    warnings = []
    used_dates = {d for e in cadence["platforms"].values() for d in e.get("dates", [])}
    for key_date in campaign.get("key_dates", []):
        if key_date["date"] not in used_dates:
            warnings.append(f"No post on key date {key_date['date']} ({key_date['event']})")
    for platform in campaign["platforms"]:
        if platform.lower() not in cadence["platforms"]:
            warnings.append(f"Platform '{platform}' has no posts")
    return warnings


# ===========================================================================
# THE CALENDAR (also imported by plan.py in the next step)
# ===========================================================================

def build_calendar(cadence: dict, campaign: dict) -> list:
    """
    Turn an approved schedule into one row per post:
      {"date": "2027-01-11", "weekday": "mon", "platform": "instagram", "length": "short"}
    Sorted by date, then by the platform order in campaign_input.json.
    """
    order = [p.lower() for p in campaign["platforms"]]
    rows = []
    for name, entry in cadence["platforms"].items():
        for d in entry["dates"]:
            rows.append({"date": d,
                         "weekday": DAY_NAMES[date.fromisoformat(d).weekday()],
                         "platform": name,
                         "length": entry["length"]})
    rows.sort(key=lambda r: (r["date"], order.index(r["platform"])))
    return rows


def print_calendar(rows: list, campaign: dict) -> None:
    key_dates = {k["date"]: k["event"] for k in campaign.get("key_dates", [])}
    print(f"\n  {'#':>2}  {'date':<11} {'day':<4} {'platform':<10} {'length':<9}")
    for number, row in enumerate(rows, start=1):
        note = f"   <- {key_dates[row['date']]}" if row["date"] in key_dates else ""
        print(f"  {number:>2}  {row['date']:<11} {row['weekday']:<4} "
              f"{row['platform']:<10} {row['length']:<9}{note[:60]}")
    print(f"\n  Total: {len(rows)} post(s)  (limit {config.PLAN_MAX_POSTS})")


# ===========================================================================
# BUILDING THE PROMPT
# ===========================================================================

def fmt_campaign(c: dict) -> str:
    goals = "\n".join(f"- {g}" for g in c["goals"])
    return (f"Campaign name: {c['name']}\n"
            f"Theme: {c['theme']}\n"
            f"Target audience: {c['target_audience']}\n"
            f"Dates: {c['start_date']} to {c['end_date']}\n"
            f"Goals:\n{goals}")


def fmt_platform_lengths(c: dict) -> str:
    lines = []
    for platform in c["platforms"]:
        options = config.LENGTH_OPTIONS.get(platform.lower(), {})
        text = "; ".join(f"{name} = {meaning}" for name, meaning in options.items())
        lines.append(f"{platform.lower()}: {text}")
    return "\n".join(lines)


def fmt_key_dates(c: dict) -> str:
    return "\n".join(f"- {k['date']}: {k['event']}" for k in c.get("key_dates", [])) or "(none)"


def fmt_available_dates(c: dict) -> str:
    start = date.fromisoformat(c["start_date"])
    end = date.fromisoformat(c["end_date"])
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    return "\n".join(f"{d.isoformat()} ({DAY_NAMES[d.weekday()]})" for d in days)


def fmt_cadence(cadence: dict) -> str:
    return "\n".join(
        f"{name} ({entry.get('length')}): {', '.join(entry.get('dates', []))}"
        for name, entry in cadence.get("platforms", {}).items())


# ===========================================================================
# ASKING THE AI
# ===========================================================================

def process_reply(reply: str, campaign: dict) -> dict:
    """Parse the AI's reply and check it. Raises ValueError if unusable."""
    data = parse_json_response(reply)
    raw_platforms = data.get("platforms")
    if not isinstance(raw_platforms, dict):
        raise ValueError("'platforms' is missing or not an object")

    platforms = {}
    for name, entry in raw_platforms.items():
        if not isinstance(entry, dict):
            raise ValueError(f"'{name}' should be an object")
        dates = entry.get("dates", [])
        if not isinstance(dates, list):
            raise ValueError(f"'{name}': dates should be a list")
        if not dates:
            continue   # a platform with no dates simply gets no posts
        platforms[name.strip().lower()] = {
            "length": entry.get("length"),
            "dates": sorted(set(str(d) for d in dates)),
            "reason": str(entry.get("reason", "")).strip(),
        }

    # Key order here is the order the keys appear in the saved file.
    cadence = {
        "_how_to_edit": HOW_TO_EDIT,
        "approved": False,   # a human must approve it, with --approve
        "summary": str(data.get("summary", "")).strip(),
        "platforms": platforms,
    }
    errors = validate_cadence(cadence, campaign)
    if errors:
        raise ValueError("; ".join(errors))
    return cadence


def propose(campaign: dict, feedback: str, previous) -> dict:
    """Ask the AI for a schedule, retrying (with the reasons) if it breaks a rule."""
    if feedback:
        feedback_block = ("=== HUMAN FEEDBACK (follow this) ===\n" + feedback)
        if previous:
            feedback_block += ("\n\nThe previous proposal was:\n" + fmt_cadence(previous))
    else:
        feedback_block = "(This is the first proposal. There is no feedback yet.)"

    system_prompt = load_prompt("cadence_system.txt")
    user_prompt = fill(load_prompt("cadence_user.txt"), {
        "CAMPAIGN_CONTEXT": fmt_campaign(campaign),
        "MAX_POSTS": config.PLAN_MAX_POSTS,
        "PLATFORM_LENGTHS": fmt_platform_lengths(campaign),
        "KEY_DATES": fmt_key_dates(campaign),
        "AVAILABLE_DATES": fmt_available_dates(campaign),
        "FEEDBACK_BLOCK": feedback_block,
    })

    extra = ""
    for attempt in range(1, config.CADENCE_MAX_ATTEMPTS + 1):
        print(f"[Attempt {attempt}/{config.CADENCE_MAX_ATTEMPTS}] asking role '{ROLE}'...")
        reply = call_llm(ROLE, user_prompt + extra, system_prompt, json_mode=True)

        # Save the raw reply every time, in case you need to inspect it.
        RAW_REPLY_FILE.parent.mkdir(parents=True, exist_ok=True)
        RAW_REPLY_FILE.write_text(reply, encoding="utf-8")

        try:
            return process_reply(reply, campaign)
        except ValueError as error:   # also catches broken JSON
            print(f"   [RETRY] Rejected: {error}")
            extra = ("\n\n=== YOUR PREVIOUS ANSWER WAS REJECTED ===\n"
                     f"Reason: {error}\n"
                     "Fix this and answer again with the complete JSON.")

    raise SystemExit(f"[FAILED] No valid schedule after {config.CADENCE_MAX_ATTEMPTS} "
                     f"attempts. Last raw reply: {RAW_REPLY_FILE}")


# ===========================================================================
# THE FOUR MODES
# ===========================================================================

def show(cadence: dict, campaign: dict) -> None:
    """Print a schedule: summary, reasons, calendar, warnings."""
    if cadence.get("summary"):
        print(f"\nSummary: {cadence['summary']}")
    for name, entry in cadence["platforms"].items():
        if entry.get("reason"):
            print(f"  {name}: {entry['reason']}")
    print_calendar(build_calendar(cadence, campaign), campaign)
    for warning in cadence_warnings(cadence, campaign):
        print(f"  [WARN] {warning}")


def mode_propose(campaign: dict, feedback: str) -> None:
    previous = None
    if CADENCE_FILE.exists():
        try:
            previous = json.loads(CADENCE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = None   # a broken old file is simply ignored

    cadence = propose(campaign, feedback, previous)
    save_cadence(cadence)
    print(f"\n[OK] Proposed schedule saved to {CADENCE_FILE}")
    show(cadence, campaign)
    print("\nNEXT: edit the dates in cadence.json if you like, then run\n"
          "      py pipeline1/cadence.py --check\n"
          "      py pipeline1/cadence.py --approve")


def mode_check(campaign: dict) -> None:
    cadence = load_json_file(CADENCE_FILE)
    errors = validate_cadence(cadence, campaign)
    if errors:
        print("[PROBLEMS] Fix these in cadence.json, then run --check again:")
        for error in errors:
            print(f"  - {error}")
        return
    print(f"[OK] Schedule is valid. Approved: {cadence.get('approved', False)}")
    show(cadence, campaign)


def mode_approve(campaign: dict) -> None:
    cadence = load_json_file(CADENCE_FILE)
    errors = validate_cadence(cadence, campaign)
    if errors:
        print("[NOT APPROVED] Fix these in cadence.json first:")
        for error in errors:
            print(f"  - {error}")
        return
    cadence["approved"] = True
    cadence["approved_at"] = datetime.now().isoformat(timespec="seconds")
    save_cadence(cadence)
    print("[OK] Schedule approved. plan.py can now build the plan from it.")
    show(cadence, campaign)


def main():
    parser = argparse.ArgumentParser(description="Propose, check or approve the posting schedule.")
    parser.add_argument("--feedback", help="tell the AI what to change in the proposal")
    parser.add_argument("--check", action="store_true", help="validate cadence.json and show the calendar")
    parser.add_argument("--approve", action="store_true", help="validate and approve cadence.json")
    args = parser.parse_args()

    campaign = load_json_file(CAMPAIGN_FILE)["campaign"]

    if args.approve:
        mode_approve(campaign)
    elif args.check:
        mode_check(campaign)
    else:
        mode_propose(campaign, args.feedback or "")


if __name__ == "__main__":
    main()