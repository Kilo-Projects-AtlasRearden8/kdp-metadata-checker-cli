"""Command-line interface for the KDP metadata checker."""


import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .checker import check_metadata
from .metadata import BookMetadata
from .report import render_markdown
from .rules import Rules


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()] if value else []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kdp-metadata-check",
        description=(
            "Check KDP book metadata (title, subtitle, description, categories, keywords) "
            "for common issues and length limits. Local-first; no API keys required."
        ),
    )
    parser.add_argument("--version", action="version", version=f"kdp-metadata-check {__version__}")
    parser.add_argument("--metadata", help="Path to a JSON file containing book metadata")
    parser.add_argument("--title", default="", help="Book title")
    parser.add_argument("--subtitle", default="", help="Book subtitle")
    parser.add_argument("--description", default="", help="Book description")
    parser.add_argument("--categories", default="", help="Comma-separated categories")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--rules", default=None, help="Path to a custom rules JSON file (default: bundled rules)")
    parser.add_argument("--output", default=None, help="Write the report to this file instead of stdout")
    parser.add_argument(
        "--format",
        choices=["markdown"],
        default="markdown",
        help="Report format",
    )
    return parser


def _load_metadata(path: str) -> BookMetadata:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: metadata file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: metadata file is not valid JSON: {path} ({exc})")
    if not isinstance(data, dict):
        raise SystemExit(f"error: metadata file must contain a JSON object: {path}")
    return BookMetadata.from_dict(data)


def _load_rules(path: str | None) -> Rules:
    rules_path = path or str(Path(__file__).resolve().parent / "rules" / "kdp_rules.json")
    try:
        return Rules.load(rules_path)
    except FileNotFoundError:
        raise SystemExit(f"error: rules file not found: {rules_path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: rules file is not valid JSON: {rules_path} ({exc})")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    rules = _load_rules(args.rules)

    if args.metadata:
        metadata = _load_metadata(args.metadata)
    else:
        metadata = BookMetadata(
            title=args.title,
            subtitle=args.subtitle,
            description=args.description,
            categories=_split_list(args.categories),
            keywords=_split_list(args.keywords),
        )

    report = check_metadata(metadata, rules)
    text = render_markdown(report)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")

    return 0 if report.passed else 1
