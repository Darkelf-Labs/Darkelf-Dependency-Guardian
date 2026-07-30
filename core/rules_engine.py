"""
Darkelf Dependency Guardian
Enhanced Rules Engine
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


@dataclass(slots=True)
class Rule:
    package: str
    allowed: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    replacement: str = ""
    severity: str = "high"
    reason: str = ""


@dataclass(slots=True)
class RuleResult:
    allowed: bool
    package: str
    version: str
    severity: str
    reason: str
    replacement: str = ""
    
@lru_cache(maxsize=64)
def _load_rules_file(path: str) -> dict:
    file = Path(path)

    if not file.exists():
        raise FileNotFoundError(file)

    data = json.loads(file.read_text(encoding="utf-8"))

    if "packages" not in data:
        raise ValueError(
            f"Invalid schema: {file.name} (missing 'packages')"
        )

    return data


class RulesEngine:
    def __init__(
        self,
        rules_dir: str | Path | None = None,
        mode: str = "strict",
    ):
        self.mode = mode.lower()

        if rules_dir is None:
            self.rules_dir = Path(__file__).resolve().parent.parent / "rules"
        else:
            self.rules_dir = Path(rules_dir)

    @staticmethod
    def _major(version: str) -> str:
        m = re.search(r"\d+", version or "")
        return m.group(0) if m else "0"

    def get_rules(self, framework: str) -> list[Rule]:

        data = self.load(framework)

        packages = data.get("packages", {})
        blocked = data.get("blocked", {})

        rules = []

        for package, allowed in packages.items():

            if isinstance(allowed, str):
                allowed = [allowed]

            blocked_versions = []
            reason = ""

            for item in blocked.get(package, []):

                blocked_versions.append(item.get("version", ""))

                if not reason:
                    reason = item.get("reason", "")

            rules.append(
                Rule(
                    package=package,
                    allowed=allowed,
                    blocked=blocked_versions,
                    severity="high",
                    reason=reason,
                )
            )

        return rules

    def find_rule(self, framework: str, package: str) -> Rule | None:
        return next(
            (r for r in self.get_rules(framework) if r.package == package), None
        )

    def check_dependency(
        self, framework: str, package: str, version: str
    ) -> RuleResult:
        rule = self.find_rule(framework, package)
        if rule is None:
            return RuleResult(True, package, version, "info", "No compatibility rule.")

        installed_major = self._major(version)

        for blocked in rule.blocked:

            blocked_major = self._major(blocked)

            if blocked_major == installed_major:
                return RuleResult(
                    False,
                    package,
                    version,
                    rule.severity,
                    rule.reason or "Blocked version.",
                    rule.replacement,
                )

        if rule.allowed:
            allowed_majors = {self._major(v) for v in rule.allowed}

            if installed_major not in allowed_majors:

                if self.mode == "permissive":
                    return RuleResult(
                        True,
                        package,
                        version,
                        "warning",
                        "Outside tested compatibility range.",
                        rule.replacement,
                    )

                return RuleResult(
                    False,
                    package,
                    version,
                    rule.severity,
                    rule.reason or "Unsupported version.",
                    rule.replacement,
                )

        return RuleResult(True, package, version, "info", "Compatible.")

    def is_allowed(
        self,
        framework: str,
        package: str,
        version: str,
    ) -> tuple[bool, str]:
        """
        Backwards-compatible wrapper for older Guardian modules.
        """
        result = self.check_dependency(framework, package, version)
        return result.allowed, result.reason

    def list_frameworks(self) -> list[str]:

        return (
            sorted(p.stem for p in self.rules_dir.glob("*.json"))
            if self.rules_dir.exists()
            else []
        )
