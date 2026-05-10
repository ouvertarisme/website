# Scripts

## `build_testimonials.py`

Regenerates `testimonial/testimonials.json` from `testimonial/testimonials.csv`. Python 3 stdlib only.

Workflow:

1. Add a row to `testimonial/testimonials.csv` with columns `source,name,quote,mugshot`.
2. Save the avatar image (any filename, e.g. `alice.jpg`) into `testimonial/mugshot/`. Put that filename in the `mugshot` column.
3. Run:
   ```
   python3 scripts/build_testimonials.py
   ```
4. The script renames the file to `<token>.<ext>` (token derived from `source`) and rewrites the JSON. Re-running with no changes is a safe no-op.
5. Commit the updated CSV, JSON, and renamed mugshot file.

If a row's `mugshot` column is left empty, the script expects an existing `<token>.<ext>` file already in `testimonial/mugshot/`.
