from dataclasses import dataclass
from .algorithms import phonetic_screening, monge_elkan_jaro_winkler, monge_elkan_trigram, monge_elkan_levenshtein

_SCORE_FUNCS = {
    "jaro_winkler": monge_elkan_jaro_winkler,
    "trigram":      monge_elkan_trigram,
    "levenshtein":  monge_elkan_levenshtein,
}


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

    def find_matches(
        self, query: str, top_k: int = 5, min_score: float = 0.0,
        method: str = "jaro_winkler",
    ) -> list[MatchResult]:
        """Return the top-k candidates for *query* from the registered name list.

        Parameters
        ----------
        method : "jaro_winkler" | "trigram"
            Inner similarity function used inside Monge-Elkan.
        """
        score_func = _SCORE_FUNCS.get(method, monge_elkan_jaro_winkler)
        candidates = [n for n in self.names if phonetic_screening(query, n)]

        results = []
        for c in candidates:
            score = score_func(query, c)
            if score >= min_score:
                results.append(MatchResult(name=c, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
