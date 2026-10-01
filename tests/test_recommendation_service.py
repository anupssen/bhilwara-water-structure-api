"""Tests for the random mock recommendation."""

import random

from app.services.recommendation_service import STRUCTURES, compute_recommendation


def test_random_recommendation_never_repeats_and_covers_all():
    random.seed(0)
    previous = None
    seen = set()
    for _ in range(200):
        result = compute_recommendation(25.4, 74.5, "Mandal", previous)
        name = result["recommendation"]
        assert name in STRUCTURES
        assert name != previous
        seen.add(name)
        previous = name
    assert seen == set(STRUCTURES)


def test_alternatives_are_other_structures_with_lower_scores():
    random.seed(1)
    for _ in range(50):
        result = compute_recommendation(25.4, 74.5, "Mandal")
        alt_names = [alt["name"] for alt in result["alternatives"]]
        alt_scores = [alt["score"] for alt in result["alternatives"]]
        assert len(set(alt_names)) == 3
        assert result["recommendation"] not in alt_names
        assert set(alt_names) <= set(STRUCTURES)
        assert alt_scores == sorted(alt_scores, reverse=True)
        assert max(alt_scores) < result["score"]
