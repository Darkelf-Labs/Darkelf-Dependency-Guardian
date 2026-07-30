#!/usr/bin/env python3
"""
Darkelf Dependency Guardian
Logger

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

import logging
import sys
import time

from config import LOG_FILE, LOGS

# ============================================================
# Colors
# ============================================================


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


# ============================================================
# Log Initialization
# ============================================================

LOGS.mkdir(parents=True, exist_ok=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Color.BLUE,
        logging.INFO: Color.GREEN,
        logging.WARNING: Color.YELLOW,
        logging.ERROR: Color.RED,
        logging.CRITICAL: Color.RED,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Color.WHITE)
        message = super().format(record)
        return f"{color}{message}{Color.RESET}"


logger = logging.getLogger("guardian")
logger.setLevel(logging.DEBUG)

if not logger.handlers:

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    console.setFormatter(ColoredFormatter("%(levelname)-8s %(message)s"))

    logfile = logging.FileHandler(LOG_FILE, encoding="utf-8")
    logfile.setLevel(logging.DEBUG)

    logfile.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(console)
    logger.addHandler(logfile)


# ============================================================
# Helper Functions
# ============================================================


def info(message: str):
    logger.info(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def debug(message: str):
    logger.debug(message)


def critical(message: str):
    logger.critical(message)


def success(message: str):
    logger.info("✓ %s", message)


def failure(message: str):
    logger.error("✗ %s", message)


def header(title: str):
    line = "=" * 70
    logger.info(line)
    logger.info(title)
    logger.info(line)


def separator():
    logger.info("-" * 70)


# ============================================================
# Timer
# ============================================================


class Timer:

    def __init__(self, label: str):
        self.label = label
        self.start = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        info(f"Starting {self.label}")
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - self.start

        if exc:
            failure(f"{self.label} failed ({elapsed:.2f}s)")
        else:
            success(f"{self.label} completed ({elapsed:.2f}s)")


# ============================================================
# GitHub Actions
# ============================================================


def github_notice(message: str):
    print(f"::notice::{message}")


def github_warning(message: str):
    print(f"::warning::{message}")


def github_error(message: str):
    print(f"::error::{message}")


# ============================================================
# Exception Logger
# ============================================================


def exception(exc: Exception):
    logger.exception(exc)


# ============================================================
# Session Header
# ============================================================


def startup(app_name: str, version: str):

    header(f"{app_name} v{version}")

    info(f"Log file: {LOG_FILE}")
