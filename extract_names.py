"""Extract English names from the Japanese asset-freeze CSV (資産凍結リスト).

Usage:
    python extract_names.py <input.csv> [output.csv]

Reads columns:
  - 氏名（英語）        : primary English name
  - 別名・別称（英語）  : semicolon-separated English aliases

Outputs a single-column CSV with header "name", one name per row,
deduped and sorted — ready to import into the name-matcher GUI.
"""

import csv
import sys
import pathlib


def extract(input_path: str, output_path: str) -> int:
    names: set[str] = set()

    with open(input_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            primary = (row.get("氏名（英語）") or "").strip()
            if primary:
                names.add(primary)

            aliases_raw = (row.get("別名・別称（英語）") or "").strip()
            for alias in aliases_raw.split(";"):
                alias = alias.strip()
                if alias:
                    names.add(alias)

    sorted_names = sorted(names)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["name"])
        for name in sorted_names:
            writer.writerow([name])

    return len(sorted_names)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_names.py <input.csv> [output.csv]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else str(
        pathlib.Path(input_path).with_stem(pathlib.Path(input_path).stem + "_names")
    )

    count = extract(input_path, output_path)
    print(f"Extracted {count} names → {output_path}")
