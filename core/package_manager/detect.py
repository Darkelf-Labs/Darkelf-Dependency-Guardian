"""
Darkelf Dependency Guardian

Package Manager Detection

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

from .base import PackageManager
from .npm import NpmManager
from .pnpm import PnpmManager

try:
    from .yarn import YarnManager
except ImportError:
    YarnManager = None

try:
    from .bun import BunManager
except ImportError:
    BunManager = None


class PackageManagerDetector:
    """
    Detect the package manager used by a project.

    Detection priority:

        bun.lockb
        pnpm-lock.yaml
        yarn.lock
        package-lock.json

    Fallback: npm
    """

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir)

    def detect_name(self) -> str:

        if (self.project_dir / "bun.lockb").exists():
            return "bun"

        if (self.project_dir / "pnpm-lock.yaml").exists():
            return "pnpm"

        if (self.project_dir / "yarn.lock").exists():
            return "yarn"

        if (self.project_dir / "package-lock.json").exists():
            return "npm"

        return "npm"

    def detect(self) -> PackageManager:

        name = self.detect_name()

        if name == "pnpm":
            return PnpmManager(self.project_dir)

        if name == "yarn" and YarnManager:
            return YarnManager(self.project_dir)

        if name == "bun" and BunManager:
            return BunManager(self.project_dir)

        return NpmManager(self.project_dir)

    @staticmethod
    def supported() -> list[str]:
        return [
            "npm",
            "pnpm",
            "yarn",
            "bun",
        ]
