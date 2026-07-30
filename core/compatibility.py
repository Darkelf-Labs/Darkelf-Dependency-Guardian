"""
Darkelf Dependency Guardian
Compatibility Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .rules_engine import RulesEngine


@dataclass(slots=True)
class CompatibilityIssue:
    package: str
    installed: str
    expected: str
    severity: str
    message: str


@dataclass(slots=True)
class CompatibilityReport:
    framework: str
    framework_version: str
    passed: bool = True
    issues: list[CompatibilityIssue] = field(default_factory=list)

    def add(self, issue: CompatibilityIssue) -> None:
        self.issues.append(issue)

        if issue.severity.lower() in {
            "high",
            "critical",
        }:
            self.passed = False


class CompatibilityEngine:
    """Validate project dependencies against Guardian rules."""

    def __init__(
        self,
        rules_dir=None,
        mode: str = "strict",
    ):
        self.rules = RulesEngine(
            rules_dir=rules_dir,
            mode=mode,
        )

    @staticmethod
    def _normalize_framework(name: str) -> str:
        framework = name.lower().replace(".js", "")

        aliases = {
            "next": "nextjs",
        }

        return aliases.get(framework, framework)

    @staticmethod
    def _detect_framework_version(project_info) -> str:
        for package in (
            "next",
            "react",
            "vue",
            "@angular/core",
            "electron",
            "vite",
            "astro",
            "nuxt",
        ):
            if package in project_info.all_packages:
                return project_info.all_packages[package]

        return "unknown"

    def check(self, project_info) -> CompatibilityReport:

        framework = self._normalize_framework(project_info.framework)

        report = CompatibilityReport(
            framework=project_info.framework,
            framework_version=self._detect_framework_version(project_info),
        )

        for package, installed in project_info.all_packages.items():

            result = self.rules.check_dependency(
                framework,
                package,
                installed,
            )

            if result.allowed:
                continue

            rule = self.rules.find_rule(
                framework,
                package,
            )

            expected = (
                ", ".join(rule.allowed)
                if rule and rule.allowed
                else "Supported version"
            )

            report.add(
                CompatibilityIssue(
                    package=package,
                    installed=installed,
                    expected=expected,
                    severity=result.severity,
                    message=result.reason,
                )
            )

        return report


def print_report(report: CompatibilityReport) -> None:

    print("=" * 60)
    print("Darkelf Dependency Guardian Compatibility Report")
    print("=" * 60)

    print(f"Framework : {report.framework}")
    print(f"Version   : {report.framework_version}")
    print(f"Status    : {'PASS' if report.passed else 'FAIL'}")
    print()

    if not report.issues:
        print("No compatibility issues detected.")
        return

    for issue in report.issues:
        print(f"[{issue.severity.upper()}] {issue.package}")
        print(f" Installed : {issue.installed}")
        print(f" Expected  : {issue.expected}")
        print(f" Reason    : {issue.message}")
        print()
