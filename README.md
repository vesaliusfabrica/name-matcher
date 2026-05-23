# name-matcher

English name matching library using a three-stage pipeline:

1. **Double Metaphone** — fast phonetic pre-filter to narrow candidates
2. **Monge-Elkan** — token-level similarity that handles first/last name reversal
3. **Jaro-Winkler** — inner string similarity for typo tolerance

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from name_matcher import NameMatcher

registry = ["John Smith", "Jane Smith", "Robert Johnson"]
matcher = NameMatcher(registry)

results = matcher.find_matches("Jon Smythe", top_k=3)
for r in results:
    print(f"{r.score:.4f}  {r.name}")
```

## How it works

### Stage 1 — Phonetic screening (Double Metaphone)

Each token in the query name is encoded with Double Metaphone. A candidate passes the filter if any of its tokens share a code (exact or prefix match) with a query token. This eliminates clearly unrelated names before the expensive similarity step.

### Stage 2 — Monge-Elkan + Jaro-Winkler scoring

For each screened candidate the symmetric Monge-Elkan score is computed:

```
score = ( ME(query → candidate) + ME(candidate → query) ) / 2
```

where each direction averages the best Jaro-Winkler match for every token. Symmetric averaging makes the score robust to "Smith John" vs "John Smith" reversal.

## Running tests

```bash
python -m pytest tests/ -v
```

## Running the example

```bash
python example.py
```
