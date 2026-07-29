"""
Darkelf Dependency Guardian

Rollback Manager

Copyright (c) 2026 Darkelf Labs
Licensed under the MIT License.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RollbackResult:
    success: bool
    message: str
    backup_dir: Path | None = None


class RollbackManager:
    """
    Creates and restores project backups before dependency updates.
    """

    FILES_TO_BACKUP = (
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lockb",
    )

    def __init__(
        self,
        project_dir: str | Path = ".",
        backup_root: str | Path = ".guardian/backups",
    ):
        self.project_dir = Path(project_dir).resolve()
        self.backup_root = Path(backup_root).resolve()

    # ---------------------------------------------------------
    # Backup
    # ---------------------------------------------------------

    def create_backup(self) -> RollbackResult:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_dir = self.backup_root / timestamp

        backup_dir.mkdir(parents=True, exist_ok=True)

        copied = 0

        for filename in self.FILES_TO_BACKUP:

            src = self.project_dir / filename

            if src.exists():
                shutil.copy2(src, backup_dir / filename)
                copied += 1

        if copied == 0:
            return RollbackResult(
                False,
                "Nothing to backup.",
            )

        return RollbackResult(
            True,
            f"Backup created ({copied} files).",
            backup_dir,
        )

    # ---------------------------------------------------------
    # Restore
    # ---------------------------------------------------------

    def restore(
        self,
        backup_dir: str | Path,
    ) -> RollbackResult:

        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            return RollbackResult(
                False,
                "Backup not found.",
            )

        restored = 0

        for file in backup_dir.iterdir():

            shutil.copy2(
                file,
                self.project_dir / file.name,
            )

            restored += 1

        return RollbackResult(
            True,
            f"Restored {restored} files.",
            backup_dir,
        )

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def latest_backup(self) -> Path | None:

        if not self.backup_root.exists():
            return None

        backups = sorted(
            self.backup_root.iterdir(),
            reverse=True,
        )

        return backups[0] if backups else None

    def restore_latest(self) -> RollbackResult:

        latest = self.latest_backup()

        if latest is None:
            return RollbackResult(
                False,
                "No backups available.",
            )

        return self.restore(latest)

    def list_backups(self) -> list[Path]:

        if not self.backup_root.exists():
            return []

        return sorted(
            self.backup_root.iterdir(),
            reverse=True,
        )

    def delete_backup(
        self,
        backup_dir: str | Path,
    ) -> RollbackResult:

        backup_dir = Path(backup_dir)

        if not backup_dir.exists():
            return RollbackResult(
                False,
                "Backup not found.",
            )

        shutil.rmtree(backup_dir)

        return RollbackResult(
            True,
            "Backup deleted.",
        )
