from name_matcher import NameMatcher

registry = [
    "John Smith",
    "Jon Smyth",
    "Jane Smith",
    "Robert Johnson",
    "Roberto Johnson",
    "Michael Brown",
    "Smith John",
]

matcher = NameMatcher(registry)

queries = ["John Smith", "Jon Smythe", "Smith John", "Roberto Jonson"]

for query in queries:
    print(f"\nQuery: {query!r}")
    for result in matcher.find_matches(query, top_k=3):
        print(f"  {result.score:.4f}  {result.name}")
