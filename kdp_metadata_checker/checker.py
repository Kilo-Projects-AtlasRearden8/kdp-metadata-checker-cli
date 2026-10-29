"""Validation logic for KDP book metadata."""


import re
from dataclasses import dataclass, field
from typing import Optional

from .metadata import BookMetadata
from .rules import FieldRule, Rules

_PUNCTUATION = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
_WHITESPACE_LINE = re.compile(r"[ \t]+$", re.MULTILINE)
_HTML_TAG = re.compile(r"<[^>]+>")
_BLANK_PARAGRAPH_RUN = re.compile(r"\n[ \t]*\n[ \t]*\n")
_ASIN_LIKE = re.compile(r"^B0[A-Z0-9]{8}$", re.IGNORECASE)


@dataclass
class Issue:
    """A single validation issue found in a metadata field."""

    field: str
    check: str
    message: str
    severity: str  # "error" or "warning"


@dataclass
class CheckResult:
    """Validation issues for one metadata field."""

    field: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def passed(self) -> bool:
        return not self.errors


@dataclass
class Report:
    """Full validation report for one book's metadata."""

    results: list[CheckResult] = field(default_factory=list)

    @property
    def issues(self) -> list[Issue]:
        return [issue for result in self.results for issue in result.issues]

    @property
    def errors(self) -> list[Issue]:
        return [issue for result in self.results for issue in result.errors]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for result in self.results for issue in result.warnings]

    @property
    def passed(self) -> bool:
        return not self.errors


def _has_letters(value: str) -> bool:
    return any(char.isalpha() for char in value)


def _check_severity(rule: FieldRule, name: str, default: str = "warning") -> str:
    for check in rule.checks:
        if check.name == name:
            return check.severity or default
    return default


def _issue(field: str, check: str, message: str, severity: str) -> Issue:
    return Issue(field=field, check=check, message=message, severity=severity)


def _check_length(value: str, rule: FieldRule) -> list[Issue]:
    issues: list[Issue] = []
    if not value:
        if rule.min_length is not None:
            issues.append(_issue(rule.name, "required", f"{rule.name.title()} is required but is empty.", "error"))
    elif rule.min_length is not None and len(value) < rule.min_length:
        issues.append(
            _issue(
                rule.name,
                "min_length",
                f"{rule.name.title()} is shorter than the recommended minimum of {rule.min_length} characters ({len(value)}).",
                "warning",
            )
        )
    if rule.max_length is not None and len(value) > rule.max_length:
        issues.append(
            _issue(
                rule.name,
                "max_length",
                f"{rule.name.title()} exceeds the maximum length of {rule.max_length} characters ({len(value)}).",
                "error",
            )
        )
    if rule.max_words is not None and len(value.split()) > rule.max_words:
        issues.append(
            _issue(
                rule.name,
                "max_words",
                f"{rule.name.title()} has more than {rule.max_words} words ({len(value.split())}).",
                "error",
            )
        )
    return issues


def _check_named_checks(value: str, rule: FieldRule) -> list[Issue]:
    issues: list[Issue] = []
    for check in rule.checks:
        name = check.name
        severity = check.severity or "warning"
        if name == "trailing_whitespace":
            if _WHITESPACE_LINE.search(value):
                issues.append(
                    _issue(rule.name, "trailing_whitespace", "contains trailing whitespace on one or more lines.", severity)
                )
        elif name == "multiple_spaces":
            if "  " in value:
                issues.append(_issue(rule.name, "multiple_spaces", "contains multiple consecutive spaces.", severity))
        elif name == "all_caps":
            if _has_letters(value) and value == value.upper():
                issues.append(_issue(rule.name, "all_caps", "is written in all capital letters.", severity))
        elif name == "leading_trailing_punctuation":
            stripped = value.strip()
            if stripped and (stripped[0] in _PUNCTUATION or stripped[-1] in _PUNCTUATION):
                issues.append(_issue(rule.name, "leading_trailing_punctuation", "starts or ends with punctuation.", severity))
        elif name == "raw_html_tags":
            if _HTML_TAG.search(value):
                issues.append(
                    _issue(
                        rule.name,
                        "raw_html_tags",
                        "contains HTML tags. KDP supports basic HTML in descriptions, but verify the markup renders correctly.",
                        severity,
                    )
                )
        elif name == "empty_paragraphs":
            if _BLANK_PARAGRAPH_RUN.search(value):
                issues.append(
                    _issue(rule.name, "empty_paragraphs", "contains two or more consecutive blank lines.", severity)
                )
    return issues


