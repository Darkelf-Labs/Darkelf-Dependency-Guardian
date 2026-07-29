"""
Darkelf Dependency Guardian

Package manager backends.
"""

from .base import CommandResult, PackageManager
from .bun import BunManager
from .detect import PackageManagerDetector
from .npm import NpmManager
from .pnpm import PnpmManager
from .yarn import YarnManager

__all__ = [
    "CommandResult",
    "PackageManager",
    "PackageManagerDetector",
    "NpmManager",
    "PnpmManager",
    "YarnManager",
    "BunManager",
]
