#!/usr/bin/env python3
"""Build testimonials/testimonials.json from testimonials/testimonials.csv.

Input CSV columns (header required, any order): id, mugshot, name, quote, source
- id      : stable identifier (e.g. REV-001).
- mugshot : filename of the avatar inside testimonials/mugshots/ (e.g. REV-001.jpg).
- name    : display name shown under the quote.
- quote   : the short testimonial text.
- source  : link to the original post/comment.

Run from the repo root:
    python3 scripts/build_testimonials.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "testimonials" / "testimonials.csv"
JSON_PATH = ROOT / "testimonials" / "testimonials.json"
MUGSHOTS_DIR = ROOT / "testimonials" / "mugshots"

REQUIRED = ("id", "mugshot", "name", "quote", "source")


def detect_encoding(path: Path) -> str:
    """Pick an encoding based on the file's BOM. Defaults to utf-8-sig."""
    head = path.open("rb").read(4)
    if head.startswith(b"\xff\xfe") or head.startswith(b"\xfe\xff"):
        return "utf-16"
    return "utf-8-sig"


def main() -> int:
    if not CSV_PATH.exists():
        print(f"error: {CSV_PATH} not found", file=sys.stderr)
        return 1
    MUGSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    out: list[dict] = []
    warnings = 0

    encoding = detect_encoding(CSV_PATH)
    with CSV_PATH.open(newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED) - set(reader.fieldnames or [])
        if missing:
            print(f"error: CSV missing columns: {sorted(missing)}", file=sys.stderr)
            return 1

        for row_idx, row in enumerate(reader, start=2):
            entry = {k: (row.get(k) or "").strip() for k in REQUIRED}

            empty = [k for k in REQUIRED if not entry[k]]
            if empty:
                print(f"warn: row {row_idx} ({entry['id'] or '?'}): empty {empty}, skipping", file=sys.stderr)
                warnings += 1
                continue

            mug_path = MUGSHOTS_DIR / entry["mugshot"]
            if not mug_path.is_file():
                print(
                    f"warn: {entry['id']}: mugshot '{entry['mugshot']}' not found in "
                    f"testimonials/mugshots/, skipping",
                    file=sys.stderr,
                )
                warnings += 1
                continue

            out.append(entry)

    out.sort(key=lambda e: e["id"])
    JSON_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {JSON_PATH.relative_to(ROOT)} ({len(out)} entries, {warnings} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
