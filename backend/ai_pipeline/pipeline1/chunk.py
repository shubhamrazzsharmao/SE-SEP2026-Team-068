"""
chunk.py  --  Pipeline 1, step 3c: CHUNKING

JOB: cut the cleaned text into small, meaningful pieces ("chunks").
     Each chunk gets an ID and metadata, so later steps can point back to it.
     Plain code, no AI.

HOW IT SPLITS:
  1. Split the text at section headings ("1. ABOUT BREWLEAF", ...).
     A chunk never mixes two sections.
  2. Inside a section, pack paragraphs together until the chunk is full
     (CHUNK_MAX_WORDS in config.py), then start a new chunk.
  3. Every chunk begins with its section title, so the chunk still makes
     sense on its own when it is searched later.

INPUT : data/output/cleaned_documents.json    (made by clean.py)
OUTPUT: data/output/chunks.json

RUN   : from the mosaic_ai folder ->  py pipeline1/chunk.py
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "output" / "cleaned_documents.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "chunks.json"

# config.py lives in the project root, but when you run "py pipeline1/chunk.py"
# Python only looks inside the pipeline1 folder. This line tells Python to
# also look in the project root, so "import config" works.
sys.path.insert(0, str(PROJECT_ROOT))
import config  # noqa: E402  (our settings file)

# Same heading style that clean.py recognises: "1. SOME CAPITAL TITLE"
HEADING_REGEX = re.compile(r"^\d+\.\s+[A-Z][A-Z0-9 :,&'/()-]*$")


# ---------------------------------------------------------------------------
# SMALL HELPERS
# ---------------------------------------------------------------------------

def count_words(text: str) -> int:
    """Number of words in a piece of text."""
    return len(text.split())


def split_long_unit(unit: str, max_words: int) -> list:
    """
    A single paragraph can be longer than the whole chunk limit.
    Break such a paragraph into pieces that each fit, preferring sentence ends.
    """
    if count_words(unit) <= max_words:
        return [unit]

    # Split into sentences: cut after . ! or ? followed by whitespace.
    sentences = re.split(r"(?<=[.!?])\s+", unit)

    pieces = []
    current = []          # sentences collected for the piece being built
    current_words = 0
    for sentence in sentences:
        words = count_words(sentence)

        # Extreme case: ONE sentence is longer than the limit.
        # Cut it by raw word count, because there is no better place to cut.
        if words > max_words:
            if current:
                pieces.append(" ".join(current))
                current, current_words = [], 0
            sentence_words = sentence.split()
            for i in range(0, len(sentence_words), max_words):
                pieces.append(" ".join(sentence_words[i:i + max_words]))
            continue

        # Normal case: add the sentence if it fits, otherwise close the piece.
        if current and current_words + words > max_words:
            pieces.append(" ".join(current))
            current, current_words = [], 0
        current.append(sentence)
        current_words += words

    if current:
        pieces.append(" ".join(current))
    return pieces


def pack_units(units: list, max_words: int, overlap_words: int) -> list:
    """
    Pack paragraphs ("units") into chunk bodies without exceeding max_words.
    When a new chunk starts, it begins with the last few words of the
    previous chunk (the overlap).
    """
    # First make sure no single unit is bigger than the limit.
    expanded = []
    for unit in units:
        expanded.extend(split_long_unit(unit, max_words))

    bodies = []        # finished chunk bodies
    current = []       # units in the chunk being built
    current_words = 0

    for unit in expanded:
        words = count_words(unit)

        # If adding this unit would overflow the chunk, close the chunk.
        if current and current_words + words > max_words:
            body = "\n\n".join(current)
            bodies.append(body)

            # Start the next chunk with the tail of the one we just closed.
            current, current_words = [], 0
            if overlap_words > 0:
                tail = " ".join(body.split()[-overlap_words:])
                current.append(tail)
                current_words = count_words(tail)

        current.append(unit)
        current_words += words

    if current:
        bodies.append("\n\n".join(current))
    return bodies


def group_by_heading(text: str, default_title: str) -> list:
    """
    Walk through a document's text and group paragraphs under their heading.
    Returns a list of (title, [paragraph, paragraph, ...]).
    Text that appears before any heading goes under default_title.
    """
    groups = []
    title = default_title
    units = []

    # clean.py separated paragraphs with a blank line, so split on that.
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if HEADING_REGEX.match(block):
            # A new heading starts: save the previous group first.
            if units:
                groups.append((title, units))
            title = block
            units = []
        else:
            units.append(block)

    if units:
        groups.append((title, units))
    return groups


# ---------------------------------------------------------------------------
# CHUNK ONE DOCUMENT
# ---------------------------------------------------------------------------

def chunk_document(doc: dict, doc_number: int) -> list:
    """Turn one cleaned document into a list of chunk dicts."""
    chunks = []
    counter = 1  # numbers chunks within this document: 001, 002, ...

    # Go through each section (a PDF has one per page, a .txt has just one).
    for section in doc["sections"]:
        groups = group_by_heading(section["text"], default_title="(no heading)")

        for title, units in groups:
            bodies = pack_units(
                units,
                max_words=config.CHUNK_MAX_WORDS,
                overlap_words=config.CHUNK_OVERLAP_WORDS,
            )
            for body in bodies:
                # Put the section title at the top of the chunk text, so the
                # chunk carries its own context. Skip it if there was no heading.
                text = body if title == "(no heading)" else f"{title}\n\n{body}"

                chunks.append({
                    # Stable ID that later steps (and fact IDs) will point to.
                    "chunk_id": f"doc{doc_number}_c{counter:03d}",
                    "file": doc["file"],
                    "doc_type": doc["doc_type"],
                    "section_label": section["label"],   # e.g. "page_2"
                    "section_title": title,
                    "text": text,
                    "word_count": count_words(text),
                })
                counter += 1
    return chunks


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Load the cleaned documents. Missing file means clean.py was not run.
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} not found. Run clean.py first.")
        return
    with open(INPUT_FILE, encoding="utf-8") as f:
        cleaned_documents = json.load(f)

    all_chunks = []

    # 2. Chunk each document.
    for doc_number, doc in enumerate(cleaned_documents, start=1):
        chunks = chunk_document(doc, doc_number)
        all_chunks.extend(chunks)

        # 3. Print a report so you can SEE how the text was split.
        print(f"[OK] {doc['file']}: {len(chunks)} chunk(s)")
        for chunk in chunks:
            preview = chunk["text"].replace("\n", " ")[:60]
            print(f"     {chunk['chunk_id']}  {chunk['word_count']:>3} words  | {preview}...")

    # 4. Save the result.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(all_chunks)} chunk(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()