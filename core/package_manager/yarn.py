"""
Darkelf Dependency Guardian

Yarn Package Manager

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

from .base import CommandResult, PackageManager


class YarnManager(PackageManager):
    """
    Yarn package manager implementation.
    """

    name = "yarn"
    executable = "yarn"

    def __init__(self, project_dir: str | Path = "."):
        super().__init__(project_dir)

    # ---------------------------------------------------------
    # Installation
    # ---------------------------------------------------------

    def install(self) -> CommandResult:
        return self.run(self.command("install"))

    def update(self) -> CommandResult:
        return self.run(self.command("upgrade"))

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    def audit(self) -> CommandResult:
        return self.run(self.command("audit"))

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def outdated(self) -> CommandResult:
        return self.run(self.command("outdated"))

    def list_packages(self) -> CommandResult:
        return self.run(
            self.command(
                "list",
                "--depth=0",
            )
        )

    def version(self) -> CommandResult:
        return self.run(self.command("--version"))

    def doctor(self) -> CommandResult:
        return self.run(self.command("doctor"))

    # ---------------------------------------------------------
    # Development
    # ---------------------------------------------------------

    def build(self) -> CommandResult:
        return self.run(
            self.command(
                "run",
                "build",
            )
        )

    def lint(self) -> CommandResult:
        return self.run(
            self.command(
                "run",
                "lint",
            )
        )

    def test(self) -> CommandResult:
        return self.run(
            self.command(
                "test",
            )
        )

    # ---------------------------------------------------------
    # Extras
    # ---------------------------------------------------------

    def add(self, package: str, dev: bool = False) -> CommandResult:
        cmd = ["add"]

        if dev:
            cmd.append("--dev")

        cmd.append(package)

        return self.run(self.command(*cmd))

    def remove(self, package: str) -> CommandResult:
        return self.run(
            self.command(
                "remove",
                package,
            )
        )

    def upgrade_latest(self) -> CommandResult:
        return self.run(
            self.command(
                "upgrade",
                "--latest",
            )
        )

    def cache_clean(self) -> CommandResult:
        return self.run(
            self.command(
                "cache",
                "clean",
            )
        )
