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
        if issue.severity.lower() in {"high", "critical"}:
            self.passed = False


class CompatibilityEngine:
    """Validate installed dependencies using RulesEngine."""

    def __init__(self, rules_dir=None):
        self.rules = RulesEngine(rules_dir)

    @staticmethod
    def _major(version: str) -> str:
        digits = "".join(
            ch if ch.isdigit() or ch == "." else " "
            for ch in version
        )
        token = digits.strip().split()
        return token[0].split(".")[0] if token else "0"

    def check(self, project_info) -> CompatibilityReport:

        framework = project_info.framework.lower().replace(".js", "")

        if framework == "next":
            framework = "nextjs"

        fw_version = "unknown"

        for pkg in (
            "next",
            "react",
            "vue",
            "@angular/core",
            "electron",
            "vite",
            "astro",
            "nuxt",
        ):
            if pkg in project_info.all_packages:
                fw_version = project_info.all_packages[pkg]
                break

        report = CompatibilityReport(
            project_info.framework,
            fw_version,
        )

        for package, installed in project_info.all_packages.items():

            allowed, reason = self.rules.is_allowed(
                framework,
                package,
                installed,
            )

            if not allowed:

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
                        severity="high",
                        message=reason,
                    )
                )

        return report


def print_report(report: CompatibilityReport):

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
