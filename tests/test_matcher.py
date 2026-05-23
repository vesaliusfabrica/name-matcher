import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from name_matcher import NameMatcher, MatchResult
from name_matcher.algorithms.phonetic import phonetic_screening
from name_matcher.algorithms.monge_elkan import monge_elkan_jaro_winkler


REGISTRY = [
    "John Smith",
    "Jon Smyth",
    "Jane Smith",
    "Robert Johnson",
    "Roberto Johnson",
    "Michael Brown",
    "Michelle Brown",
    "Smith John",
]

matcher = NameMatcher(REGISTRY)


class TestPhoneticScreening:
    def test_exact_match_passes(self):
        assert phonetic_screening("John Smith", "John Smith")

    def test_phonetic_variant_passes(self):
        assert phonetic_screening("John Smith", "Jon Smyth")

    def test_name_reversal_passes(self):
        assert phonetic_screening("John Smith", "Smith John")

    def test_unrelated_name_fails(self):
        assert not phonetic_screening("John Smith", "Michael Brown")


class TestMongeElkanJaroWinkler:
    def test_identical_names_score_one(self):
        assert monge_elkan_jaro_winkler("John Smith", "John Smith") == 1.0

    def test_reversed_names_score_high(self):
        score = monge_elkan_jaro_winkler("John Smith", "Smith John")
        assert score > 0.9, f"Expected > 0.9, got {score}"

    def test_variant_spelling_score_high(self):
        score = monge_elkan_jaro_winkler("John Smith", "Jon Smyth")
        assert score > 0.8, f"Expected > 0.8, got {score}"

    def test_unrelated_names_score_low(self):
        score = monge_elkan_jaro_winkler("John Smith", "Michael Brown")
        assert score < 0.7, f"Expected < 0.7, got {score}"


class TestNameMatcher:
    def test_returns_match_results(self):
        results = matcher.find_matches("John Smith")
        assert all(isinstance(r, MatchResult) for r in results)

    def test_top_result_is_exact_match(self):
        results = matcher.find_matches("John Smith")
        assert results[0].name == "John Smith"
        assert results[0].score == 1.0

    def test_respects_top_k(self):
        results = matcher.find_matches("John Smith", top_k=2)
        assert len(results) <= 2

    def test_results_sorted_descending(self):
        results = matcher.find_matches("Robert Johnson")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
