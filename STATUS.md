# STATUS

## What was built

A local-first Python CLI, `kdp-metadata-check`, that audits Kindle Direct Publishing (KDP) book metadata for common issues and length limits.

**Package:** `kdp_metadata_checker/`
- `metadata.py` — `BookMetadata` model (title, subtitle, description, categories, keywords) with JSON loading.
- `rules.py` — loads validation rules from a local JSON file; `_meta` keys ignored.
- `rules/kdp_rules.json` — default rules (no API keys, no network, fully editable locally).
- `checker.py` — validation logic producing `Issue`/`CheckResult`/`Report` objects.
- `report.py` — Markdown report renderer.
- `cli.py` — argparse CLI (`--metadata`, `--title/--subtitle/--description/--categories/--keywords`, `--rules`, `--output`, `--format`, `--version`); exit code 0 = pass, 1 = errors.
- `__main__.py` — `python3 -m kdp_metadata_checker` entry point.

**Checks implemented:**
- Title/subtitle/description: required, min/max length, max words, trailing whitespace, multiple spaces, all-caps, leading/trailing punctuation.
- Description: raw HTML tags, empty paragraphs (two or more consecutive blank lines).
- Categories: max count (3), max length per item (120), empty items, duplicates, trailing whitespace.
- Keywords: max count (7), max total bytes (500), max length per item (50), empty items, duplicates, repeated words, ASIN-like values.
- Length-limit breaches are errors; style issues are warnings. Severity is configurable per check in the rules JSON.

**Other files:** `pyproject.toml` (setuptools, console script `kdp-metadata-check`, package data includes rules JSON), `LICENSE` (MIT), `README.md`, `tests/` (pytest), `examples/sample_metadata.json`, `.gitignore`.

## How to run

```bash
# From source (no install required)
python3 -m kdp_metadata_checker --metadata examples/sample_metadata.json

# With individual fields
python3 -m kdp_metadata_checker --title "The Massive AI Manual" --keywords "ai,artificial intelligence,machine learning"

# Write a Markdown report to a file
python3 -m kdp_metadata_checker --metadata examples/sample_metadata.json --output report.md

# Installable
pip install kdp-metadata-check   # then: kdp-metadata-check --help
```

Exit code: 0 when no errors, 1 when errors found. Warnings do not affect the exit code.

## Verification results

- Tests: **40 passed** (`python3 -m pytest`) covering validation logic, Markdown rendering, and CLI behavior (exit codes, output file, custom rules, error handling).
- CLI smoke runs: sample metadata passes with 1 warning; deliberately bad metadata exits 1 with errors and warnings listed in the report; `--version` and `--help` work.
- Build: `pip wheel --no-deps --no-build-isolation` succeeds; wheel includes `rules/kdp_rules.json`.

No lint/typecheck tooling is configured in the project.

## Known gaps

- Only Markdown report format supported (`--format markdown` is the only choice).
- Rules are field-level only; no cross-field rules (e.g., title + subtitle combined length).
- Description checks are basic (no HTML well-formedness validation).
- `pip install -e .` requires `--break-system-packages` on this host due to PEP 668; not a code defect.

## Attribution

Built for Dylan Asdale / Asdale Dynamics, LLC (Indiana, formed October 2026). MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.