"""
Darkelf Dependency Guardian
PNPM Package Manager
"""

from __future__ import annotations

from pathlib import Path

from .base import PackageManager, CommandResult


class PnpmManager(PackageManager):
    """pnpm package manager implementation."""

    executable = "pnpm"

    def __init__(self, project_dir: str | Path = "."):
        super().__init__(project_dir)

    # ---------------------------------------------------------
    # Installation
    # ---------------------------------------------------------

    def install(self) -> CommandResult:
        return self.run(["pnpm", "install"])

    def ci(self) -> CommandResult:
        return self.run(["pnpm", "install", "--frozen-lockfile"])

    def update(self) -> CommandResult:
        return self.run(["pnpm", "update"])

    def upgrade(self) -> CommandResult:
        return self.run(["pnpm", "update", "--latest"])

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    def audit(self) -> CommandResult:
        return self.run(["pnpm", "audit"])

    def audit_fix(self) -> CommandResult:
        return self.run(["pnpm", "audit", "--fix"])

    # ---------------------------------------------------------
    # Dependency Inspection
    # ---------------------------------------------------------

    def outdated(self) -> CommandResult:
        return self.run(["pnpm", "outdated", "--json"])

    def list(self) -> CommandResult:
        return self.run(["pnpm", "list", "--depth", "0"])

    def doctor(self) -> CommandResult:
        return self.run(["pnpm", "doctor"])

    # ---------------------------------------------------------
    # Development
    # ---------------------------------------------------------

    def lint(self) -> CommandResult:
        return self.run(["pnpm", "run", "lint"])

    def build(self) -> CommandResult:
        return self.run(["pnpm", "run", "build"])

    def test(self) -> CommandResult:
        return self.run(["pnpm", "test"])

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def version(self) -> CommandResult:
        return self.run(["pnpm", "--version"])

    # ---------------------------------------------------------
    # Maintenance
    # ---------------------------------------------------------

    def clean_cache(self) -> CommandResult:
        return self.run(["pnpm", "store", "prune"])

    def prune(self) -> CommandResult:
        return self.run(["pnpm", "prune"])

    def dedupe(self) -> CommandResult:
        return self.run(["pnpm", "dedupe"])

    # ---------------------------------------------------------
    # Package Operations
    # ---------------------------------------------------------

    def add(self, package: str, dev: bool = False) -> CommandResult:
        cmd = ["pnpm", "add"]

        if dev:
            cmd.append("-D")

        cmd.append(package)

        return self.run(cmd)

    def remove(self, package: str) -> CommandResult:
        return self.run(["pnpm", "remove", package])

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def exec(self, *args: str) -> CommandResult:
        return self.run(["pnpm", "exec", *args])

    def why(self, package: str) -> CommandResult:
        return self.run(["pnpm", "why", package])

    def store_status(self) -> CommandResult:
        return self.run(["pnpm", "store", "status"])
