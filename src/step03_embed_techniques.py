"""
step03_embed_techniques.py
Step 3a: Turn every ATT&CK technique into an embedding (a list of numbers
that captures its meaning) and save them, so this only has to run once.

Reads:  data/processed/techniques.json            (made by step02)
Writes: data/processed/technique_embeddings.json

Run from the project folder with the virtual environment on:
    python src/step03_embed_techniques.py
"""

import json
import sys
import time
from pathlib import Path

import ollama

TECHNIQUES_PATH = Path("data/processed/techniques.json")
EMBEDDINGS_PATH = Path("data/processed/technique_embeddings.json")
EMBED_MODEL = "nomic-embed-text"
BATCH_SIZE = 32  # how many texts to send to Ollama in one request


def technique_to_text(tech: dict) -> str:
    """
    Turn one technique into the text we embed.

    nomic-embed-text expects documents (the things being searched) to start
    with "search_document: ". Including the name as well as the description
    gives the model more to go on.
    """
    return f"search_document: {tech['name']}. {tech['description']}"
    return ""


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts in batches, printing progress. Returns one vector per text."""
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]  # the next 32 texts (or fewer at the end)
        result = ollama.embed(model=EMBED_MODEL, input=batch)
        vectors.extend(result.embeddings)
        print(f"  embedded {min(start + BATCH_SIZE, len(texts))}/{len(texts)}")
    return vectors


def main() -> int:
    """Embed all techniques and save them. Returns 0 on success, 1 on failure."""
    if not TECHNIQUES_PATH.exists():
        print(f"Can't find {TECHNIQUES_PATH}. Run step02_load_attack.py first.")
        return 1

    with open(TECHNIQUES_PATH, encoding="utf-8") as f:
        techniques = json.load(f)

    texts = [technique_to_text(t) for t in techniques]
    print(f"Embedding {len(texts)} techniques with {EMBED_MODEL}...")
    start = time.perf_counter()

    try:
        vectors = embed_texts(texts)
    except ConnectionError:
        print("Could not reach Ollama. Open the Ollama app and try again.")
        return 1
    except ollama.ResponseError as err:
        print(f"Ollama returned an error: {err.error}")
        print(f"If the model is missing, run: ollama pull {EMBED_MODEL}")
        return 1

    # Safety check: there must be exactly one vector per technique.
    if len(vectors) != len(techniques):
        print(f"Expected {len(techniques)} embeddings but got {len(vectors)}. Check TODO 2.")
        return 1

    output = {
        "model": EMBED_MODEL,  # saved so later steps can check they use the same model
        "ids": [t["id"] for t in techniques],
        "vectors": vectors,
    }
    EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EMBEDDINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f)  # no indent: this file is for the computer, not people

    seconds = time.perf_counter() - start
    print(f"Saved {len(vectors)} embeddings ({len(vectors[0])} numbers each) "
          f"to {EMBEDDINGS_PATH} in {seconds:.0f}s")
    return 0


# Runs main() only when you run this file directly.
if __name__ == "__main__":
    sys.exit(main())