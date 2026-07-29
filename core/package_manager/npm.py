"""
Darkelf Dependency Guardian
npm Package Manager Backend
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(slots=True)
class CommandResult:
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float


class NpmManager:
    """Wrapper around npm."""

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir).resolve()

    def _run(
        self,
        args: List[str],
        timeout: int = 600,
    ) -> CommandResult:
        """Execute an npm command."""

        start = time.perf_counter()

        try:
            proc = subprocess.run(
                ["npm", *args],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            duration = time.perf_counter() - start

            return CommandResult(
                success=proc.returncode == 0,
                exit_code=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
                duration=duration,
            )

        except subprocess.TimeoutExpired as exc:
            duration = time.perf_counter() - start

            return CommandResult(
                success=False,
                exit_code=-1,
                stdout=exc.stdout or "",
                stderr=f"Command timed out after {timeout} seconds.",
                duration=duration,
            )

        except FileNotFoundError:
            duration = time.perf_counter() - start

            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="npm executable not found.",
                duration=duration,
            )

    #
    # Core Commands
    #

    def install(self) -> CommandResult:
        return self._run(["install"])

    def ci(self) -> CommandResult:
        return self._run(["ci"])

    def update(self) -> CommandResult:
        return self._run(["update"])

    def audit(self) -> CommandResult:
        return self._run(["audit"])

    def audit_fix(self) -> CommandResult:
        return self._run(["audit", "fix"])

    def outdated(self) -> CommandResult:
        return self._run(["outdated"])

    def lint(self) -> CommandResult:
        return self._run(["run", "lint"])

    def build(self) -> CommandResult:
        return self._run(["run", "build"])

    def test(self) -> CommandResult:
        return self._run(["test"])

    def doctor(self) -> CommandResult:
        return self._run(["doctor"])

    def version(self) -> CommandResult:
        return self._run(["--version"])

    def list_packages(self, depth: int = 0) -> CommandResult:
        return self._run(
            [
                "list",
                "--json",
                f"--depth={depth}",
            ]
        )

    def list_top_level(self) -> CommandResult:
        return self.list_packages(depth=0)
