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
    return _one_sided(tokens_a, tokens_b, jellyfish.jaro_winkler_similarity)


# ── Trigram (Dice coefficient) ────────────────────────────────────────────────

def _trigram_set(s: str) -> set[str]:
    s = s.upper()
    if len(s) < 3:
        return {s}
    return {s[i:i + 3] for i in range(len(s) - 2)}


def trigram_similarity(s1: str, s2: str) -> float:
    """Trigram Dice coefficient: 2|A∩B| / (|A|+|B|)."""
    t1 = _trigram_set(s1)
    t2 = _trigram_set(s2)
    if not t1 or not t2:
        return 0.0
    return 2 * len(t1 & t2) / (len(t1) + len(t2))


def monge_elkan_trigram(name_a: str, name_b: str) -> float:
    """One-directional Monge-Elkan score using Trigram Dice as the inner similarity."""
    tokens_a = name_a.upper().split()
    tokens_b = name_b.upper().split()
    return _one_sided(tokens_a, tokens_b, trigram_similarity)
