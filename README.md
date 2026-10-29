# KDP Metadata Checker

Local-first command-line tool that checks Kindle Direct Publishing (KDP) book
metadata — title, subtitle, description, categories, and keywords — for common
issues and length limits. No API keys, no network access, no personal data.

Built and maintained by Asdale Dynamics, LLC.

## Install

```bash
pip install kdp-metadata-check
```

Or run directly from source:

```bash
python -m kdp_metadata_checker --help
```

## Usage

Check metadata from a JSON file:

```bash
kdp-metadata-check --metadata book.json
```

Or pass fields on the command line:

```bash
kdp-metadata-check \
  --title "The Massive AI Manual" \
  --subtitle "Artificial intelligence explained like a friend would" \
  --description "A plain-English, step-by-step guide to AI for beginners." \
  --categories "Computers & Technology,Artificial Intelligence" \
  --keywords "ai,artificial intelligence,machine learning,local ai,beginners guide"
```

Write the Markdown report to a file:

```bash
kdp-metadata-check --metadata book.json --output report.md
```

## Rules

Validation rules live in `kdp_metadata_checker/rules/kdp_rules.json`, a local JSON
file you can edit. Override them with `--rules /path/to/rules.json`.

Limits enforced by default:

- Title: max 200 characters, max 100 words, required
- Subtitle: max 200 characters
- Description: max 4000 characters
- Categories: max 3, max 120 characters each
- Keywords: max 7, max 50 characters each, max 500 bytes total

Common issues flagged: trailing whitespace, multiple spaces, all-caps text,
leading or trailing punctuation, raw HTML tags, empty paragraphs, empty or
duplicate items, repeated words across keywords, and ASIN-like keyword values.

## Report

The tool prints a Markdown report with a summary and per-field issue lists.
Exit code is 0 when no errors are found and 1 when errors are found; warnings
do not change the exit code.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) belongs to Dylan Asdale, a
registered nurse turned AI author and founder of dylanasdale.github.io. The LLC
publishes beginner-friendly AI education, books, guides, and practical open-source
tools that explain AI "like a friend would": plain English, step by step, never
condescending.
