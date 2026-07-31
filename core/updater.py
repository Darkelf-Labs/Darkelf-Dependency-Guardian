"""
Darkelf Dependency Guardian
Updater Module
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .compatibility import CompatibilityEngine
from .package_manager import PackageManagerDetector
from .rollback import RollbackManager
from .scanner import ProjectScanner
from .validator import ProjectValidator


@dataclass(slots=True)
class UpdateRecommendation:
    package: str
    installed: str
    latest: str
    action: str
    reason: str


class GuardianUpdater:
    """
    Analyze, validate, backup and safely update dependencies.
    """

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir)

        self.scanner = ProjectScanner(self.project_dir)

        self.validator = ProjectValidator(self.project_dir)

        self.pm = PackageManagerDetector(self.project_dir).detect()

        self.compatibility = CompatibilityEngine()

        self.rollback = RollbackManager(self.project_dir)

    # ---------------------------------------------------------
    # Dependency discovery
    # ---------------------------------------------------------

    def get_outdated(self) -> dict:

        result = self.pm.outdated()

        if not result.success:
            return {}

        try:
            return json.loads(result.stdout or "{}")

        except json.JSONDecodeError:
            return {}

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    def recommend(self) -> list[UpdateRecommendation]:

        project = self.scanner.scan()

        report = self.compatibility.check(project)

        outdated = self.get_outdated()

        blocked = {issue.package for issue in report.issues}

        recommendations = []

        for package, info in outdated.items():
            current = str(info.get("current", ""))

            latest = str(info.get("latest", ""))

            if package in blocked:
                recommendations.append(
                    UpdateRecommendation(
                        package,
                        current,
                        latest,
                        "BLOCK",
                        "Blocked by compatibility rules.",
                    )
                )

            else:
                recommendations.append(
                    UpdateRecommendation(
                        package,
                        current,
                        latest,
                        "UPDATE",
                        "Compatible.",
                    )
                )

        return recommendations

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    def print_report(self):

        recommendations = self.recommend()

        print("=" * 70)
        print("Darkelf Dependency Guardian")
        print("Safe Update Report")
        print("=" * 70)

        if not recommendations:
            print("Everything is up to date.")
            return

        for item in recommendations:
            print(item.package)
            print(f" Installed : {item.installed}")
            print(f" Latest    : {item.latest}")
            print(f" Action    : {item.action}")
            print(f" Reason    : {item.reason}")
            print()

    # ---------------------------------------------------------
    # Safe Update
    # ---------------------------------------------------------

    def update_safe(self) -> int:

        #
        # Validate project
        #

        validation = self.validator.validate()

        if not validation.passed:
            print("Project validation failed.")

            return 1

        #
        # Compatibility
        #

        blocked = [r for r in self.recommend() if r.action == "BLOCK"]

        if blocked:
            print("Unsafe update cancelled.")

            for item in blocked:
                print(f" - {item.package}: {item.reason}")

            return 1

        #
        # Backup
        #

        backup = self.rollback.create_backup()

        if not backup.success:
            print(backup.message)

            return 1

        print(backup.message)

        #
        # Update
        #

        update = self.pm.update()

        if not update.success:
            print(update.stderr)

            self.rollback.restore_latest()

            return update.exit_code

        #
        # Lint
        #

        lint = self.pm.lint()

        if not lint.success:
            print("Lint failed.")

            self.rollback.restore_latest()

            return lint.exit_code

        #
        # Build
        #

        build = self.pm.build()

        if not build.success:
            print("Build failed.")

            self.rollback.restore_latest()

            return build.exit_code

        #
        # Tests
        #

        test = self.pm.test()

        if not test.success:
            print("Tests failed.")

            self.rollback.restore_latest()

            return test.exit_code

        print()
        print("Safe update completed successfully.")

        return 0


def main():

    updater = GuardianUpdater()

    updater.print_report()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
