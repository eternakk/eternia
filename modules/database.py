"""
Database module for Eternia.

This module provides a database schema and operations for persistent storage of the Eternia state.
It uses SQLite as the database engine for simplicity and portability.
"""

import datetime
import json
import os
import sqlite3
import time


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

    # Database schema version - increment this when making schema changes
    SCHEMA_VERSION = 1

    def __init__(self, db_path="data/eternia.db"):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file. Defaults to "data/eternia.db".
        """
        self.db_path = db_path
        self._ensure_dir_exists()
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _ensure_dir_exists(self):
        """Ensure the directory for the database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Use Row factory to get column names
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        """Create the database tables if they don't exist."""
        # Schema version table - stores the current schema version
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version
            (
                id
                INTEGER
                PRIMARY
                KEY,
                version
                INTEGER
                NOT
                NULL,
                updated_at
                REAL
                NOT
                NULL
            )
            """
        )

        # State table - stores the main state information
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS state
            (
                id
                INTEGER
                PRIMARY
                KEY,
                version
                INTEGER
                NOT
                NULL,
                timestamp
                REAL
                NOT
                NULL,
                last_emotion
                TEXT,
                last_intensity
                REAL,
                last_dominance
                REAL,
                last_zone
                TEXT,
                evolution_stats
                TEXT
                NOT
                NULL,
                max_memories
                INTEGER
                NOT
                NULL,
                max_discoveries
                INTEGER
                NOT
                NULL,
                max_explored_zones
                INTEGER
                NOT
                NULL,
                max_modifiers
                INTEGER
                NOT
                NULL,
                max_checkpoints
                INTEGER
                NOT
                NULL
            )
            """
        )

        # Memories table - stores memories
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories
            (
                id
                INTEGER
                PRIMARY
                KEY,
                state_id
                INTEGER
                NOT
                NULL,
                description
                TEXT
                NOT
                NULL,
                emotional_quality
                TEXT,
                clarity
                REAL,
                timestamp
                REAL
                NOT
                NULL,
                data
                TEXT,
                FOREIGN
                KEY
            (
                state_id
            ) REFERENCES state
            (
                id
            )
                )
            """
        )

        # Discoveries table - stores discoveries
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS discoveries
            (
                id
                INTEGER
                PRIMARY
                KEY,
                state_id
                INTEGER
                NOT
                NULL,
                name
                TEXT
                NOT
                NULL,
                category
                TEXT,
                timestamp
                REAL
                NOT
                NULL,
                data
                TEXT,
                FOREIGN
                KEY
            (
                state_id
            ) REFERENCES state
            (
                id
            )
                )
            """
        )

        # Explored zones table - stores explored zones
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS explored_zones
            (
                id
                INTEGER
                PRIMARY
                KEY,
                state_id
                INTEGER
                NOT
                NULL,
                name
                TEXT
                NOT
                NULL,
                timestamp
                REAL
                NOT
                NULL,
                FOREIGN
                KEY
            (
                state_id
            ) REFERENCES state
            (
                id
            )
                )
            """
        )

        # Modifiers table - stores modifiers
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS modifiers
            (
                id
                INTEGER
                PRIMARY
                KEY,
                state_id
                INTEGER
                NOT
                NULL,
                zone
                TEXT
                NOT
                NULL,
                type
                TEXT,
                effect
                TEXT,
                timestamp
                REAL
                NOT
                NULL,
                data
                TEXT,
                FOREIGN
                KEY
            (
                state_id
            ) REFERENCES state
            (
                id
            )
                )
            """
        )

        # Checkpoints table - stores checkpoint paths
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS checkpoints
            (
                id
                INTEGER
                PRIMARY
                KEY,
                state_id
                INTEGER
                NOT
                NULL,
                path
                TEXT
                NOT
                NULL,
                timestamp
                REAL
                NOT
                NULL,
                FOREIGN
                KEY
            (
                state_id
            ) REFERENCES state
            (
                id
            )
                )
            """
        )

        # Check and update schema version
        self._check_schema_version()

        # Commit the changes
        self.conn.commit()

    def _check_schema_version(self):
        """
        Check the current schema version and perform migrations if necessary.

        This method:
        1. Checks the current schema version in the database
        2. If no version exists, initializes it to the current version
        3. If the version is older than the current version, performs migrations
        """
        # Check if schema_version table exists and has a version
        self.cursor.execute(
            "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1"
        )
        result = self.cursor.fetchone()

        if result is None:
            # No version exists, initialize to current version
            self.cursor.execute(
                "INSERT INTO schema_version (version, updated_at) VALUES (?, ?)",
                (self.SCHEMA_VERSION, time.time()),
            )
            print(f"🔄 Initialized database schema to version {self.SCHEMA_VERSION}")
            return

        db_version = result[0]

        if db_version < self.SCHEMA_VERSION:
            # Database schema is older, perform migrations
            print(
                f"🔄 Migrating database schema from version {db_version} to {self.SCHEMA_VERSION}"
            )
            self._migrate_schema(db_version)

            # Update schema version
            self.cursor.execute(
                "INSERT INTO schema_version (version, updated_at) VALUES (?, ?)",
                (self.SCHEMA_VERSION, time.time()),
            )
            print(f"✅ Database schema migrated to version {self.SCHEMA_VERSION}")
        elif db_version > self.SCHEMA_VERSION:
            # Database schema is newer than the code expects
            print(
                f"⚠️ Warning: Database schema version ({db_version}) is newer than the code expects ({self.SCHEMA_VERSION})"
            )

    def _migrate_schema(self, from_version):
        """
        Perform database schema migrations.

        Args:
            from_version: The current version of the schema to migrate from.
        """
        # Migration steps for each version
        if from_version < 1:
            # Migration to version 1 (initial schema)
            pass  # No migration needed for initial schema

        # Add future migrations here
        # if from_version < 2:
        #     # Migration to version 2
        #     self._migrate_to_v2()

        # Commit the changes
        self.conn.commit()

    def _migrate_to_v2(self):
        """
        Example migration function for future schema changes.

        This would implement the changes needed to migrate from version 1 to version 2.
        For example, adding new tables, columns, or modifying existing ones.
        """
        # Example: Add a new column to the state table
        # try:
        #     self.cursor.execute("ALTER TABLE state ADD COLUMN new_column TEXT")
        #     print("✅ Added new_column to state table")
        # except sqlite3.Error as e:
        #     print(f"❌ Failed to add new_column to state table: {e}")
        pass

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
        self.cursor.execute(
            """
            INSERT INTO checkpoints (state_id, path, timestamp)
            VALUES (?, ?, ?)
            """,
            (state_id, checkpoint, time.time()),
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
            SELECT path
            FROM checkpoints
            WHERE state_id = ?
            ORDER BY timestamp
            """,
            (state_id,),
        )

        return [row["path"] for row in self.cursor.fetchall()]

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

        # Create a backup using SQLite's backup API
        backup_conn = sqlite3.connect(backup_path)

        try:
            # Perform the backup
            with backup_conn:
                self.conn.backup(backup_conn)

            print(f"✅ Database backup created at {backup_path}")
            return backup_path
        except sqlite3.Error as e:
            print(f"❌ Database backup failed: {e}")
            return None
        finally:
            backup_conn.close()

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

        # Close the current connection
        self.close()

        # Create a backup of the current database before restoring
        current_backup = None
        if os.path.exists(self.db_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"{self.db_path}.{timestamp}.bak"
            try:
                import shutil

                shutil.copy2(self.db_path, current_backup)
                print(f"✅ Created backup of current database at {current_backup}")
            except Exception as e:
                print(f"⚠️ Failed to create backup of current database: {e}")

        try:
            # Copy the backup file to the database path
            import shutil

            shutil.copy2(backup_path, self.db_path)

            # Reconnect to the database
            self._connect()

            print(f"✅ Database restored from {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Database restore failed: {e}")

            # Try to restore from the backup of the current database
            if current_backup and os.path.exists(current_backup):
                try:
                    shutil.copy2(current_backup, self.db_path)
                    print(
                        f"✅ Reverted to previous database state from {current_backup}"
                    )
                except Exception as e2:
                    print(f"❌ Failed to revert to previous database state: {e2}")

            # Reconnect to the database (or try to)
            try:
                self._connect()
            except Exception:
                pass

            return False

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
