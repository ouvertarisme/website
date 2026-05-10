# Scripts

## `build_testimonials.py`

Regenerates `testimonials/testimonials.json` from `testimonials/testimonials.csv`. Python 3 stdlib only.

### CSV format

`testimonials/testimonials.csv` (header required, columns in any order):

| column    | meaning                                                 |
|-----------|---------------------------------------------------------|
| `id`      | stable id, e.g. `REV-001`.                              |
| `mugshot` | avatar filename in `testimonials/mugshots/`.            |
| `name`    | display name shown under the quote.                     |
| `quote`   | the short testimonial text.                             |
| `source`  | link to the original post/comment.                      |

### Workflow

1. Drop the avatar image into `testimonials/mugshots/` (e.g. `REV-001.jpg`).
2. Add a row to `testimonials/testimonials.csv` with the matching filename in the `mugshot` column.
3. Run:
   ```
   python3 scripts/build_testimonials.py
   ```
4. Commit the CSV, the new mugshot file, and the regenerated JSON.

Rows with empty fields or a missing mugshot file are skipped with a warning. Re-running with no changes is a safe no-op.
