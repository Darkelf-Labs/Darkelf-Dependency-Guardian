
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


class RulesEngine:
    """Framework compatibility rule loader."""

    def __init__(self, rules_dir: str | Path = "rules"):
        self.rules_dir = Path(rules_dir)

    @staticmethod
    def _major(version: str) -> str:
        m = re.search(r"\d+", version or "")
        return m.group(0) if m else "0"

    @lru_cache(maxsize=64)
    def load(self, framework: str) -> dict:
        path = self.rules_dir / f"{framework.lower()}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        if "rules" not in data or not isinstance(data["rules"], list):
            raise ValueError(f"Invalid schema: {path.name}")
        return data

    def get_rules(self, framework: str) -> list[Rule]:
        return [
            Rule(
                package=i["package"],
                allowed=i.get("allowed", []),
                blocked=i.get("blocked", []),
                replacement=i.get("replacement", ""),
                severity=i.get("severity", "high"),
                reason=i.get("reason", ""),
            )
            for i in self.load(framework)["rules"]
        ]

    def find_rule(self, framework: str, package: str) -> Rule | None:
        return next((r for r in self.get_rules(framework) if r.package == package), None)

    def check_dependency(self, framework: str, package: str, version: str) -> RuleResult:
        rule = self.find_rule(framework, package)
        if rule is None:
            return RuleResult(True, package, version, "info", "No compatibility rule.")

        major = self._major(version)

        for blocked in rule.blocked:
            if self._major(blocked) == major:
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
            if major not in allowed_majors:
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
    
        return sorted(p.stem for p in self.rules_dir.glob("*.json")) if self.rules_dir.exists() else []
