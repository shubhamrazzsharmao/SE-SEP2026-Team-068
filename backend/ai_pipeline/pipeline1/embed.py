"""
embed.py  --  Pipeline 1, step 3d: EMBEDDING

JOB: turn each chunk of text into a vector (a list of numbers that captures
     its meaning), and save it. Later steps use these vectors to find the
     chunks most relevant to a topic.
     Plain code, no LLM call. The model runs on your own laptop.

INPUT : data/output/chunks.json          (made by chunk.py)
OUTPUT: data/output/embeddings.json      (chunks + their vectors)

RUN   : from the mosaic_ai folder ->  py pipeline1/embed.py

This file also contains find_similar(), which later steps (AI B) will import
to look up the most relevant chunks for a topic.
"""

import json
import sys
from pathlib import Path

import numpy as np  # installed automatically together with sentence-transformers

# ---------------------------------------------------------------------------
# PATHS + CONFIG (same pattern as chunk.py)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "output" / "chunks.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "embeddings.json"

sys.path.insert(0, str(PROJECT_ROOT))
import config  # noqa: E402


# ---------------------------------------------------------------------------
# THE EMBEDDING MODEL
# ---------------------------------------------------------------------------

def load_model():
    """Load the embedding model chosen in config.py."""
    if config.EMBEDDING_PROVIDER != "local":
        # Only the local model is built so far. A hosted option can be added
        # here later without touching any other file.
        raise NotImplementedError(
            f"EMBEDDING_PROVIDER '{config.EMBEDDING_PROVIDER}' is not built yet. "
            "Set it to 'local' in config.py."
        )

    # Imported here (not at the top) so a missing install gives a clear message.
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit(
            "[ERROR] sentence-transformers is not installed.\n"
            "        Run:  pip install sentence-transformers"
        )

    print(f"Loading embedding model '{config.EMBEDDING_MODEL_NAME}' "
          "(first run downloads ~90 MB, please wait)...")
    return SentenceTransformer(config.EMBEDDING_MODEL_NAME)


def embed_texts(texts: list, model) -> np.ndarray:
    """
    Turn a list of texts into a 2D array: one row (vector) per text.

    normalize_embeddings=True scales every vector to length 1. That means
    "similarity between two texts" is just a dot product, which keeps the
    search code below very simple.
    """
    return model.encode(
        texts,
        batch_size=config.EMBEDDING_BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


# ---------------------------------------------------------------------------
# SEARCH (used by later steps, and by the sanity check at the bottom)
# ---------------------------------------------------------------------------

def find_similar(query: str, model, chunks: list, vectors: np.ndarray, top_k: int = 3):
    """
    Find the chunks whose meaning is closest to the query text.
    Returns a list of (score, chunk) pairs, best first.
    Score is between -1 and 1; higher means more similar.
    """
    query_vector = embed_texts([query], model)[0]

    # Dot product of the query with every chunk vector, in one go.
    scores = vectors @ query_vector

    # argsort gives indexes from lowest to highest, so reverse it and take top_k.
    best_indexes = np.argsort(scores)[::-1][:top_k]
    return [(float(scores[i]), chunks[i]) for i in best_indexes]


def load_embeddings():
    """
    Load embeddings.json back into memory (for later pipeline steps).
    Returns (chunks, vectors) where vectors is a numpy array.
    """
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    chunks = data["chunks"]
    vectors = np.array([c["embedding"] for c in chunks])
    return chunks, vectors


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Load the chunks. Missing file means chunk.py was not run.
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} not found. Run chunk.py first.")
        return
    with open(INPUT_FILE, encoding="utf-8") as f:
        chunks = json.load(f)
    if not chunks:
        print("[ERROR] chunks.json is empty, nothing to embed.")
        return

    # 2. Load the model and embed every chunk's text.
    model = load_model()
    vectors = embed_texts([c["text"] for c in chunks], model)
    print(f"[OK] Embedded {len(chunks)} chunk(s). "
          f"Each vector has {vectors.shape[1]} numbers.")

    # 3. Save. Each chunk keeps all its old fields, plus an "embedding" field.
    #    We also record WHICH model made the vectors, because vectors from
    #    different models cannot be compared.
    records = []
    for chunk, vector in zip(chunks, vectors):
        record = dict(chunk)
        record["embedding"] = np.round(vector, 6).tolist()  # rounded to keep the file small
        records.append(record)

    output = {
        "embedding_model": config.EMBEDDING_MODEL_NAME,
        "dimensions": int(vectors.shape[1]),
        "chunks": records,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print(f"[OK] Saved to {OUTPUT_FILE}")

    # 4. SANITY CHECK: ask a few questions and see which chunks come back.
    #    If embedding works, each question should land on the right section.
    print("\n--- Sanity check: does search find the right chunks? ---")
    test_questions = [
        "How much does a 6-pack cost?",
        "Is the coffee organic?",
        "When is the launch event?",
        "What do customers want?",
    ]
    for question in test_questions:
        print(f"\nQ: {question}")
        for score, chunk in find_similar(question, model, chunks, vectors, top_k=2):
            print(f"   {score:.2f}  {chunk['chunk_id']}  {chunk['section_title']}")


if __name__ == "__main__":
    main()