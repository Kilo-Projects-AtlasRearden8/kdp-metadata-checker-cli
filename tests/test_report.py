"""Tests for Markdown report rendering."""


from kdp_metadata_checker.checker import CheckResult, Issue, Report
from kdp_metadata_checker.report import render_markdown


def test_render_markdown_contains_summary():
    report = Report(
        results=[
            CheckResult(
                field="title",
                issues=[Issue("title", "max_length", "too long", "error")],
            ),
            CheckResult(field="subtitle", issues=[]),
        ]
    )
    text = render_markdown(report)
    assert "# KDP Metadata Check Report" in text
    assert "## Summary" in text
    assert "- Errors: 1" in text
    assert "- Warnings: 0" in text
    assert "- Overall: FAIL" in text
    assert "## Title" in text
    assert "[ERROR] max_length: too long" in text
    assert "## Subtitle" in text
    assert "No issues found." in text


def test_render_markdown_pass_when_no_errors():
    report = Report(
        results=[
            CheckResult(field="keywords", issues=[Issue("keywords", "all_caps", "caps", "warning")])
        ]
    )
    assert report.passed
    assert "- Overall: PASS" in render_markdown(report)
