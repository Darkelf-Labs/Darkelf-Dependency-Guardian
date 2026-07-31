#!/usr/bin/env python3
"""
Darkelf Dependency Guardian
Core Utilities

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess  # nosec B404
import sys
import time
from pathlib import Path

from logger import (
    error,
    info,
    success,
    warning,
)

# ============================================================
# Platform
# ============================================================


def operating_system() -> str:
    return platform.system()


def architecture() -> str:
    return platform.machine()


def python_version() -> str:
    return platform.python_version()


# ============================================================
# Files
# ============================================================


def file_exists(path: str | Path) -> bool:
    return Path(path).exists()


def read_json(path: str | Path) -> dict:

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data: dict):

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            sort_keys=True,
        )


def read_text(path: str | Path) -> str:

    return Path(path).read_text(
        encoding="utf-8",
    )


def write_text(path: str | Path, text: str):

    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(path).write_text(
        text,
        encoding="utf-8",
    )


# ============================================================
# Checksums
# ============================================================


def sha256(path: str | Path) -> str:

    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


# ============================================================
# Command Runner
# ============================================================


def run(
    command: list[str],
    cwd: str | Path | None = None,
    check: bool = False,
):

    if not command:
        raise ValueError("Command cannot be empty.")

    executable = shutil.which(command[0])

    if executable is None:
        raise FileNotFoundError(f"Executable not found: {command[0]}")

    command = [executable, *command[1:]]

    info(f"$ {' '.join(command)}")

    start = time.perf_counter()

    result = subprocess.run(  # nosec B603
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    elapsed = time.perf_counter() - start

    if result.returncode == 0:
        success(f"Completed ({elapsed:.2f}s)")
    else:
        warning(f"Exited with code {result.returncode}")

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result


# ============================================================
# Environment
# ============================================================


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def require(name: str):

    if not command_exists(name):
        error(f"{name} not found.")

        sys.exit(1)


# ============================================================
# npm
# ============================================================


def npm_version() -> str:

    result = run(["npm", "--version"])

    return result.stdout.strip()


def node_version() -> str:

    result = run(["node", "--version"])

    return result.stdout.strip()


# ============================================================
# Timing
# ============================================================


class Stopwatch:
    def __init__(self):

        self.start = time.perf_counter()

    def elapsed(self):

        return time.perf_counter() - self.start


# ============================================================
# Formatting
# ============================================================


def human_bytes(size: int) -> str:

    for unit in (
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ):
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


# ============================================================
# Git
# ============================================================


def git_branch() -> str:

    result = run(
        [
            "git",
            "branch",
            "--show-current",
        ]
    )

    return result.stdout.strip()


def git_clean() -> bool:

    result = run(
        [
            "git",
            "status",
            "--porcelain",
        ]
    )

    return result.stdout.strip() == ""


# ============================================================
# Package
# ============================================================


def package_json() -> dict:

    return read_json("package.json")


def package_name() -> str:

    return package_json().get(
        "name",
        "Unknown",
    )


def package_version() -> str:

    return package_json().get(
        "version",
        "0.0.0",
    )


# ============================================================
# Misc
# ============================================================


def timestamp() -> str:

    return time.strftime(
        "%Y-%m-%d %H:%M:%S",
    )


def ensure_directory(path: str | Path):

    Path(path).mkdir(
        parents=True,
        exist_ok=True,
    )


def getenv(
    name: str,
    default: str = "",
) -> str:

    return os.getenv(
        name,
        default,
    )


# ============================================================
# Version
# ============================================================


def print_environment():

    info(f"OS: {operating_system()}")

    info(f"Python: {python_version()}")

    info(f"Node: {node_version()}")

    info(f"npm: {npm_version()}")

    info(f"Git Branch: {git_branch()}")
