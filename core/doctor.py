"""
Darkelf Dependency Guardian
Doctor Module
"""

from __future__ import annotations

from pathlib import Path

from .compatibility import CompatibilityEngine, print_report
from .package_manager.detect import PackageManagerDetector
from .reporter import Reporter
from .rules_engine import RulesEngine
from .scanner import ProjectScanner
from .validator import ProjectValidator, print_validation


class GuardianDoctor:
    """Runs a complete dependency health check."""

    def __init__(
        self,
        project_dir: str | Path = ".",
        reports_dir: str | Path = "reports",
    ):
        self.project_dir = Path(project_dir).resolve()

        self.validator = ProjectValidator(self.project_dir)

        self.scanner = ProjectScanner(self.project_dir)

        self.compatibility = CompatibilityEngine()

        self.reporter = Reporter(reports_dir)

        self.package_manager = PackageManagerDetector(self.project_dir).detect()

    def run(self):

        print("=" * 60)
        print("Darkelf Dependency Guardian")
        print("=" * 60)

        validation = self.validator.validate()

        print_validation(validation)
        print()

        if not validation.passed:
            print("Project validation failed.")
            return validation

        rules = RulesEngine()

        print("Guardian")
        print("-" * 60)
        print(f"Rules Directory : {rules.rules_dir}")
        print(f"Rules Present   : {rules.rules_dir.exists()}")
        print()

        print("Package Manager")
        print("-" * 60)
        print(f"Detected : {self.package_manager.name}")

        version = self.package_manager.version()

        if version.success:
            print(f"Version  : {version.stdout}")

        print()

        project = self.scanner.scan()

        print("Project")
        print("-" * 60)
        print(f"Name            : {project.package_name}")
        print(f"Framework       : {project.framework}")
        print(f"Package Manager : {project.package_manager}")
        print(f"Version         : {project.version}")
        print()

        report = self.compatibility.check(project)

        print_report(report)

        outputs = {
            "json": self.reporter.write_json(report),
            "markdown": self.reporter.write_markdown(report),
            "html": self.reporter.write_html(report),
            "sarif": self.reporter.write_sarif(report),
        }

        print()
        print("Generated Reports")
        print("-" * 60)

        for fmt, path in outputs.items():
            print(f"{fmt.upper():10} {path}")

        print()

        return report

    @staticmethod
    def exit_code(result) -> int:

        if hasattr(result, "passed"):
            return 0 if result.passed else 1

        return 1


def main() -> int:

    doctor = GuardianDoctor()

    result = doctor.run()

    return GuardianDoctor.exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
