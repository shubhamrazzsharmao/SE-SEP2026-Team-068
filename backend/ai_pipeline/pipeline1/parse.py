"""
parse.py  --  Pipeline 1, step 3a: PARSING

JOB: take each uploaded document and turn it into plain text.
     No cleaning here (that is the next script), and no AI at all.

INPUT : data/campaign_input.json      (lists which documents to read)
OUTPUT: data/output/parsed_documents.json

RUN   : from the mosaic_ai folder ->  python pipeline1/parse.py
"""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# We build every path from the location of THIS file, so the script works no
# matter which folder you run it from.
# parse.py lives in mosaic_ai/pipeline1/, so .parent.parent = mosaic_ai/
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "campaign_input.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "parsed_documents.json"


# ---------------------------------------------------------------------------
# ONE PARSER PER FILE TYPE
# Each parser returns a list of "sections". A section is a dict:
#     {"label": "page_1", "text": "...text of that page..."}
# We keep the label so that later, a fact can point back to where it came from.
# ---------------------------------------------------------------------------

def parse_txt(path: Path) -> list:
    """Read a plain text file. Returns one section holding the whole text."""
    # Text files can be saved in different encodings. We try the common ones
    # in order. 'utf-8-sig' also handles the invisible BOM character that
    # Windows Notepad sometimes adds at the start of a file.
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = path.read_text(encoding=encoding)
            return [{"label": "full_text", "text": text}]
        except UnicodeDecodeError:
            continue  # wrong encoding, try the next one
    raise ValueError(f"Could not decode text file: {path.name}")


def parse_pdf(path: Path) -> list:
    """Read a PDF page by page. Needs:  pip install pypdf  (not needed for the demo)."""
    # Imported here (not at the top) so the demo runs even if pypdf is not
    # installed. It only matters when a PDF is actually uploaded.
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    sections = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""  # a page with no text gives ""
        sections.append({"label": f"page_{page_number}", "text": text})

    # If every page is empty, this is probably a scanned PDF (just images).
    # Reading those needs OCR, which we are not doing yet, so fail clearly.
    if not any(s["text"].strip() for s in sections):
        raise ValueError(f"No text found in {path.name} (scanned PDF? needs OCR)")
    return sections


def parse_docx(path: Path) -> list:
    """Read a Word file. Needs:  pip install python-docx  (not needed for the demo)."""
    from docx import Document

    document = Document(str(path))
    # Join all paragraphs with a newline between them.
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return [{"label": "full_text", "text": text}]


# Which parser handles which file extension.
# To support a new format later, write a parse_xxx function and add one line here.
PARSERS = {
    ".txt": parse_txt,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
}


# ---------------------------------------------------------------------------
# PARSE ONE DOCUMENT
# ---------------------------------------------------------------------------

def parse_document(path: Path) -> dict:
    """Pick the right parser by extension and return a standard result dict."""
    extension = path.suffix.lower()  # e.g. ".txt"

    if extension not in PARSERS:
        supported = ", ".join(PARSERS)
        raise ValueError(f"Unsupported file type '{extension}'. Supported: {supported}")

    sections = PARSERS[extension](path)

    # Also keep the whole text joined together, for convenience in later steps.
    raw_text = "\n\n".join(s["text"] for s in sections)

    return {
        "file": path.name,
        "file_type": extension,
        "sections": sections,
        "raw_text": raw_text,
        "char_count": len(raw_text),
    }


# ---------------------------------------------------------------------------
# MAIN: parse every document listed in campaign_input.json
# ---------------------------------------------------------------------------

def main():
    # 1. Load the campaign settings file.
    with open(INPUT_FILE, encoding="utf-8") as f:
        campaign_input = json.load(f)

    parsed_documents = []

    # 2. Go through each document listed in the input.
    for doc in campaign_input["documents"]:
        # Paths in the JSON are relative to the project root.
        doc_path = PROJECT_ROOT / doc["file"]

        # A missing file should not crash the whole run: warn and move on.
        if not doc_path.exists():
            print(f"[WARN] File not found, skipping: {doc_path}")
            continue

        # Same idea for a file that fails to parse (bad format, scanned PDF...).
        try:
            result = parse_document(doc_path)
        except Exception as error:
            print(f"[WARN] Could not parse {doc_path.name}: {error}")
            continue

        # Keep the document type from the input file (e.g. "launch_brief").
        result["doc_type"] = doc.get("type", "unknown")
        parsed_documents.append(result)
        print(f"[OK] Parsed {result['file']}: {result['char_count']} characters, "
              f"{len(result['sections'])} section(s)")

    # 3. Save the output. parents=True creates data/output/ if it is missing.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(parsed_documents, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(parsed_documents)} document(s) to {OUTPUT_FILE}")


# This block runs main() only when you run the file directly,
# not when another script imports parse_document from it.
if __name__ == "__main__":
    main()