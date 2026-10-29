"""Local JSON rule loading for KDP metadata checks."""


import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class CheckRule:
    """A single named check with an optional severity override."""

    name: str
    severity: str = "warning"


@dataclass
class FieldRule:
    """Validation rules for one metadata field."""

    name: str
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    max_words: Optional[int] = None
    max_count: Optional[int] = None
    max_length_per: Optional[int] = None
    max_total_bytes: Optional[int] = None
    checks: list[CheckRule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, name: str, raw: dict) -> "FieldRule":
        checks = [
            CheckRule(item.get("name", ""), item.get("severity", "warning"))
            for item in raw.get("checks", [])
            if item.get("name")
        ]
        return cls(
            name=name,
            max_length=raw.get("max_length"),
            min_length=raw.get("min_length"),
            max_words=raw.get("max_words"),
            max_count=raw.get("max_count"),
            max_length_per=raw.get("max_length_per"),
            max_total_bytes=raw.get("max_total_bytes"),
            checks=checks,
        )


@dataclass
class Rules:
    """Collection of field rules loaded from a local JSON file."""

    fields: dict[str, FieldRule]

    def get(self, name: str) -> Optional[FieldRule]:
        return self.fields.get(name)

    @classmethod
    def load(cls, path: str | Path) -> "Rules":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        fields: dict[str, FieldRule] = {}
        for key, raw in data.items():
            if key.startswith("_"):
                continue
            if isinstance(raw, dict):
                fields[key] = FieldRule.from_dict(key, raw)
        return cls(fields=fields)
