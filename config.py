#!/usr/bin/env python3
"""
Darkelf Dependency Guardian
Configuration

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

# ============================================================
# Project
# ============================================================

APP_NAME = "Darkelf Dependency Guardian"
VERSION = "1.0.0"
AUTHOR = "Darkelf Labs"

# ============================================================
# Paths
# ============================================================

ROOT = Path.cwd()

PACKAGE_JSON = ROOT / "package.json"
PACKAGE_LOCK = ROOT / "package-lock.json"

NODE_MODULES = ROOT / "node_modules"

REPORTS = ROOT / "guardian_reports"

CACHE = ROOT / ".guardian"

RULES = ROOT / "rules"

BACKUPS = CACHE / "backups"

LOGS = CACHE / "logs"

# ============================================================
# Output Files
# ============================================================

MARKDOWN_REPORT = REPORTS / "dependency_report.md"

JSON_REPORT = REPORTS / "dependency_report.json"

HTML_REPORT = REPORTS / "dependency_report.html"

SARIF_REPORT = REPORTS / "dependency_report.sarif"

LOG_FILE = LOGS / "guardian.log"

# ============================================================
# Git
# ============================================================

DEFAULT_BRANCH = "main"

AUTO_COMMIT = False

AUTO_PUSH = False

AUTO_PR = False

ROLLBACK_ON_FAILURE = True

# ============================================================
# Safety
# ============================================================

SAFE_MODE = True

VERIFY_BUILD = True

VERIFY_LINT = True

VERIFY_TESTS = True

ALLOW_MAJOR_UPDATES = False

ALLOW_FRAMEWORK_DOWNGRADE = False

ALLOW_FORCE_INSTALL = False

ALLOW_AUDIT_FORCE = False

# ============================================================
# npm Commands
# ============================================================

NPM_INSTALL = ["npm", "install"]

NPM_UPDATE = ["npm", "update"]

NPM_AUDIT = ["npm", "audit"]

NPM_OUTDATED = ["npm", "outdated"]

NPM_LINT = ["npm", "run", "lint"]

NPM_BUILD = ["npm", "run", "build"]

NPM_TEST = ["npm", "test"]

# ============================================================
# Scoring
# ============================================================

MAX_SCORE = 100

PENALTY_BUILD_FAIL = 40

PENALTY_LINT_FAIL = 20

PENALTY_SECURITY = 10

PENALTY_OUTDATED = 2

# ============================================================
# Compatibility
# ============================================================

SUPPORTED = {
    "next": {
        "typescript": ">=5 <6.1",
        "eslint": "^9",
    },
    "react": {
        "minimum": "19",
    },
}

# ============================================================
# Colors
# ============================================================

GREEN = "\033[92m"

RED = "\033[91m"

YELLOW = "\033[93m"

BLUE = "\033[94m"

CYAN = "\033[96m"

RESET = "\033[0m"

# ============================================================
# Helpers
# ============================================================


def initialize() -> None:
    """
    Create Guardian working directories.
    """

    REPORTS.mkdir(exist_ok=True)

    CACHE.mkdir(exist_ok=True)

    BACKUPS.mkdir(exist_ok=True)

    LOGS.mkdir(exist_ok=True)


def banner() -> str:
    return f"{APP_NAME} v{VERSION}"
