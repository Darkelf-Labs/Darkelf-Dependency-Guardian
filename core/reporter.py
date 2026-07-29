
"""
Darkelf Dependency Guardian
Reporter
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


class Reporter:
    """Generate reports in multiple formats."""

    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def to_dict(self, report: Any) -> dict:
        return asdict(report)

    def write_json(self, report: Any, filename: str = "report.json") -> Path:
        path = self.output_dir / filename
        path.write_text(
            json.dumps(self.to_dict(report), indent=2),
            encoding="utf-8",
        )
        return path

    def write_markdown(self, report: Any, filename: str = "report.md") -> Path:
        path = self.output_dir / filename

        lines = [
            "# Darkelf Dependency Guardian Report",
            "",
            f"Generated: {self._timestamp()}",
            "",
            f"- **Framework:** {report.framework}",
            f"- **Version:** {report.framework_version}",
            f"- **Status:** {'PASS' if report.passed else 'FAIL'}",
            "",
            "## Issues",
            "",
        ]

        if not report.issues:
            lines.append("No compatibility issues detected.")
        else:
            for issue in report.issues:
                lines.extend([
                    f"### {issue.package}",
                    f"- Severity: {issue.severity}",
                    f"- Installed: `{issue.installed}`",
                    f"- Expected: `{issue.expected}`",
                    f"- Message: {issue.message}",
                    "",
                ])

        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def write_html(self, report: Any, filename: str = "report.html") -> Path:
        path = self.output_dir / filename

        rows = ""
        for issue in report.issues:
            rows += (
                "<tr>"
                f"<td>{escape(issue.package)}</td>"
                f"<td>{escape(issue.installed)}</td>"
                f"<td>{escape(issue.expected)}</td>"
                f"<td>{escape(issue.severity)}</td>"
                f"<td>{escape(issue.message)}</td>"
                "</tr>\n"
            )

        if not rows:
            rows = "<tr><td colspan='5'>No compatibility issues detected.</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Darkelf Dependency Guardian Report</title>
<style>
body{{font-family:Arial,sans-serif;margin:40px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ccc;padding:8px;text-align:left}}
th{{background:#f3f3f3}}
</style>
</head>
<body>
<h1>Darkelf Dependency Guardian Report</h1>
<p><strong>Generated:</strong> {self._timestamp()}</p>
<p><strong>Framework:</strong> {escape(report.framework)}</p>
<p><strong>Version:</strong> {escape(report.framework_version)}</p>
<p><strong>Status:</strong> {"PASS" if report.passed else "FAIL"}</p>

<table>
<thead>
<tr>
<th>Package</th>
<th>Installed</th>
<th>Expected</th>
<th>Severity</th>
<th>Message</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>
"""
        path.write_text(html, encoding="utf-8")
        return path

    def write_sarif(self, report: Any, filename: str = "report.sarif") -> Path:
        results = []
        for issue in report.issues:
            results.append({
                "ruleId": issue.package,
                "level": issue.severity.lower(),
                "message": {"text": issue.message},
            })

        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Darkelf Dependency Guardian",
                        "version": "1.0.0",
                    }
                },
                "results": results,
            }],
        }

        path = self.output_dir / filename
        path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")
        return path
