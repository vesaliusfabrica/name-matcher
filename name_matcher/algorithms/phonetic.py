from doublemetaphone import doublemetaphone


def get_dm_codes(token: str) -> set[str]:
    primary, secondary = doublemetaphone(token.upper())
    return {c for c in (primary, secondary) if c}


def phonetic_screening(query: str, candidate: str) -> bool:
    """Return True if query and candidate share at least one phonetically similar token pair."""
    query_tokens = query.upper().split()
    candidate_tokens = candidate.upper().split()

    for qt in query_tokens:
        q_codes = get_dm_codes(qt)
        for ct in candidate_tokens:
            c_codes = get_dm_codes(ct)
            for qc in q_codes:
                for cc in c_codes:
                    if qc == cc or qc.startswith(cc) or cc.startswith(qc):
                        return True
    return False
