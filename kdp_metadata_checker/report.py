"""Markdown report rendering for KDP metadata check results."""


from datetime import datetime, timezone

from .checker import Report


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append("# KDP Metadata Check Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Fields checked: {len(report.results)}")
    lines.append(f"- Errors: {len(report.errors)}")
    lines.append(f"- Warnings: {len(report.warnings)}")
    lines.append(f"- Overall: {'PASS' if report.passed else 'FAIL'}")
    lines.append("")
    for result in report.results:
        lines.append(f"## {result.field.title()}")
        lines.append("")
        if not result.issues:
            lines.append("No issues found.")
        else:
            for issue in result.issues:
                lines.append(f"- [{issue.severity.upper()}] {issue.check}: {issue.message}")
        lines.append("")
    return "\n".join(lines)
