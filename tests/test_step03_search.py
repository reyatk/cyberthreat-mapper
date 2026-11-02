"""
Tests for step03_search.py.

These use tiny hand-made vectors and a fake Ollama, so they run instantly
and don't need Ollama running. They test our math and sorting logic.

Run from the project folder with:  python -m pytest
"""

from types import SimpleNamespace

import pytest

import step03_search as search_mod


# ---------- cosine_similarity ----------

def test_identical_vectors_score_1():
    assert search_mod.cosine_similarity([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_perpendicular_vectors_score_0():
    # [1, 0] points right, [0, 1] points up: completely unrelated directions.
    assert search_mod.cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_length_does_not_matter_only_direction():
    # [2, 4] is just [1, 2] made twice as long, so the meaning (direction) is the same.
    assert search_mod.cosine_similarity([1, 2], [2, 4]) == pytest.approx(1.0)


def test_opposite_vectors_score_minus_1():
    assert search_mod.cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)


# ---------- search ----------

TECHNIQUES = [
    {"id": "T0001", "name": "Points Right"},
    {"id": "T0002", "name": "Points Up"},
    {"id": "T0003", "name": "Points Mostly Right"},
]
VECTORS = [
    [1.0, 0.0],
    [0.0, 1.0],
    [0.9, 0.1],
]


def fake_embed(query_vector):
    """Return a stand-in for ollama.embed that always gives back `query_vector`."""
    def _embed(model, input):
        return SimpleNamespace(embeddings=[query_vector])
    return _embed


def test_search_ranks_closest_first(monkeypatch):
    # The query points right, so "Points Right" should win, then "Mostly Right".
    monkeypatch.setattr(search_mod.ollama, "embed", fake_embed([1.0, 0.0]))
    results = search_mod.search("anything", TECHNIQUES, VECTORS, top_k=3)
    assert [tech["id"] for score, tech in results] == ["T0001", "T0003", "T0002"]


def test_search_returns_only_top_k(monkeypatch):
    monkeypatch.setattr(search_mod.ollama, "embed", fake_embed([1.0, 0.0]))
    results = search_mod.search("anything", TECHNIQUES, VECTORS, top_k=2)
    assert len(results) == 2


def test_search_adds_query_label(monkeypatch):
    # nomic-embed-text needs the "search_query: " label on queries.
    seen = {}

    def spy_embed(model, input):
        seen["input"] = input
        return SimpleNamespace(embeddings=[[1.0, 0.0]])

    monkeypatch.setattr(search_mod.ollama, "embed", spy_embed)
    search_mod.search("stole passwords", TECHNIQUES, VECTORS)
    assert seen["input"] == "search_query: stole passwords"