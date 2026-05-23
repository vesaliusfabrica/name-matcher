from dataclasses import dataclass
from .algorithms import phonetic_screening, monge_elkan_jaro_winkler


@dataclass
class MatchResult:
    name: str
    score: float

    def __repr__(self) -> str:
        return f"MatchResult(name={self.name!r}, score={self.score:.4f})"


class NameMatcher:
    """English name matcher using Double Metaphone screening + Monge-Elkan/Jaro-Winkler scoring."""

    def __init__(self, names: list[str]) -> None:
        self.names = names

    def find_matches(self, query: str, top_k: int = 5) -> list[MatchResult]:
        """Return the top-k candidates for *query* from the registered name list.

        Steps:
        1. Phonetic screening via Double Metaphone (fast pre-filter).
        2. Detailed scoring with symmetric Monge-Elkan + Jaro-Winkler.
        """
        candidates = [n for n in self.names if phonetic_screening(query, n)]

        results = [
            MatchResult(name=c, score=monge_elkan_jaro_winkler(query, c))
            for c in candidates
        ]
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
