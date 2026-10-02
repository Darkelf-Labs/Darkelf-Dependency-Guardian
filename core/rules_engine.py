"""Darkelf Dependency Guardian - stable npm version-range checks.

Supports exact stable versions, partial versions, ^, ~, comparisons,
wildcards, hyphen ranges and || alternatives. Declared dependency ranges
must fit entirely inside the allowed ranges and avoid blocked ranges.
Prereleases, tags, URLs and workspace protocols require separate resolution;
they return an unverified result instead of being treated as compatible.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

Version = tuple[int, int, int]
Interval = tuple[Version, Version | None]
ZERO: Version = (0, 0, 0)


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


def _partial(value: str) -> tuple[Version, int]:
    value = value.removeprefix("v")
    parts = value.split(".")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Unsupported version expression: {value!r}")

    numbers = []
    wildcard = False
    for part in parts:
        if part.lower() in {"x", "*"}:
            wildcard = True
        elif wildcard or not re.fullmatch(r"0|[1-9]\d*", part):
            raise ValueError(f"Unsupported version expression: {value!r}")
        else:
            numbers.append(int(part))

    precision = len(numbers)
    return tuple(numbers + [0] * (3 - precision)), precision


def _upper(version: Version, precision: int) -> Version | None:
    major, minor, patch = version
    if precision == 0:
        return None
    if precision == 1:
        return major + 1, 0, 0
    if precision == 2:
        return major, minor + 1, 0
    return major, minor, patch + 1


def _intersection(left: Interval, right: Interval) -> Interval | None:
    low = max(left[0], right[0])
    ends = [end for end in (left[1], right[1]) if end is not None]
    high = min(ends) if ends else None
    return (low, high) if high is None or low < high else None


def _merge(intervals: list[Interval]) -> list[Interval]:
    merged: list[Interval] = []

    for low, high in sorted(intervals, key=lambda item: item[0]):
        if high is not None and low >= high:
            continue

        if not merged or (
            merged[-1][1] is not None and low > merged[-1][1]
        ):
            merged.append((low, high))
            continue

        previous_low, previous_high = merged[-1]
        new_high = (
            None
            if previous_high is None or high is None
            else max(previous_high, high)
        )
        merged[-1] = previous_low, new_high

    return merged


def _token_interval(token: str) -> Interval:
    match = re.fullmatch(r"(>=|<=|>|<|=|\^|~)?(.+)", token)
    if match is None:
        raise ValueError(f"Unsupported range token: {token!r}")

    operator, value = match.groups()
    version, precision = _partial(value)
    upper = _upper(version, precision)

    if precision == 0:
        if operator in (None, "=", "^", "~", ">=", "<="):
            return ZERO, None
        return ZERO, ZERO

    if operator in (None, "="):
        return version, upper
    if operator == ">=":
        return version, None
    if operator == ">":
        return upper, None
    if operator == "<":
        return ZERO, version
    if operator == "<=":
        return ZERO, upper

    major, minor, patch = version

    if operator == "~":
        return (
            version,
            (major + 1, 0, 0)
            if precision == 1
            else (major, minor + 1, 0),
        )

    if major > 0 or precision == 1:
        return version, (major + 1, 0, 0)
    if minor > 0 or precision == 2:
        return version, (major, minor + 1, 0)
    return version, (major, minor, patch + 1)


@lru_cache(maxsize=256)
def _parse_range(expression: str) -> tuple[Interval, ...]:
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Missing version expression")

    intervals = []

    for alternative in expression.strip().split("||"):
        alternative = alternative.strip()
        if not alternative:
            raise ValueError("Empty range alternative")

        hyphen = re.fullmatch(r"(\S+)\s+-\s+(\S+)", alternative)
        if hyphen:
            low, _ = _partial(hyphen.group(1))
            high_version, precision = _partial(hyphen.group(2))
            intervals.append(
                (low, _upper(high_version, precision))
            )
            continue

        alternative = re.sub(
            r"(>=|<=|>|<|=|\^|~)\s+",
            r"\1",
            alternative,
        )
        combined: Interval | None = (ZERO, None)

        for token in alternative.split():
            interval = _token_interval(token)
            if combined is not None:
                combined = _intersection(combined, interval)

        if combined is not None:
            intervals.append(combined)

    return tuple(_merge(intervals))


def _covered(requested: Interval, allowed: Interval) -> bool:
    low, high = requested
    allowed_low, allowed_high = allowed

    return low >= allowed_low and (
        allowed_high is None
        or (high is not None and high <= allowed_high)
    )


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
        self.rules_dir = (
            Path(__file__).resolve().parent.parent / "rules"
            if rules_dir is None
            else Path(rules_dir)
        )

    def load(self, framework: str) -> dict:
        return _load_rules_file(
            str(self.rules_dir / f"{framework.lower()}.json")
        )

    def get_rules(self, framework: str) -> list[Rule]:
        data = self.load(framework)
        rules = []

        for package, allowed in data.get("packages", {}).items():
            if isinstance(allowed, str):
                allowed = [allowed]

            blocked_items = data.get("blocked", {}).get(package, [])

            rules.append(
                Rule(
                    package=package,
                    allowed=allowed,
                    blocked=[
                        item.get("version", "")
                        for item in blocked_items
                    ],
                    reason=next(
                        (
                            item.get("reason", "")
                            for item in blocked_items
                            if item.get("reason")
                        ),
                        "",
                    ),
                )
            )

        return rules

    def find_rule(
        self,
        framework: str,
        package: str,
    ) -> Rule | None:
        return next(
            (
                rule
                for rule in self.get_rules(framework)
                if rule.package == package
            ),
            None,
        )

    def check_dependency(
        self,
        framework: str,
        package: str,
        version: str,
    ) -> RuleResult:
        rule = self.find_rule(framework, package)

        if rule is None:
            return RuleResult(
                True,
                package,
                version,
                "info",
                "No compatibility rule.",
            )

        try:
            requested = _parse_range(version)

            if not requested:
                raise ValueError(
                    "Expression contains no stable versions"
                )

            blocked = [
                interval
                for expression in rule.blocked
                for interval in _parse_range(expression)
            ]

            allowed = _merge(
                [
                    interval
                    for expression in rule.allowed
                    for interval in _parse_range(expression)
                ]
            )

        except (ValueError, TypeError) as error:
            return RuleResult(
                False,
                package,
                version,
                "high",
                f"Cannot verify dependency or rule: {error}. "
                "Resolve an exact stable version.",
                rule.replacement,
            )

        if any(
            _intersection(candidate, block) is not None
            for candidate in requested
            for block in blocked
        ):
            return RuleResult(
                False,
                package,
                version,
                rule.severity,
                rule.reason
                or "Version expression includes blocked versions.",
                rule.replacement,
            )

        if rule.allowed and not all(
            any(
                _covered(candidate, accepted)
                for accepted in allowed
            )
            for candidate in requested
        ):
            permissive = self.mode == "permissive"

            return RuleResult(
                permissive,
                package,
                version,
                "warning" if permissive else rule.severity,
                "Outside tested compatibility range.",
                rule.replacement,
            )

        return RuleResult(
            True,
            package,
            version,
            "info",
            "Compatible.",
        )

    def is_allowed(
        self,
        framework: str,
        package: str,
        version: str,
    ) -> tuple[bool, str]:
        result = self.check_dependency(
            framework,
            package,
            version,
        )
        return result.allowed, result.reason

    def list_frameworks(self) -> list[str]:
        if not self.rules_dir.exists():
            return []

        return sorted(
            path.stem
            for path in self.rules_dir.glob("*.json")
        )
