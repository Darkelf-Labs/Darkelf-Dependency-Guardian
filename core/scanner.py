"""
Darkelf Dependency Guardian
Project Scanner
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


FRAMEWORKS = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "svelte": "Svelte",
    "@angular/core": "Angular",
    "electron": "Electron",
    "vite": "Vite",
    "astro": "Astro",
    "nuxt": "Nuxt",
}


@dataclass(slots=True)
class ProjectInfo:
    root: Path
    package_manager: str
    package_name: str
    version: str
    framework: str
    node_engine: str | None
    scripts: dict[str, str] = field(default_factory=dict)
    dependencies: dict[str, str] = field(default_factory=dict)
    dev_dependencies: dict[str, str] = field(default_factory=dict)

    @property
    def all_packages(self) -> dict[str, str]:
        return {**self.dependencies, **self.dev_dependencies}


class ProjectScanner:
    """Scans a JavaScript/TypeScript project."""

    def __init__(self, start: str | Path = "."):
        self.root = self._find_root(Path(start).resolve())

    def _find_root(self, path: Path) -> Path:
        current = path
        while current != current.parent:
            if (current / "package.json").exists():
                return current
            current = current.parent
        raise FileNotFoundError("package.json not found.")

    def _load_package_json(self) -> dict[str, Any]:
        with open(self.root / "package.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def detect_package_manager(self) -> str:
        if (self.root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (self.root / "yarn.lock").exists():
            return "yarn"
        if (self.root / "bun.lockb").exists() or (self.root / "bun.lock").exists():
            return "bun"
        return "npm"

    def detect_framework(self, packages: dict[str, str]) -> str:
        for pkg, name in FRAMEWORKS.items():
            if pkg in packages:
                return name
        return "Unknown"

    def scan(self) -> ProjectInfo:
        pkg = self._load_package_json()

        deps = pkg.get("dependencies", {})
        dev = pkg.get("devDependencies", {})
        all_packages = {**deps, **dev}

        return ProjectInfo(
            root=self.root,
            package_manager=self.detect_package_manager(),
            package_name=pkg.get("name", "unknown"),
            version=pkg.get("version", "0.0.0"),
            framework=self.detect_framework(all_packages),
            node_engine=pkg.get("engines", {}).get("node"),
            scripts=pkg.get("scripts", {}),
            dependencies=deps,
            dev_dependencies=dev,
        )


if __name__ == "__main__":
    scanner = ProjectScanner()
    info = scanner.scan()

    print("=" * 60)
    print("Darkelf Dependency Guardian")
    print("=" * 60)
    print(f"Project         : {info.package_name}")
    print(f"Version         : {info.version}")
    print(f"Framework       : {info.framework}")
    print(f"Package Manager : {info.package_manager}")
    print(f"Node Engine     : {info.node_engine or 'Not specified'}")
    print(f"Dependencies    : {len(info.dependencies)}")
    print(f"Dev Dependencies: {len(info.dev_dependencies)}")
