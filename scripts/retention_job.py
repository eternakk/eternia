#!/usr/bin/env python3
"""
Retention job for Eternia.

Purges old logs and triggers backup rotation according to environment variables.

Environment variables:
- LOG_RETENTION_DAYS (default: 7)
- BACKUP_RETENTION_DAYS (default: config backup.retention_days or 7)
"""
from __future__ import annotations

import os
import sys
import logging

from modules.retention import purge_logs
from modules.backup_manager import backup_manager
from config.config_manager import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retention_job")


def main() -> int:
    log_days = int(os.getenv("LOG_RETENTION_DAYS", "7"))
    backup_days_env = os.getenv("BACKUP_RETENTION_DAYS")
    if backup_days_env is not None:
        # override runtime config for one-off execution
        try:
            backup_manager.retention_days = int(backup_days_env)
        except ValueError:
            logger.warning("Invalid BACKUP_RETENTION_DAYS, using configured value: %s", backup_days_env)

    deleted_logs = purge_logs(older_than_days=log_days)
    deleted_backups = backup_manager.cleanup_old_backups()

    logger.info("Retention summary: logs=%d, backups=%d", deleted_logs, deleted_backups)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
