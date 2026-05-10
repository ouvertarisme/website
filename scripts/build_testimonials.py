#!/usr/bin/env python3
"""Build testimonial/testimonials.json from testimonial/testimonials.csv.

CSV columns (header required): source, name, quote, mugshot
- source : URL to the testimonial post (LinkedIn, blog, etc.). Used to derive a stable token.
- name   : display name.
- quote  : the testimonial text.
- mugshot: filename the user dropped into testimonial/mugshot/ (any name).
           The script renames it to <token>.<ext> in place. May be empty if a
           file named <token>.<ext> already exists in mugshot/.

Run from the repo root:
    python3 scripts/build_testimonials.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "testimonial" / "testimonials.csv"
JSON_PATH = ROOT / "testimonial" / "testimonials.json"
MUGSHOT_DIR = ROOT / "testimonial" / "mugshot"


def token_for(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:10]


def find_existing_mugshot(token: str) -> Path | None:
    for p in MUGSHOT_DIR.glob(f"{token}.*"):
        if p.is_file():
            return p
    return None


def main() -> int:
    if not CSV_PATH.exists():
        print(f"error: {CSV_PATH} not found", file=sys.stderr)
        return 1
    MUGSHOT_DIR.mkdir(parents=True, exist_ok=True)

    out: list[dict] = []
    warnings = 0

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"source", "name", "quote", "mugshot"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            print(f"error: CSV missing columns: {sorted(missing)}", file=sys.stderr)
            return 1

        for row_idx, row in enumerate(reader, start=2):
            source = (row.get("source") or "").strip()
            name = (row.get("name") or "").strip()
            quote = (row.get("quote") or "").strip()
            mugshot = (row.get("mugshot") or "").strip()

            if not source or not name or not quote:
                print(
                    f"warn: row {row_idx}: missing source/name/quote, skipping",
                    file=sys.stderr,
                )
                warnings += 1
                continue

            tok = token_for(source)

            target: Path | None = None
            if mugshot:
                src_path = MUGSHOT_DIR / mugshot
                if src_path.is_file():
                    ext = src_path.suffix.lower() or ".jpg"
                    target = MUGSHOT_DIR / f"{tok}{ext}"
                    if src_path.resolve() != target.resolve():
                        # Idempotent rename: if target already exists, remove the
                        # source (already processed) rather than overwriting.
                        if target.exists():
                            src_path.unlink()
                        else:
                            src_path.rename(target)
                else:
                    existing = find_existing_mugshot(tok)
                    if existing is not None:
                        target = existing
                    else:
                        print(
                            f"warn: row {row_idx} ({name}): mugshot '{mugshot}' "
                            f"not found in testimonial/mugshot/, skipping",
                            file=sys.stderr,
                        )
                        warnings += 1
                        continue
            else:
                existing = find_existing_mugshot(tok)
                if existing is None:
                    print(
                        f"warn: row {row_idx} ({name}): no mugshot column and no "
                        f"existing {tok}.* in mugshot/, skipping",
                        file=sys.stderr,
                    )
                    warnings += 1
                    continue
                target = existing

            out.append({
                "token": tok,
                "name": name,
                "quote": quote,
                "source": source,
                "mugshot": target.name,
            })

    JSON_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {JSON_PATH.relative_to(ROOT)} ({len(out)} testimonial(s), {warnings} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
