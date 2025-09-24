#!/usr/bin/env python3
"""
Disaster recovery helper for Eternia.

Provides simple commands to create a backup and verify backup availability.
This complements scripts/restore_backup.py which performs interactive restores.

Usage:
  python scripts/disaster_recovery.py create   # create a backup now
  python scripts/disaster_recovery.py verify   # verify at least one backup exists and is readable
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

from modules.backup_manager import backup_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disaster_recovery")


def cmd_create() -> int:
    try:
        path = backup_manager.create_backup()
        if path:
            logger.info("Backup created at: %s", path)
            return 0
        logger.error("Backup creation failed")
        return 2
    except Exception as e:
        logger.exception("Backup creation error: %s", e)
        return 3


def cmd_verify() -> int:
    try:
        backups = backup_manager.list_backups()
        if not backups:
            logger.error("No backups found")
            return 2
        latest = backups[0]
        p = Path(latest["path"])  # type: ignore[index]
        if not p.exists() or p.stat().st_size <= 0:
            logger.error("Latest backup is missing or empty: %s", p)
            return 2
        logger.info("Latest backup OK: %s (%.2f MB)", p, p.stat().st_size / (1024 * 1024))
        return 0
    except Exception as e:
        logger.exception("Verification failed: %s", e)
        return 3


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "create":
        return cmd_create()
    if cmd == "verify":
        return cmd_verify()
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
