"""
Retention utilities for Eternia artifacts and logs.

Provides simple functions to purge old files based on age and patterns.
This complements backup_manager.cleanup_old_backups() for backups.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Iterable
import logging

logger = logging.getLogger(__name__)


def purge_old_files(directory: str | Path, *, older_than_days: int, patterns: Iterable[str] = ("*",)) -> int:
    """
    Delete files in a directory older than the given number of days that match any of the glob patterns.

    Returns number of files deleted. Non-recursive on purpose to avoid surprises.
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.info("Retention: directory does not exist: %s", dir_path)
        return 0

    cutoff = time.time() - older_than_days * 86400
    deleted = 0
    for pattern in patterns:
        for p in dir_path.glob(pattern):
            try:
                if not p.is_file():
                    continue
                if p.stat().st_mtime < cutoff:
                    p.unlink(missing_ok=True)
                    deleted += 1
            except Exception as e:
                logger.warning("Retention: failed to delete %s: %s", p, e)
    if deleted:
        logger.info("Retention: deleted %d files in %s", deleted, dir_path)
    return deleted


def purge_logs(*, older_than_days: int = 7) -> int:
    """
    Purge old log files under logs/ directory.
    """
    return purge_old_files("logs", older_than_days=older_than_days, patterns=("*.log", "*.json", "*.txt"))
