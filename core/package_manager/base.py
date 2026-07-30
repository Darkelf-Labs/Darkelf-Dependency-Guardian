"""
Darkelf Dependency Guardian

Base Package Manager

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CommandResult:
    """
    Standard result returned by every package manager command.
    """

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float


class PackageManager(ABC):
    """
    Base interface for all supported package managers.

    Every implementation should only define the commands.
    Execution is handled here.
    """

    name: str = "unknown"
    executable: str = ""

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir)

    # ---------------------------------------------------------
    # Shared Helpers
    # ---------------------------------------------------------

    def exists(self) -> bool:
        """Return True if the executable exists."""
        return shutil.which(self.executable) is not None

    def command(self, *args: str) -> list[str]:
        """Build a command using the configured executable."""
        return [self.executable, *args]

    def run(self, command: list[str]) -> CommandResult:
        """
        Execute a command and return a standardized result.
        """

        start = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            duration = time.perf_counter() - start

            return CommandResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                duration=duration,
            )

        except Exception as exc:
            duration = time.perf_counter() - start

            return CommandResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(exc),
                duration=duration,
            )

    # ---------------------------------------------------------
    # Required API
    # ---------------------------------------------------------

    @abstractmethod
    def install(self) -> CommandResult: ...

    @abstractmethod
    def update(self) -> CommandResult: ...

    @abstractmethod
    def audit(self) -> CommandResult: ...

    @abstractmethod
    def outdated(self) -> CommandResult: ...

    @abstractmethod
    def build(self) -> CommandResult: ...

    @abstractmethod
    def lint(self) -> CommandResult: ...

    @abstractmethod
    def test(self) -> CommandResult: ...

    @abstractmethod
    def list_packages(self) -> CommandResult: ...

    @abstractmethod
    def version(self) -> CommandResult: ...

    @abstractmethod
    def doctor(self) -> CommandResult: ...
