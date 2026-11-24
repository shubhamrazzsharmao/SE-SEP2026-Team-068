"""
clean.py  --  Pipeline 1, step 3b: CLEANING

JOB: take the raw parsed text and remove everything that is not real content,
     so the AI never sees junk like cookie banners or page numbers.
     Plain code, no AI.

INPUT : data/output/parsed_documents.json    (made by parse.py)
OUTPUT: data/output/cleaned_documents.json

RUN   : from the mosaic_ai folder ->  py pipeline1/clean.py
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS (built from this file's location, same idea as parse.py)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "output" / "parsed_documents.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "cleaned_documents.json"


# ---------------------------------------------------------------------------
# SETTINGS YOU CAN EDIT
# ---------------------------------------------------------------------------

# A line is thrown away if it matches ANY of these patterns (case-insensitive).
# To catch a new kind of junk later, just add one more line to this list.
JUNK_LINE_PATTERNS = [
    r"^page\s+\d+\s+of\s+\d+$",        # "Page 1 of 3"
    r"^page\s+\d+$",                    # "Page 4"
    r"^we use cookies",                 # cookie banner
    r"^(accept all|manage settings)",   # cookie buttons
    r"all rights reserved",             # footer text
    r"^\(c\)\s*\d{4}",                  # "(c) 2026 ..." copyright line
    r"^\u00a9",                         # the (c) symbol at the start of a line
]

# Odd characters replaced with plain ones. Documents copied from Word or a
# website often contain "smart" quotes and invisible characters that confuse
# later steps.
CHAR_REPLACEMENTS = {
    "\u2018": "'",   # curly single quote (left)
    "\u2019": "'",   # curly single quote (right)
    "\u201c": '"',   # curly double quote (left)
    "\u201d": '"',   # curly double quote (right)
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u00a0": " ",   # non-breaking space
    "\u200b": "",    # zero-width space (invisible)
    "\ufeff": "",    # byte order mark (invisible)
}

# ---------------------------------------------------------------------------
# PRE-COMPILED PATTERNS (compiling once makes the loops below faster)
# ---------------------------------------------------------------------------
JUNK_REGEXES = [re.compile(p, re.IGNORECASE) for p in JUNK_LINE_PATTERNS]

# A heading looks like "1. ABOUT BREWLEAF": a number, a dot, then CAPITAL text.
HEADING_REGEX = re.compile(r"^\d+\.\s+[A-Z][A-Z0-9 :,&'/()-]*$")

# A list item starts with "- ", "* " or a bullet dot.
LIST_ITEM_REGEX = re.compile(r"^(?:[-*]|\u2022)\s+")


# ---------------------------------------------------------------------------
# CLEANING STEPS (each does one small job; clean_text() runs them in order)
# ---------------------------------------------------------------------------

def normalize_characters(text: str) -> str:
    """Make line endings consistent and swap odd characters for plain ones."""
    # Windows files end lines with \r\n, old Macs with \r. Make all of them \n.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for odd, plain in CHAR_REPLACEMENTS.items():
        text = text.replace(odd, plain)
    return text


def remove_junk_lines(text: str):
    """
    Drop any line that matches a junk pattern.
    Returns (text_without_junk, list_of_removed_lines).
    We return the removed lines so main() can print them for you to review.
    """
    kept_lines = []
    removed_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Only non-empty lines can be junk (empty lines are handled later).
        if stripped and any(rx.search(stripped) for rx in JUNK_REGEXES):
            removed_lines.append(stripped)
        else:
            kept_lines.append(line)
    return "\n".join(kept_lines), removed_lines


def rebuild_paragraphs(text: str) -> str:
    """
    Fix broken line wraps and tidy blank lines.

    Raw text often wraps in the middle of a sentence:
        "...founded in 2019 in Pune,\\nIndia by two friends..."
    We glue those lines back into one line. We read the text line by line and
    build 'blocks' of three kinds:
        heading   -> its own block, never merged with anything
        list      -> starts at "- ", and wrapped continuation lines join it
        paragraph -> consecutive lines are glued together with a space
    A blank line always ends the current block.
    """
    blocks = []      # finished blocks, in order: {"kind": ..., "text": ...}
    current = None   # the block we are currently adding lines to

    for line in text.split("\n"):
        # Collapse runs of spaces/tabs into one space and trim the ends.
        line = re.sub(r"[ \t]+", " ", line).strip()

        if not line:
            # Blank line: the current block is finished.
            current = None
        elif HEADING_REGEX.match(line):
            blocks.append({"kind": "heading", "text": line})
            current = None
        elif LIST_ITEM_REGEX.match(line):
            current = {"kind": "list", "text": line}
            blocks.append(current)
        elif current is not None:
            # Continuation of a wrapped line: glue it onto the current block.
            current["text"] += " " + line
        else:
            current = {"kind": "paragraph", "text": line}
            blocks.append(current)

    # Join the blocks back into text:
    #   one blank line between blocks,
    #   but list items that follow each other stay on neighbouring lines.
    pieces = []
    for i, block in enumerate(blocks):
        if i > 0:
            both_list = block["kind"] == "list" and blocks[i - 1]["kind"] == "list"
            pieces.append("\n" if both_list else "\n\n")
        pieces.append(block["text"])
    return "".join(pieces)


def clean_text(raw: str):
    """Run all cleaning steps in order. Returns (clean_text, removed_lines)."""
    text = normalize_characters(raw)
    text, removed = remove_junk_lines(text)
    text = rebuild_paragraphs(text)
    return text, removed


# ---------------------------------------------------------------------------
# MAIN: clean every document produced by parse.py
# ---------------------------------------------------------------------------

def main():
    # 1. Load the parser output. If it is missing, parse.py has not been run.
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} not found. Run parse.py first.")
        return
    with open(INPUT_FILE, encoding="utf-8") as f:
        parsed_documents = json.load(f)

    cleaned_documents = []

    for doc in parsed_documents:
        all_removed = []
        cleaned_sections = []

        # 2. Clean each section separately (a PDF has one section per page).
        for section in doc["sections"]:
            text, removed = clean_text(section["text"])
            all_removed.extend(removed)
            # Skip sections that are empty after cleaning (e.g. a page that
            # only contained a footer).
            if text.strip():
                cleaned_sections.append({"label": section["label"], "text": text})

        # 3. Warn clearly if everything was removed.
        if not cleaned_sections:
            print(f"[WARN] {doc['file']} has no content left after cleaning, skipping")
            continue

        # 4. Rebuild the full text from the cleaned sections.
        full_text = "\n\n".join(s["text"] for s in cleaned_sections)

        cleaned_documents.append({
            "file": doc["file"],
            "file_type": doc["file_type"],
            "doc_type": doc.get("doc_type", "unknown"),
            "sections": cleaned_sections,
            "clean_text": full_text,
            "chars_before": doc["char_count"],
            "chars_after": len(full_text),
        })

        # 5. Print a report so you can SEE what was removed.
        print(f"[OK] {doc['file']}: {doc['char_count']} -> {len(full_text)} characters")
        print(f"     Removed {len(all_removed)} junk line(s):")
        for line in all_removed:
            # Shorten long lines so the terminal stays readable.
            shown = line if len(line) <= 70 else line[:67] + "..."
            print(f"       - {shown}")

    # 6. Save the result.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_documents, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(cleaned_documents)} document(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()