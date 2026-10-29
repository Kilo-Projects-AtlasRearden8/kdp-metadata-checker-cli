"""Smoke tests for the CLI entry point."""


import pytest

from kdp_metadata_checker.cli import main


def test_cli_help_exits_zero():
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
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
