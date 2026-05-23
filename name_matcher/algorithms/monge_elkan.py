from typing import Callable
import jellyfish


def _one_sided(tokens_a: list[str], tokens_b: list[str],
               sim_func: Callable[[str, str], float]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    total = sum(max(sim_func(ta, tb) for tb in tokens_b) for ta in tokens_a)
    return total / len(tokens_a)


def monge_elkan_jaro_winkler(name_a: str, name_b: str) -> float:
    """One-directional Monge-Elkan score using Jaro-Winkler as the inner similarity.

    For each token in name_a (query), finds the best-matching token in name_b (candidate)
    and averages those scores.  Semantics: score = 1.0 when every query token is fully
    present in the candidate, regardless of how many extra tokens the candidate has.
    Reversal ("Smith John" vs "John Smith") also scores 1.0.
    """
    tokens_a = name_a.upper().split()
    tokens_b = name_b.upper().split()
    jw = jellyfish.jaro_winkler_similarity
    return _one_sided(tokens_a, tokens_b, jw)