def check_string(value: str, rule: Optional[FieldRule]) -> list[Issue]:
    if rule is None:
        return []
    issues = _check_length(value, rule)
    issues.extend(_check_named_checks(value, rule))
    return issues


def check_items(items: list[str], rule: Optional[FieldRule]) -> list[Issue]:
    issues: list[Issue] = []
    if rule is None:
        return issues
    if rule.max_count is not None and len(items) > rule.max_count:
        issues.append(
            _issue(
                rule.name,
                "max_count",
                f"has {len(items)} items; the maximum is {rule.max_count}.",
                "error",
            )
        )
    seen: set[str] = set()
    has_duplicate = False
    cleaned: list[str] = []
    for item in items:
        key = item.casefold()
        if key in seen:
            has_duplicate = True
        seen.add(key)
        stripped = item.strip()
        cleaned.append(stripped)
        if not stripped:
            issues.append(_issue(rule.name, "empty_items", "contains an empty item.", "warning"))
            continue
        if rule.max_length_per is not None and len(item) > rule.max_length_per:
            issues.append(
                _issue(
                    rule.name,
                    "max_length_per",
                    f"item {item!r} exceeds {rule.max_length_per} characters ({len(item)}).",
                    "error",
                )
            )
        issues.extend(_check_named_checks(item, rule))
    if has_duplicate:
        issues.append(
            _issue(rule.name, "duplicates", "contains duplicate items (case-insensitive).", _check_severity(rule, "duplicates"))
        )
    if rule.max_total_bytes is not None:
        total = sum(len(item.encode("utf-8")) for item in items)
        if total > rule.max_total_bytes:
            issues.append(
                _issue(
                    rule.name,
                    "max_total_bytes",
                    f"total size is {total} bytes; the maximum is {rule.max_total_bytes} bytes.",
                    "error",
                )
            )
    words: dict[str, int] = {}
    for item in cleaned:
        for word in item.split():
            words[word.casefold()] = words.get(word.casefold(), 0) + 1
    repeated = sorted(word for word, count in words.items() if count > 1)
    if repeated:
        issues.append(
            _issue(
                rule.name,
                "repeated_words",
                f"contains repeated words: {', '.join(repeated)}.",
                _check_severity(rule, "repeated_words"),
            )
        )
    asin_like = [item for item in cleaned if item and _ASIN_LIKE.match(item)]
    if asin_like:
        issues.append(
            _issue(
                rule.name,
                "asin_like",
                f"contains ASIN-like value(s): {', '.join(asin_like)}.",
                _check_severity(rule, "asin_like"),
            )
        )
    return issues


def check_metadata(metadata: BookMetadata, rules: Rules) -> Report:
    results = [
        CheckResult(field="title", issues=check_string(metadata.title, rules.get("title"))),
        CheckResult(field="subtitle", issues=check_string(metadata.subtitle, rules.get("subtitle"))),
        CheckResult(field="description", issues=check_string(metadata.description, rules.get("description"))),
        CheckResult(field="categories", issues=check_items(metadata.categories, rules.get("categories"))),
        CheckResult(field="keywords", issues=check_items(metadata.keywords, rules.get("keywords"))),
    ]
    return Report(results=results)
