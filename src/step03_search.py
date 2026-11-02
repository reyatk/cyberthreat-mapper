"""
step03_search.py
Step 3b: Find the ATT&CK techniques whose meaning is closest to a piece of report text.

Reads:  data/processed/techniques.json
        data/processed/technique_embeddings.json   (made by step03_embed_techniques.py)

Run from the project folder with the virtual environment on:
    python src/step03_search.py
"""

import json
import math
import sys
from pathlib import Path

import ollama

TECHNIQUES_PATH = Path("data/processed/techniques.json")
EMBEDDINGS_PATH = Path("data/processed/technique_embeddings.json")
EMBED_MODEL = "nomic-embed-text"   # must match the model used in step03_embed_techniques.py
TOP_K = 5                          # how many results to show

# A sample report sentence. It never says "scheduled task" or "registry",
# so a keyword search would struggle. Embeddings match on meaning instead.
QUERY = (
    "After gaining access, the attackers made sure their backdoor would "
    "start again automatically every time the computer was restarted."
)


def load_index() -> tuple[list[dict], list[list[float]]]:
    """
    Load the techniques and their saved embeddings, in matching order.

    Raises:
        FileNotFoundError: a data file is missing (an earlier step wasn't run).
        ValueError: the embeddings don't match the techniques or the model.
    """
    with open(TECHNIQUES_PATH, encoding="utf-8") as f:
        techniques = json.load(f)
    with open(EMBEDDINGS_PATH, encoding="utf-8") as f:
        saved = json.load(f)

    # Embeddings from different models can't be compared, so check first.
    if saved["model"] != EMBED_MODEL:
        raise ValueError(
            f"Embeddings were made with {saved['model']}, not {EMBED_MODEL}. "
            "Re-run step03_embed_techniques.py."
        )
    # Both files must list the techniques in the same order.
    if saved["ids"] != [t["id"] for t in techniques]:
        raise ValueError(
            "techniques.json and the saved embeddings don't match. "
            "Re-run step03_embed_techniques.py."
        )
    return techniques, saved["vectors"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Score how similar two embeddings are: close to 1 = similar meaning, near 0 = unrelated.

    Formula: (a . b) / (length of a * length of b)
    The "dot product" a . b means: multiply each pair of matching numbers
    (a[0]*b[0], a[1]*b[1], ...) and add up all the results.
    """
    dot = sum(x * y for x, y in zip(a, b))
    length_a = math.sqrt(sum(x * x for x in a))
    length_b = math.sqrt(sum(y * y for y in b))
    return dot / (length_a * length_b)


def search(query: str, techniques: list[dict], vectors: list[list[float]],
           top_k: int = TOP_K) -> list[tuple[float, dict]]:
    """Return the top_k (score, technique) pairs most similar to the query, best first."""
    # The query is what we search WITH, so it gets the "search_query: " label.
    result = ollama.embed(model=EMBED_MODEL, input="search_query: " + query)
    query_vector = result.embeddings[0]

    # Score every technique against the query.
    scored = []
    for tech, vector in zip(techniques, vectors):
        scored.append((cosine_similarity(query_vector, vector), tech))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def main() -> int:
    """Search for report text and print the top matches. Returns 0 on success, 1 on failure."""
    try:
        techniques, vectors = load_index()
    except FileNotFoundError as err:
        print(f"Missing data file: {err.filename}. Run steps 02 and 03 (embed) first.")
        return 1
    except ValueError as err:
        print(err)
        return 1

    # Use text typed after the command if there is any; otherwise ask for it.
    query = " ".join(sys.argv[1:]) or input("Paste report text: ")

    try:
        results = search(query, techniques, vectors)
    except ConnectionError:
        print("Could not reach Ollama. Open the Ollama app and try again.")
        return 1
    except ollama.ResponseError as err:
        print(f"Ollama returned an error: {err.error}")
        return 1

    print("REPORT TEXT:")
    print(f"  {query}\n")
    print(f"TOP {len(results)} MATCHING TECHNIQUES:")
    for rank, (score, tech) in enumerate(results, start=1):
        print(f"  {rank}. {tech['id']:<10} {tech['name']:<45} score {score:.3f}")
    return 0


# Runs main() only when you run this file directly.
if __name__ == "__main__":
    sys.exit(main())