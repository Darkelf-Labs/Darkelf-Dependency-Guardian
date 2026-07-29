"""
Darkelf Dependency Guardian

Bun Package Manager

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

from .base import CommandResult, PackageManager


class BunManager(PackageManager):
    """
    Bun package manager implementation.
    """

    name = "bun"
    executable = "bun"

    def __init__(self, project_dir: str | Path = "."):
        super().__init__(project_dir)

    # ---------------------------------------------------------
    # Installation
    # ---------------------------------------------------------

    def install(self) -> CommandResult:
        return self.run(self.command("install"))

    def update(self) -> CommandResult:
        return self.run(self.command("update"))

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    def audit(self) -> CommandResult:
        """
        Bun does not currently provide a native audit command.
        Fall back to npm audit.
        """
        return self.run(["npm", "audit"])

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def outdated(self) -> CommandResult:
        """
        Bun currently has no native 'outdated' command.
        """
        return self.run(["npm", "outdated", "--json"])

    def list_packages(self) -> CommandResult:
        return self.run(self.command("pm", "ls"))

    def version(self) -> CommandResult:
        return self.run(self.command("--version"))

    def doctor(self) -> CommandResult:
        """
        Bun has no doctor command.
        Return version information instead.
        """
        return self.version()

    # ---------------------------------------------------------
    # Development
    # ---------------------------------------------------------

    def build(self) -> CommandResult:
        return self.run(self.command("run", "build"))

    def lint(self) -> CommandResult:
        return self.run(self.command("run", "lint"))

    def test(self) -> CommandResult:
        return self.run(self.command("test"))

    # ---------------------------------------------------------
    # Package Management
    # ---------------------------------------------------------

    def add(
        self,
        package: str,
        dev: bool = False,
    ) -> CommandResult:

        cmd = ["add"]

        if dev:
            cmd.append("--dev")

        cmd.append(package)

        return self.run(self.command(*cmd))

    def remove(
        self,
        package: str,
    ) -> CommandResult:

        return self.run(
            self.command(
                "remove",
                package,
            )
        )

    # ---------------------------------------------------------
    # Cache / Maintenance
    # ---------------------------------------------------------

    def cache_clean(self) -> CommandResult:
        """
        Bun automatically manages its cache.
        No-op for compatibility.
        """
        return self.version()

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def exec(
        self,
        *args: str,
    ) -> CommandResult:

        return self.run(
            self.command(
                "x",
                *args,
            )
        )

    def why(
        self,
        package: str,
    ) -> CommandResult:

        return self.run(
            self.command(
                "why",
                package,
            )
        )
