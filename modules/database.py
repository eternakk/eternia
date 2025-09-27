"""
Database module for Eternia.

This module provides a database schema and operations for persistent storage of the Eternia state.
It uses SQLite as the database engine for simplicity and portability.
"""

import datetime
import json
import logging
import os
import sqlite3
import time
from typing import List, Optional, Tuple

from pathlib import Path
from modules.migration_manager import MigrationManager

logger = logging.getLogger(__name__)


def _iso_from_timestamp(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_from_iso(value: str) -> Optional[float]:
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(value).timestamp()
    except Exception:
        return None


class EternaDatabase:
    """
    Database manager for Eternia state persistence.

    This class provides methods for creating, updating, and querying the database
    that stores the Eternia state. It uses SQLite as the database engine.

    Attributes:
        db_path: Path to the SQLite database file.
        conn: SQLite connection object.
        cursor: SQLite cursor object.
        schema_version: Current version of the database schema.
    """

    # Schema version expected by application-level serialization/export
    SCHEMA_VERSION = 1

    def __init__(self, db_path="data/eternia.db", migrations_path="migrations"):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file. Defaults to "data/eternia.db".
            migrations_path: Path to the directory containing migration scripts.
                Defaults to "migrations".
        """
        self.db_path = db_path
        self._ensure_dir_exists()
        self.conn = None
        self.cursor = None
        self._connect()

        # Initialize the migration manager
        self.migration_manager = MigrationManager(db_path, migrations_path)

        # Create tables and apply migrations
        self._create_tables()
        self._apply_migrations()
        # Ensure application-level schema_version bookkeeping table is up-to-date
        self._ensure_app_schema_version()

    def _ensure_dir_exists(self):
        """Ensure the directory for the database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self):
        """Connect to the SQLite database with sane concurrency defaults."""
        # Increase busy timeout and allow cross-thread usage for test harness concurrency
        self.conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        # Enable WAL mode to reduce writer blocking readers
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error:
            pass
        # Set reasonable sync level for performance tests while maintaining durability
        try:
            self.conn.execute("PRAGMA synchronous=NORMAL")
        except sqlite3.Error:
            pass
        # Increase busy timeout at the SQLite engine level
        try:
            self.conn.execute("PRAGMA busy_timeout=30000")
        except sqlite3.Error:
            pass
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Use Row factory to get column names
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        """
        Create the yoyo_migration table if it doesn't exist.

        Note: The actual database tables are created by the migrations.
        """
        # The yoyo_migration table is created automatically by yoyo-migrations
        # when migrations are applied. We don't need to create it manually.

        # Commit any changes
        self.conn.commit()

    def _apply_migrations(self):
        """
        Apply any pending database migrations.

        This method uses the MigrationManager to apply any pending migrations.
        """
        try:
            # Apply all pending migrations
            count = self.migration_manager.apply_migrations()

            if count > 0:
                logger.info(f"Applied {count} database migrations")
            else:
                logger.debug("No database migrations to apply")

        except sqlite3.OperationalError as e:
            # Check if the error is about a table already existing
            error_str = str(e)
            if "table" in error_str and "already exists" in error_str:
                table_name = error_str.split("table ")[1].split(" already")[0]
                logger.warning(f"Table {table_name} already exists, skipping migration")
            else:
                logger.error(f"Error applying database migrations: {e}")
                raise
        except Exception as e:
            logger.error(f"Error applying database migrations: {e}")
            raise

    # --- Minimal schema version bookkeeping expected by tests -----------------
    def _ensure_app_schema_version(self) -> None:
        """Ensure a simple schema_version table exists and reflects SCHEMA_VERSION.

        Tests expect a table named `schema_version(id INTEGER PRIMARY KEY, version INTEGER NOT NULL, updated_at REAL NOT NULL)`
        and that we insert a new row when upgrading.
        """
        try:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS schema_version (\n"
                "  id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                "  version INTEGER NOT NULL,\n"
                "  updated_at REAL NOT NULL\n"
                ")"
            )
            self.conn.commit()

            # Get current version if any
            self.cursor.execute(
                "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1"
            )
            row = self.cursor.fetchone()
            current_version = row[0] if row else None

            if current_version is None:
                # Initialize to current schema version
                self._set_schema_version(self.SCHEMA_VERSION)
            elif isinstance(current_version, int) and current_version < self.SCHEMA_VERSION:
                # Perform migration from old to new
                self._migrate_schema(current_version)
                self._set_schema_version(self.SCHEMA_VERSION)
        except Exception as e:
            logger.warning(f"Schema version bookkeeping failed or is unavailable: {e}")

    def _set_schema_version(self, version: int) -> None:
        """Insert a new schema_version row."""
        self.cursor.execute(
            "INSERT INTO schema_version (version, updated_at) VALUES (?, ?)",
            (int(version), time.time()),
        )
        self.conn.commit()

    def _migrate_schema(self, old_version: int) -> None:
        """Hook for tests; delegate to migration manager to apply latest migrations."""
        try:
            # Apply migrations up to head
            self.apply_migrations()
        except Exception as e:
            logger.warning(f"_migrate_schema encountered an error: {e}")

    def get_schema_version(self) -> Optional[str]:
        """
        Get the current schema version.

        Returns:
            The ID of the most recently applied migration, or None if no migrations
            have been applied.
        """
        return self.migration_manager.get_current_version()

    def get_migration_status(self) -> List[Tuple[str, bool, str]]:
        """
        Get the status of all migrations.

        Returns:
            List of tuples containing (migration_id, is_applied, description).
        """
        return self.migration_manager.get_migration_status()

    def apply_migrations(self, target: Optional[str] = None) -> int:
        """
        Apply pending migrations.

        Args:
            target: Target migration ID to migrate to. If None, apply all
                pending migrations. Defaults to None.

        Returns:
            int: Number of migrations applied.
        """
        return self.migration_manager.apply_migrations(target)

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
        return self.migration_manager.rollback_migrations(target, steps)

    def create_migration(self, name: str) -> str:
        """
        Create a new migration file.

        Args:
            name: Name of the migration.

        Returns:
            Path to the created migration file.
        """
        return self.migration_manager.create_migration(name)

    def save_state(self, state_data):
        """
        Save the state data to the database.

        Args:
            state_data: Dictionary containing the state data.

        Returns:
            int: The ID of the saved state.
        """
        # Get the current timestamp
        timestamp = time.time()

        # Extract the main state data
        version = state_data.get("version", 1)
        last_emotion = (
            json.dumps(state_data.get("emotion")) if state_data.get("emotion") else None
        )
        last_intensity = state_data.get("last_intensity", 0.0)
        last_dominance = state_data.get("last_dominance", 0.0)
        last_zone = state_data.get("last_zone")
        evolution_stats = json.dumps(state_data.get("evolution", {}))

        # Extract configuration parameters
        max_memories = state_data.get("max_memories", 100)
        max_discoveries = state_data.get("max_discoveries", 50)
        max_explored_zones = state_data.get("max_explored_zones", 20)
        max_modifiers = state_data.get("max_modifiers", 50)
        max_checkpoints = state_data.get("max_checkpoints", 10)

        # Insert or update the state
        self.cursor.execute(
            """
            INSERT INTO state (version, timestamp, last_emotion, last_intensity, last_dominance,
                               last_zone, evolution_stats, max_memories, max_discoveries,
                               max_explored_zones, max_modifiers, max_checkpoints)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version,
                timestamp,
                last_emotion,
                last_intensity,
                last_dominance,
                last_zone,
                evolution_stats,
                max_memories,
                max_discoveries,
                max_explored_zones,
                max_modifiers,
                max_checkpoints,
            ),
        )

        # Get the ID of the inserted state
        state_id = self.cursor.lastrowid

        # Save memories
        memories = state_data.get("memories", [])
        for memory in memories:
            self._save_memory(state_id, memory)

        # Save discoveries
        discoveries = state_data.get("discoveries", [])
        for discovery in discoveries:
            self._save_discovery(state_id, discovery)

        # Save explored zones
        explored_zones = state_data.get("explored_zones", [])
        for zone in explored_zones:
            self._save_explored_zone(state_id, zone)

        # Save modifiers
        modifiers = state_data.get("modifiers", {})
        for zone, zone_modifiers in modifiers.items():
            for modifier in zone_modifiers:
                self._save_modifier(state_id, zone, modifier)

        # Save checkpoints
        checkpoints = state_data.get("checkpoints", [])
        for checkpoint in checkpoints:
            self._save_checkpoint(state_id, checkpoint)

        # Commit the changes
        self.conn.commit()

        return state_id

    def _save_memory(self, state_id, memory):
        """Save a memory to the database."""
        if isinstance(memory, dict):
            description = memory.get("description", "")
            emotional_quality = memory.get("emotional_quality")
            clarity = memory.get("clarity", 0.0)
            # Store any additional data as JSON
            data = json.dumps(
                {
                    k: v
                    for k, v in memory.items()
                    if k not in ["description", "emotional_quality", "clarity"]
                }
            )

            self.cursor.execute(
                """
                INSERT INTO memories (state_id, description, emotional_quality, clarity, timestamp,
                                      data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (state_id, description, emotional_quality, clarity, time.time(), data),
            )

    def _save_discovery(self, state_id, discovery):
        """Save a discovery to the database."""
        if isinstance(discovery, dict):
            name = discovery.get("name", "")
            category = discovery.get("category")
            # Store any additional data as JSON
            data = json.dumps(
                {k: v for k, v in discovery.items() if k not in ["name", "category"]}
            )

            self.cursor.execute(
                """
                INSERT INTO discoveries (state_id, name, category, timestamp, data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (state_id, name, category, time.time(), data),
            )

    def _save_explored_zone(self, state_id, zone):
        """Save an explored zone to the database."""
        self.cursor.execute(
            """
            INSERT INTO explored_zones (state_id, name, timestamp)
            VALUES (?, ?, ?)
            """,
            (state_id, zone, time.time()),
        )

    def _save_modifier(self, state_id, zone, modifier):
        """Save a modifier to the database."""
        modifier_type = None
        effect = None
        data = None

        if isinstance(modifier, dict):
            modifier_type = modifier.get("type")
            effect = modifier.get("effect")
            # Store any additional data as JSON
            data = json.dumps(
                {k: v for k, v in modifier.items() if k not in ["type", "effect"]}
            )
        elif isinstance(modifier, str):
            modifier_type = modifier

        self.cursor.execute(
            """
            INSERT INTO modifiers (state_id, zone, type, effect, timestamp, data)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (state_id, zone, modifier_type, effect, time.time(), data),
        )

    def _save_checkpoint(self, state_id, checkpoint):
        """Save a checkpoint to the database."""
        path = checkpoint
        timestamp = time.time()
        if isinstance(checkpoint, dict):
            path = checkpoint.get("path")
            created_at = checkpoint.get("created_at")
            if isinstance(created_at, str):
                parsed = _timestamp_from_iso(created_at)
                if parsed is not None:
                    timestamp = parsed
        if not path:
            return
        self.cursor.execute(
            """
            INSERT INTO checkpoints (state_id, path, timestamp)
            VALUES (?, ?, ?)
            """,
            (state_id, str(path), timestamp),
        )

    def load_latest_state(self, lazy_load=False):
        """
        Load the latest state from the database.

        Args:
            lazy_load: If True, only load the main state data and defer loading
                      related collections until they are accessed. This can
                      significantly reduce memory usage for large states.
                      Defaults to False.

        Returns:
            dict: The latest state data, or None if no state exists.
        """
        # Get the latest state
        self.cursor.execute(
            """
            SELECT *
            FROM state
            ORDER BY timestamp DESC
                LIMIT 1
            """
        )

        state_row = self.cursor.fetchone()
        if not state_row:
            return None

        # Convert row to dict
        state_data = dict(state_row)
        state_id = state_data["id"]

        # Parse JSON fields
        if state_data["last_emotion"]:
            state_data["emotion"] = json.loads(state_data["last_emotion"])
        else:
            state_data["emotion"] = None

        state_data["evolution"] = json.loads(state_data["evolution_stats"])

        if lazy_load:
            # Store state_id for lazy loading
            state_data["_state_id"] = state_id
            # Add lazy loading properties
            state_data["_lazy_loaded"] = {
                "memories": False,
                "discoveries": False,
                "explored_zones": False,
                "modifiers": False,
                "checkpoints": False,
            }
            # Initialize empty collections
            state_data["memories"] = []
            state_data["discoveries"] = []
            state_data["explored_zones"] = []
            state_data["modifiers"] = {}
            state_data["checkpoints"] = []
        else:
            # Load all related collections
            state_data["memories"] = self._load_memories(state_id)
            state_data["discoveries"] = self._load_discoveries(state_id)
            state_data["explored_zones"] = self._load_explored_zones(state_id)
            state_data["modifiers"] = self._load_modifiers(state_id)
            state_data["checkpoints"] = self._load_checkpoints(state_id)

        return state_data

    def lazy_load_collection(self, state_data, collection_name):
        """
        Lazy load a collection for a state.

        Args:
            state_data: The state data dictionary.
            collection_name: The name of the collection to load.

        Returns:
            The loaded collection.
        """
        if not state_data.get("_lazy_loaded"):
            # Not a lazy-loaded state, return the existing collection
            return state_data.get(collection_name, [])

        if state_data["_lazy_loaded"].get(collection_name, True):
            # Already loaded, return the existing collection
            return state_data.get(collection_name, [])

        # Load the collection
        state_id = state_data.get("_state_id")
        if not state_id:
            return state_data.get(collection_name, [])

        if collection_name == "memories":
            state_data["memories"] = self._load_memories(state_id)
        elif collection_name == "discoveries":
            state_data["discoveries"] = self._load_discoveries(state_id)
        elif collection_name == "explored_zones":
            state_data["explored_zones"] = self._load_explored_zones(state_id)
        elif collection_name == "modifiers":
            state_data["modifiers"] = self._load_modifiers(state_id)
        elif collection_name == "checkpoints":
            state_data["checkpoints"] = self._load_checkpoints(state_id)

        # Mark as loaded
        state_data["_lazy_loaded"][collection_name] = True

        return state_data.get(collection_name, [])

    def _load_memories(self, state_id):
        """Load memories for a state."""
        self.cursor.execute(
            """
            SELECT *
            FROM memories
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        memories = []
        for row in self.cursor.fetchall():
            memory = {
                "description": row["description"],
                "emotional_quality": row["emotional_quality"],
                "clarity": row["clarity"],
            }

            # Add any additional data
            if row["data"]:
                memory.update(json.loads(row["data"]))

            memories.append(memory)

        return memories

    def _load_discoveries(self, state_id):
        """Load discoveries for a state."""
        self.cursor.execute(
            """
            SELECT *
            FROM discoveries
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        discoveries = []
        for row in self.cursor.fetchall():
            discovery = {"name": row["name"], "category": row["category"]}

            # Add any additional data
            if row["data"]:
                discovery.update(json.loads(row["data"]))

            discoveries.append(discovery)

        return discoveries

    def _load_explored_zones(self, state_id):
        """Load explored zones for a state."""
        self.cursor.execute(
            """
            SELECT name
            FROM explored_zones
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        return [row["name"] for row in self.cursor.fetchall()]

    def _load_modifiers(self, state_id):
        """Load modifiers for a state."""
        self.cursor.execute(
            """
            SELECT *
            FROM modifiers
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        modifiers = {}
        for row in self.cursor.fetchall():
            zone = row["zone"]

            if zone not in modifiers:
                modifiers[zone] = []

            # Create the modifier
            if row["data"]:
                # If we have additional data, create a dict with all data
                modifier_data = json.loads(row["data"])
                if row["type"]:
                    modifier_data["type"] = row["type"]
                if row["effect"]:
                    modifier_data["effect"] = row["effect"]
                modifiers[zone].append(modifier_data)
            elif row["type"] and row["effect"]:
                # If we have type and effect but no additional data
                modifiers[zone].append({"type": row["type"], "effect": row["effect"]})
            elif row["type"]:
                # If we only have type
                modifiers[zone].append(row["type"])

        return modifiers

    def _load_checkpoints(self, state_id):
        """Load checkpoints for a state."""
        self.cursor.execute(
            """
            SELECT path, timestamp
            FROM checkpoints
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        results = []
        for row in self.cursor.fetchall():
            path = row["path"]
            ts = row["timestamp"]
            created_at = _iso_from_timestamp(ts)
            results.append({
                    "path": path,
                    "created_at": created_at,
                    "kind": "auto",
                    "label": Path(path).name or path,
                    "target_path": path,
                })
        return results

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted."""
        self.close()

    def backup_state(self, backup_path=None):
        """
        Create a backup of the current database.

        Args:
            backup_path: Path where the backup will be saved. If None, a default path
                        will be generated based on the current timestamp.

        Returns:
            str: The path to the backup file.
        """
        if backup_path is None:
            # Generate a default backup path with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"eternia_backup_{timestamp}.db")

        # Ensure the backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Before backing up, checkpoint WAL so all data is in the main db file
        try:
            self.conn.execute("PRAGMA wal_checkpoint(FULL)")
        except sqlite3.Error:
            pass

        # Create a backup using SQLite's backup API into a temporary file, then replace
        tmp_backup_path = backup_path + ".tmp"
        backup_conn = sqlite3.connect(tmp_backup_path)

        try:
            # Perform the backup
            with backup_conn:
                self.conn.backup(backup_conn)
            backup_conn.close()

            # Atomic replace to final path
            try:
                os.replace(tmp_backup_path, backup_path)
            except Exception:
                # Fallback to copy if replace fails (e.g., cross-filesystem)
                import shutil
                shutil.copy2(tmp_backup_path, backup_path)
                try:
                    os.remove(tmp_backup_path)
                except Exception:
                    pass

            print(f"✅ Database backup created at {backup_path}")
            return backup_path
        except sqlite3.Error as e:
            print(f"❌ Database backup failed: {e}")
            try:
                backup_conn.close()
            except Exception:
                pass
            try:
                if os.path.exists(tmp_backup_path):
                    os.remove(tmp_backup_path)
            except Exception:
                pass
            return None
        finally:
            try:
                backup_conn.close()
            except Exception:
                pass

    def restore_from_backup(self, backup_path):
        """
        Restore the database from a backup.

        Args:
            backup_path: Path to the backup file to restore from.

        Returns:
            bool: True if the restore was successful, False otherwise.
        """
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False

        # Step 1: close any open connections and snapshot current DB (for rollback)
        current_backup = self._pre_restore_close_and_backup()

        # Step 2: remove any stray WAL/SHM files before we replace
        self._remove_wal_shm()

        tmp_restore_path = f"{self.db_path}.restore.tmp"
        try:
            # Step 3: stage the incoming backup to a temp file
            self._copy_to_tmp(backup_path, tmp_restore_path)

            # Step 4: atomically replace the live DB
            self._atomic_replace(tmp_restore_path)

            # Step 5: cleanup any WAL/SHM from the previous incarnation
            self._remove_wal_shm()

            # Step 6: reconnect and validate integrity
            self._reconnect_and_check()

            print(f"✅ Database restored from {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Database restore failed: {e}")
            # Try to rollback to the previous DB if we created a snapshot
            self._rollback_to_previous(current_backup)
            # Best-effort reconnect after rollback attempt
            try:
                self._connect()
            except Exception:
                pass
            # Ensure temp file is removed
            try:
                if os.path.exists(tmp_restore_path):
                    os.remove(tmp_restore_path)
            except Exception:
                pass
            return False

    # --- Helper methods for restore_from_backup (reduce complexity) ---
    def _pre_restore_close_and_backup(self) -> Optional[str]:
        """Close connection and create a timestamped backup of current DB (if exists).
        Returns the path to the snapshot or None.
        """
        # Close the current connection to release file locks
        try:
            self.close()
        except Exception:
            pass

        # Create a backup of the current database before restoring
        if not os.path.exists(self.db_path):
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = f"{self.db_path}.{timestamp}.bak"
        try:
            import shutil
            shutil.copy2(self.db_path, snapshot_path)
            print(f"✅ Created backup of current database at {snapshot_path}")
        except Exception as e:
            print(f"⚠️ Failed to create backup of current database: {e}")
        return snapshot_path

    def _remove_wal_shm(self) -> None:
        """Remove SQLite -wal/-shm sidecar files for current DB path, ignore errors."""
        try:
            for p in (f"{self.db_path}-wal", f"{self.db_path}-shm"):
                if os.path.exists(p):
                    os.remove(p)
        except Exception:
            pass

    def _copy_to_tmp(self, backup_path: str, tmp_restore_path: str) -> None:
        """Copy backup file to a temp location and fsync it to disk."""
        import shutil
        shutil.copy2(backup_path, tmp_restore_path)
        try:
            with open(tmp_restore_path, 'rb+') as f:
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            # Non-fatal: continue even if fsync fails
            pass

    def _atomic_replace(self, tmp_restore_path: str) -> None:
        """Atomically replace the live DB with the staged temp file."""
        os.replace(tmp_restore_path, self.db_path)

    def _reconnect_and_check(self) -> None:
        """Reconnect to the DB and run integrity check; raise on failure."""
        self._connect()
        row = self.conn.execute("PRAGMA integrity_check").fetchone()
        if not row or row[0] != 'ok':
            raise sqlite3.DatabaseError(
                f"Integrity check failed: {row[0] if row else 'unknown'}"
            )

    def _rollback_to_previous(self, snapshot_path: Optional[str]) -> None:
        """Attempt to restore the DB from a snapshot; log outcome."""
        if not snapshot_path or not os.path.exists(snapshot_path):
            return
        try:
            import shutil
            shutil.copy2(snapshot_path, self.db_path)
            print(f"✅ Reverted to previous database state from {snapshot_path}")
        except Exception as e2:
            print(f"❌ Failed to revert to previous database state: {e2}")

    def list_backups(self):
        """
        List all available database backups.

        Returns:
            list: A list of backup file paths.
        """
        backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        if not os.path.exists(backup_dir):
            return []

        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith("eternia_backup_") and file.endswith(".db"):
                backups.append(os.path.join(backup_dir, file))

        # Sort by modification time (newest first)
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backups

    def export_to_json(self, output_path=None):
        """
        Export the database contents to a JSON file.

        This is useful for data migration between different storage formats
        or for creating human-readable backups.

        Args:
            output_path: Path where the JSON file will be saved. If None, a default path
                        will be generated based on the current timestamp.

        Returns:
            str: The path to the JSON file, or None if the export failed.
        """
        if output_path is None:
            # Generate a default output path with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(os.path.dirname(self.db_path), "exports")
            os.makedirs(export_dir, exist_ok=True)
            output_path = os.path.join(export_dir, f"eternia_export_{timestamp}.json")

        # Ensure the export directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Load the latest state
            state_data = self.load_latest_state()

            if state_data is None:
                print("❌ No state data to export")
                return None

            # Add metadata
            export_data = {
                "export_timestamp": time.time(),
                "schema_version": self.SCHEMA_VERSION,
                "state": state_data,
            }

            # Write to JSON file
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)

            print(f"✅ Database exported to {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Database export failed: {e}")
            return None

    def import_from_json(self, input_path):
        """
        Import data from a JSON file into the database.

        This is useful for data migration between different storage formats.

        Args:
            input_path: Path to the JSON file to import.

        Returns:
            bool: True if the import was successful, False otherwise.
        """
        if not os.path.exists(input_path):
            print(f"❌ Import file not found: {input_path}")
            return False

        try:
            # Read the JSON file
            with open(input_path, "r") as f:
                import_data = json.load(f)

            # Check schema version
            import_schema_version = import_data.get("schema_version")
            if import_schema_version and import_schema_version > self.SCHEMA_VERSION:
                print(
                    f"⚠️ Warning: Import data schema version ({import_schema_version}) is newer than the current schema version ({self.SCHEMA_VERSION})"
                )

            # Get the state data
            state_data = import_data.get("state")
            if not state_data:
                print("❌ No state data found in import file")
                return False

            # Save the state data to the database
            state_id = self.save_state(state_data)

            print(f"✅ Data imported from {input_path} (State ID: {state_id})")
            return True
        except Exception as e:
            print(f"❌ Data import failed: {e}")
            return False
