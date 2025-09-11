"""
Migration manager for Eternia database.

This module provides a migration manager for the Eternia database using yoyo-migrations.
It handles database schema migrations, tracking applied migrations, and providing
migration status information.
"""

import logging
import os
from typing import List, Optional, Tuple

from yoyo import read_migrations, get_backend
from yoyo.migrations import Migration

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Migration manager for Eternia database.

    This class provides methods for managing database schema migrations using
    yoyo-migrations. It handles applying migrations, rolling back migrations,
    and checking migration status.

    Attributes:
        db_path: Path to the SQLite database file.
        migrations_path: Path to the directory containing migration scripts.
        backend: Yoyo backend for the database.
        migrations: List of available migrations.
    """

    def __init__(self, db_path: str, migrations_path: str = "migrations"):
        """
        Initialize the migration manager.

        Args:
            db_path: Path to the SQLite database file.
            migrations_path: Path to the directory containing migration scripts.
                Defaults to "migrations".
        """
        self.db_path = db_path
        self.migrations_path = migrations_path
        self.backend = self._get_backend()
        self.migrations = self._get_migrations()

    def _get_backend(self):
        """Get the yoyo backend for the database."""
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Create the database connection string
        db_uri = f"sqlite:///{self.db_path}"

        # Get the backend
        return get_backend(db_uri)

    def _get_migrations(self) -> List[Migration]:
        """Get the list of available migrations."""
        # Ensure the migrations directory exists
        if not os.path.exists(self.migrations_path):
            logger.warning(f"Migrations directory not found: {self.migrations_path}")
            return []

        # Get the migrations
        return read_migrations(self.migrations_path)

    def apply_migrations(self, target: Optional[str] = None) -> int:
        """
        Apply pending migrations.

        Args:
            target: Target migration ID to migrate to. If None, apply all
                pending migrations. Defaults to None.

        Returns:
            int: Number of migrations applied.
        """
        # Get the migrations to apply
        if target:
            migrations_to_apply = self._get_migrations_to_target(target)
        else:
            migrations_to_apply = self.migrations

        # Apply the migrations
        with self.backend.lock():
            count = 0
            for migration in migrations_to_apply:
                if self.backend.is_applied(migration):
                    continue

                logger.info(f"Applying migration: {migration.id}")
                migration.process_steps(self.backend, "apply", force=False)
                count += 1

            if count > 0:
                logger.info(f"Applied {count} migrations")
            else:
                logger.info("No migrations to apply")

            return count

    def rollback_migrations(self, target: Optional[str] = None, steps: int = 1) -> int:
        """
        Roll back applied migrations.

        Args:
            target: Target migration ID to rollback to. If None, rollback the
                specified number of steps. Defaults to None.
            steps: Number of migrations to roll back. Defaults to 1.

        Returns:
            int: Number of migrations rolled back.
        """
        # Get the migrations to roll back
        if target:
            migrations_to_rollback = self._get_migrations_to_rollback_target(target)
        else:
            migrations_to_rollback = self._get_migrations_to_rollback_steps(steps)

        # Roll back the migrations
        with self.backend.lock():
            count = 0
            for migration in migrations_to_rollback:
                if not self.backend.is_applied(migration):
                    continue

                logger.info(f"Rolling back migration: {migration.id}")
                migration.process_steps(self.backend, "rollback", force=False)
                count += 1

            if count > 0:
                logger.info(f"Rolled back {count} migrations")
            else:
                logger.info("No migrations to roll back")

            return count

    def _get_migrations_to_target(self, target: str) -> List[Migration]:
        """
        Get the list of migrations to apply to reach the target.

        Args:
            target: Target migration ID.

        Returns:
            List of migrations to apply.
        """
        # Find the target migration
        target_migration = None
        for migration in self.migrations:
            if migration.id == target:
                target_migration = migration
                break

        if not target_migration:
            logger.warning(f"Target migration not found: {target}")
            return []

        # Get all migrations up to and including the target
        migrations_to_apply = []
        for migration in self.migrations:
            migrations_to_apply.append(migration)
            if migration.id == target:
                break

        return migrations_to_apply

    def _get_migrations_to_rollback_target(self, target: str) -> List[Migration]:
        """
        Get the list of migrations to roll back to reach the target.

        Args:
            target: Target migration ID.

        Returns:
            List of migrations to roll back.
        """
        # Find the target migration
        target_index = -1
        for i, migration in enumerate(self.migrations):
            if migration.id == target:
                target_index = i
                break

        if target_index == -1:
            logger.warning(f"Target migration not found: {target}")
            return []

        # Get all migrations after the target, in reverse order
        migrations_to_rollback = list(reversed(self.migrations[target_index + 1:]))

        return migrations_to_rollback

    def _get_migrations_to_rollback_steps(self, steps: int) -> List[Migration]:
        """
        Get the list of migrations to roll back the specified number of steps.

        Args:
            steps: Number of migrations to roll back.

        Returns:
            List of migrations to roll back.
        """
        # Get the applied migrations
        applied_migrations = [m for m in self.migrations if self.backend.is_applied(m)]

        # Get the migrations to roll back, in reverse order
        migrations_to_rollback = list(reversed(applied_migrations))[:steps]

        return migrations_to_rollback

    def get_migration_status(self) -> List[Tuple[str, bool, str]]:
        """
        Get the status of all migrations.

        Returns:
            List of tuples containing (migration_id, is_applied, description).
        """
        status = []
        for migration in self.migrations:
            is_applied = self.backend.is_applied(migration)
            status.append((migration.id, is_applied, migration.path))

        return status

    def get_current_version(self) -> Optional[str]:
        """
        Get the ID of the most recently applied migration.

        Returns:
            ID of the most recently applied migration, or None if no migrations
            have been applied.
        """
        applied_migrations = [m for m in self.migrations if self.backend.is_applied(m)]
        if not applied_migrations:
            return None

        return applied_migrations[-1].id

    def create_migration(self, name: str) -> str:
        """
        Create a new migration file.

        Args:
            name: Name of the migration.

        Returns:
            Path to the created migration file.
        """
        # Ensure the migrations directory exists
        os.makedirs(self.migrations_path, exist_ok=True)

        # Generate a migration ID
        import datetime

        migration_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the migration file
        filename = f"{migration_id}_{name}.py"
        filepath = os.path.join(self.migrations_path, filename)

        with open(filepath, "w") as f:
            f.write(
                f'''"""
{name.replace("_", " ").title()}.

This migration [describe what this migration does].
"""

from yoyo import step

__depends__ = {{}}

steps = [
    step(
        """
        -- Write your forward SQL here
        """,
        """
        -- Write your rollback SQL here
        """
    )
]
'''
            )

        logger.info(f"Created migration file: {filepath}")
        return filepath
