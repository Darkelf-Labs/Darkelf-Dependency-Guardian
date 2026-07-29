"""
Darkelf Dependency Guardian
Validator
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ValidationIssue:
    name: str
    passed: bool
    message: str


@dataclass(slots=True)
class ValidationReport:
    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if not issue.passed:
            self.passed = False


class ProjectValidator:
    """Validate the target project (not Guardian itself)."""

    REQUIRED_SCRIPTS = ("lint", "build")
    OPTIONAL_SCRIPTS = ("test",)

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()

    def _exists(self, path: str) -> bool:
        return (self.root / path).exists()

    def validate(self) -> ValidationReport:

        report = ValidationReport()

        pkg = self.root / "package.json"

        if not pkg.exists():
            report.add(
                ValidationIssue(
                    "package.json",
                    False,
                    "Missing package.json",
                )
            )
            return report

        report.add(
            ValidationIssue(
                "package.json",
                True,
                "Found",
            )
        )

        data = json.loads(pkg.read_text(encoding="utf-8"))

        lock_files = (
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "bun.lockb",
        )

        has_lock = any(self._exists(f) for f in lock_files)

        report.add(
            ValidationIssue(
                "lockfile",
                has_lock,
                "Found" if has_lock else "No lock file found",
            )
        )

        node_modules_exists = self._exists("node_modules")

        report.add(
            ValidationIssue(
                "node_modules",
                True,  # Optional, never fail validation
                "Installed"
                if node_modules_exists
                else "Not installed (using package lockfile)",
    )
)

        for exe in ("node", "npm"):
            ok = shutil.which(exe) is not None

            report.add(
                ValidationIssue(
                    exe,
                    ok,
                    "Detected" if ok else f"{exe} not found",
                )
            )

        scripts = data.get("scripts", {})

        for script in self.REQUIRED_SCRIPTS:

            ok = script in scripts

            report.add(
                ValidationIssue(
                    f"script:{script}",
                    ok,
                    "Present"
                    if ok
                    else "Missing required script",
                )
            )

        for script in self.OPTIONAL_SCRIPTS:

            ok = script in scripts

            report.add(
                ValidationIssue(
                    f"script:{script}",
                    True,
                    "Present"
                    if ok
                    else "Optional",
                )
            )

        reports_dir = self.root / "reports"

        report.add(
            ValidationIssue(
                "reports",
                True,
                "Present"
                if reports_dir.exists()
                else "Will be created automatically",
            )
        )

        return report


def print_validation(report: ValidationReport) -> None:

    print("=" * 60)
    print("Darkelf Dependency Guardian Validation")
    print("=" * 60)

    for issue in report.issues:

        status = "PASS" if issue.passed else "FAIL"

        print(f"[{status:4}] {issue.name:<22} {issue.message}")

    print("-" * 60)
    print("Overall:", "PASS" if report.passed else "FAIL")


if __name__ == "__main__":
    validator = ProjectValidator()
    print_validation(validator.validate())
