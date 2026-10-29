"""Smoke tests for the CLI entry point."""


import json
import pytest

from kdp_metadata_checker.cli import main


def test_cli_help_exits_zero():
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_cli_version_exits_zero():
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0


def test_cli_clean_metadata_exits_zero():
    assert main(["--title", "The Massive AI Manual", "--description", "Plain English guide."]) == 0


def test_cli_errors_exit_nonzero():
    assert main(["--title", "x" * 201]) == 1


def test_cli_writes_output_file(tmp_path):
    out = tmp_path / "report.md"
    code = main(["--title", "Bad  ", "--output", str(out)])
    assert code == 0
    text = out.read_text(encoding="utf-8")
    assert "# KDP Metadata Check Report" in text
    assert "multiple_spaces" in text


def test_cli_missing_metadata_file_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        main(["--metadata", "does-not-exist.json"])
    assert exc_info.value.code != 0


def test_cli_invalid_metadata_json_exits_nonzero(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        main(["--metadata", str(bad)])
    assert exc_info.value.code != 0


def test_cli_metadata_not_object_exits_nonzero(tmp_path):
    bad = tmp_path / "list.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        main(["--metadata", str(bad)])
    assert exc_info.value.code != 0


def test_cli_custom_rules(tmp_path):
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "title": {"max_length": 5, "checks": []},
                "subtitle": {"max_length": 5, "checks": []},
                "description": {"max_length": 5, "checks": []},
                "categories": {"max_count": 1, "max_length_per": 5, "checks": []},
                "keywords": {"max_count": 1, "max_length_per": 5, "max_total_bytes": 5, "checks": []},
            }
        ),
        encoding="utf-8",
    )
    assert main(["--title", "ok", "--rules", str(rules)]) == 0
    assert main(["--title", "too long", "--rules", str(rules)]) == 1


def test_cli_missing_rules_file_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        main(["--title", "x", "--rules", "no-such-rules.json"])
    assert exc_info.value.code != 0
