"""
Darkelf Dependency Guardian
Doctor Module
"""

from __future__ import annotations

from pathlib import Path

from .compatibility import CompatibilityEngine, print_report
from .reporter import Reporter
from .scanner import ProjectScanner
from .validator import ProjectValidator, print_validation
from .package_manager.detect import PackageManagerDetector


class GuardianDoctor:
    """Runs a complete dependency health check."""

    def __init__(
        self,
        project_dir: str | Path = ".",
        reports_dir: str | Path = "reports",
    ):
        self.project_dir = Path(project_dir)

        self.validator = ProjectValidator(self.project_dir)

        self.scanner = ProjectScanner(self.project_dir)

        self.compatibility = CompatibilityEngine()

        self.reporter = Reporter(reports_dir)

        self.package_manager = PackageManagerDetector(
            self.project_dir
        ).detect()

    def run(self):

        print("=" * 60)
        print("Darkelf Dependency Guardian")
        print("=" * 60)

        #
        # Validate project
        #

        validation = self.validator.validate()

        print_validation(validation)
        print()

        if not validation.passed:
            print("Project validation failed.")
            return validation

        #
        # Package manager information
        #

        print("Package Manager")
        print("-" * 60)
        print(f"Detected : {self.package_manager.name}")

        version = self.package_manager.version()

        if version.success:
            print(f"Version  : {version.stdout}")

        print()

        #
        # Project scan
        #

        project = self.scanner.scan()

        print("Project")
        print("-" * 60)

        print(f"Name            : {project.package_name}")
        print(f"Framework       : {project.framework}")
        print(f"Package Manager : {project.package_manager}")
        print(f"Version         : {project.version}")

        print()

        #
        # Compatibility
        #

        report = self.compatibility.check(project)

        print_report(report)

        #
        # Reports
        #

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

        #
        # Package manager diagnostics
        #

        print("Package Manager Diagnostics")
        print("-" * 60)

        doctor = self.package_manager.doctor()

        if doctor.success:
            print(doctor.stdout)
        else:
            print(doctor.stderr)

        print()

        audit = self.package_manager.audit()

        if audit.success:
            print("Audit completed successfully.")
        else:
            print("Audit reported issues.")

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
