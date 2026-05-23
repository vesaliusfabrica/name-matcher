from typing import Callable
import jellyfish


def _one_sided(tokens_a: list[str], tokens_b: list[str],
               sim_func: Callable[[str, str], float]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    total = sum(max(sim_func(ta, tb) for tb in tokens_b) for ta in tokens_a)
    return total / len(tokens_a)


def monge_elkan_jaro_winkler(name_a: str, name_b: str) -> float:
    """Symmetric Monge-Elkan score using Jaro-Winkler as the inner similarity.

    Symmetric averaging handles first/last name reversal gracefully.
    """
    tokens_a = name_a.upper().split()
    tokens_b = name_b.upper().split()
    jw = jellyfish.jaro_winkler_similarity
    me_ab = _one_sided(tokens_a, tokens_b, jw)
    me_ba = _one_sided(tokens_b, tokens_a, jw)
    return (me_ab + me_ba) / 2
