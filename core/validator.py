"""
Darkelf Dependency Guardian
Validator
"""

from __future__ import annotations

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
    """Validate project structure and development environment."""

    REQUIRED_SCRIPTS = ("lint", "build")
    OPTIONAL_SCRIPTS = ("test",)

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()

    def _exists(self, name: str) -> bool:
        return (self.root / name).exists()

    def validate(self) -> ValidationReport:
        import json

        report = ValidationReport()

        pkg = self.root / "package.json"
        if not pkg.exists():
            report.add(ValidationIssue("package.json", False, "Missing package.json"))
            return report
        report.add(ValidationIssue("package.json", True, "Found"))

        data = json.loads(pkg.read_text(encoding="utf-8"))

        report.add(
            ValidationIssue(
                "package-lock.json",
                self._exists("package-lock.json"),
                "Found" if self._exists("package-lock.json") else "Lock file missing",
            )
        )

        report.add(
            ValidationIssue(
                "node_modules",
                self._exists("node_modules"),
                "Installed" if self._exists("node_modules") else "Run npm install",
            )
        )

        for exe in ("node", "npm"):
            ok = shutil.which(exe) is not None
            report.add(
                ValidationIssue(
                    exe,
                    ok,
                    "Detected" if ok else f"{exe} not found in PATH",
                )
            )

        scripts = data.get("scripts", {})
        for script in self.REQUIRED_SCRIPTS:
            ok = script in scripts
            report.add(
                ValidationIssue(
                    f"script:{script}",
                    ok,
                    "Present" if ok else "Missing required script",
                )
            )

        for script in self.OPTIONAL_SCRIPTS:
            ok = script in scripts
            report.add(
                ValidationIssue(
                    f"script:{script}",
                    True,
                    "Present" if ok else "Optional script not defined",
                )
            )

        for folder in ("rules", "reports"):
            ok = self._exists(folder)
            report.add(
                ValidationIssue(
                    folder,
                    ok,
                    "Present" if ok else "Directory missing",
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
