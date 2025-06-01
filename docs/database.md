# Eternia Database System

This document provides comprehensive information about the Eternia database system, including its purpose, schema structure, API usage, configuration options, examples, best practices, and troubleshooting.

## Table of Contents

1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Configuration Options](#configuration-options)
4. [Using the Database API](#using-the-database-api)
5. [Common Operations](#common-operations)
6. [Migration and Versioning](#migration-and-versioning)
7. [Backup and Restore](#backup-and-restore)
8. [Memory Optimization](#memory-optimization)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Testing](#testing)

## Overview

The Eternia database system provides persistent storage for the Eternia world state. It uses SQLite as the database engine for simplicity, portability, and reliability. The database system is implemented in the `modules/database.py` file through the `EternaDatabase` class.

Key features of the database system include:

- **Persistent Storage**: Safely store and retrieve the Eternia world state
- **Schema Versioning**: Track and manage database schema changes
- **Migration Support**: Upgrade database schema between versions
- **Backup and Restore**: Create and restore backups of the database
- **Memory Optimization**: Lazy loading for efficient memory usage
- **Data Import/Export**: Convert between database and JSON formats

The database system is integrated with the `EternaStateTracker` class, which can use either the database or JSON files for persistence.

## Database Schema

The database schema consists of the following tables:

### schema_version

Tracks the current schema version of the database.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| version | INTEGER | Schema version number |
| updated_at | REAL | Timestamp of the last update |

### state

Stores the main state information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| version | INTEGER | State version number |
| timestamp | REAL | Timestamp of the state |
| last_emotion | TEXT | JSON representation of the last emotion |
| last_intensity | REAL | Intensity of the last emotion |
| last_dominance | REAL | Dominance of the last emotion |
| last_zone | TEXT | Name of the last zone |
| evolution_stats | TEXT | JSON representation of evolution statistics |
| max_memories | INTEGER | Maximum number of memories to store |
| max_discoveries | INTEGER | Maximum number of discoveries to store |
| max_explored_zones | INTEGER | Maximum number of explored zones to store |
| max_modifiers | INTEGER | Maximum number of modifiers to store |
| max_checkpoints | INTEGER | Maximum number of checkpoints to store |

### memories

Stores memories integrated into the world.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| state_id | INTEGER | Foreign key to state table |
| description | TEXT | Description of the memory |
| emotional_quality | TEXT | Emotional quality of the memory |
| clarity | REAL | Clarity of the memory |
| timestamp | REAL | Timestamp of the memory |
| data | TEXT | Additional JSON data for the memory |

### discoveries

Stores discoveries made in the world.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| state_id | INTEGER | Foreign key to state table |
| name | TEXT | Name of the discovery |
| category | TEXT | Category of the discovery |
| timestamp | REAL | Timestamp of the discovery |
| data | TEXT | Additional JSON data for the discovery |

### explored_zones

Stores zones that have been explored.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| state_id | INTEGER | Foreign key to state table |
| name | TEXT | Name of the zone |
| timestamp | REAL | Timestamp of the exploration |

### modifiers

Stores modifiers applied to zones.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| state_id | INTEGER | Foreign key to state table |
| zone | TEXT | Name of the zone |
| type | TEXT | Type of the modifier |
| effect | TEXT | Effect of the modifier |
| timestamp | REAL | Timestamp of the modifier |
| data | TEXT | Additional JSON data for the modifier |

### checkpoints

Stores checkpoint paths.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| state_id | INTEGER | Foreign key to state table |
| path | TEXT | Path to the checkpoint |
| timestamp | REAL | Timestamp of the checkpoint |

## Configuration Options

The database system can be configured through the following parameters:

### EternaDatabase

| Parameter | Default | Description |
|-----------|---------|-------------|
| db_path | "data/eternia.db" | Path to the SQLite database file |

### EternaStateTracker

| Parameter | Default | Description |
|-----------|---------|-------------|
| save_path | "logs/state_snapshot.json" | Path where the state snapshot is saved (for JSON persistence) |
| max_memories | 100 | Maximum number of memories to store |
| max_discoveries | 50 | Maximum number of discoveries to store |
| max_explored_zones | 20 | Maximum number of explored zones to store |
| max_modifiers | 50 | Maximum number of modifiers to store |
| max_checkpoints | 10 | Maximum number of checkpoints to store |
| db_path | "data/eternia.db" | Path to the SQLite database file |
| use_database | True | Whether to use the database for persistence (if False, will use JSON) |
| use_lazy_loading | True | Whether to use lazy loading for collections |

## Using the Database API

### Initializing the Database

```python
from modules.database import EternaDatabase

# Initialize with default settings
db = EternaDatabase()

# Initialize with custom database path
db = EternaDatabase(db_path="custom/path/to/eternia.db")
```

### Using the Database with EternaStateTracker

```python
from modules.state_tracker import EternaStateTracker

# Initialize with database persistence (default)
tracker = EternaStateTracker(
    use_database=True,
    db_path="data/eternia.db",
    use_lazy_loading=True
)

# Initialize with JSON persistence
tracker = EternaStateTracker(
    use_database=False,
    save_path="logs/state_snapshot.json"
)
```

## Common Operations

### Saving and Loading State

The `EternaStateTracker` handles saving and loading state automatically. When `use_database` is set to `True`, it will use the database for persistence.

```python
# Save the current state
tracker.save()

# Save the full state (not incremental)
tracker.save(incremental=False)

# Load the state
tracker.load()
```

### Backup and Restore

```python
# Create a backup
backup_path = tracker.backup_state()
print(f"Backup created at: {backup_path}")

# Create a backup with a custom path
backup_path = tracker.backup_state(backup_path="custom/path/to/backup.db")

# List available backups
backups = tracker.list_backups()
for backup in backups:
    print(backup)

# Restore from a backup
success = tracker.restore_from_backup(backup_path)
if success:
    print("Restore successful")
else:
    print("Restore failed")
```

### Data Migration

```python
# Export to JSON
json_path = tracker.export_to_json()
print(f"Exported to: {json_path}")

# Import from JSON
success = tracker.import_from_json(json_path)
if success:
    print("Import successful")
else:
    print("Import failed")
```

## Migration and Versioning

The database system includes schema versioning and migration support. The current schema version is stored in the `schema_version` table, and migrations are performed automatically when the database is opened with a newer schema version.

To update the schema version:

1. Increment the `SCHEMA_VERSION` constant in the `EternaDatabase` class
2. Add a migration function for the new version
3. Update the `_migrate_schema` method to call the new migration function

Example of adding a new migration:

```python
# In EternaDatabase class
SCHEMA_VERSION = 2  # Increment from 1 to 2

def _migrate_to_v2(self):
    """Migrate from version 1 to version 2."""
    try:
        self.cursor.execute("ALTER TABLE state ADD COLUMN new_column TEXT")
        print("✅ Added new_column to state table")
    except sqlite3.Error as e:
        print(f"❌ Failed to add new_column to state table: {e}")

def _migrate_schema(self, from_version):
    """Perform database schema migrations."""
    # Migration steps for each version
    if from_version < 1:
        # Migration to version 1 (initial schema)
        pass  # No migration needed for initial schema

    # Add migration to version 2
    if from_version < 2:
        self._migrate_to_v2()

    # Commit the changes
    self.conn.commit()
```

## Backup and Restore

The database system provides built-in backup and restore functionality:

### Creating Backups

```python
# Using EternaDatabase directly
db = EternaDatabase()
backup_path = db.backup_state()

# Using EternaStateTracker
tracker = EternaStateTracker()
backup_path = tracker.backup_state()
```

Backups are stored in the `backups` directory next to the database file, with a timestamp in the filename.

### Restoring from Backups

```python
# Using EternaDatabase directly
db = EternaDatabase()
success = db.restore_from_backup(backup_path)

# Using EternaStateTracker
tracker = EternaStateTracker()
success = tracker.restore_from_backup(backup_path)
```

When restoring from a backup, the current database is backed up first to allow for recovery if the restore fails.

### Listing Backups

```python
# Using EternaDatabase directly
db = EternaDatabase()
backups = db.list_backups()

# Using EternaStateTracker
tracker = EternaStateTracker()
backups = tracker.list_backups()
```

## Memory Optimization

The database system includes memory optimization features to reduce memory usage for large states:

### Lazy Loading

When `use_lazy_loading` is set to `True`, collections (memories, discoveries, explored_zones, modifiers, checkpoints) are loaded only when accessed, reducing memory usage.

```python
# Initialize with lazy loading
tracker = EternaStateTracker(use_lazy_loading=True)

# Collections are loaded only when accessed
memories = tracker.get_memories_by_emotion("joy")  # Loads memories
discoveries = tracker.get_discoveries_by_category("artifact")  # Loads discoveries
```

### Bounded Collections

Collections are stored in bounded deques with configurable maximum sizes:

```python
# Initialize with custom collection sizes
tracker = EternaStateTracker(
    max_memories=200,
    max_discoveries=100,
    max_explored_zones=50,
    max_modifiers=100,
    max_checkpoints=20
)
```

### Incremental Updates

State snapshots support incremental updates to avoid saving unchanged data:

```python
# Save incrementally (default)
tracker.save()

# Save full state
tracker.save(incremental=False)
```

## Best Practices

### Database Configuration

- **Use Lazy Loading**: Enable lazy loading for large states to reduce memory usage
- **Configure Collection Sizes**: Adjust collection sizes based on your application's needs
- **Regular Backups**: Create regular backups of the database, especially before schema migrations

### Database Access

- **Close Connections**: Always close database connections when done
- **Use Context Managers**: Use context managers for database operations when possible
- **Handle Exceptions**: Catch and handle database exceptions to prevent crashes

### Schema Changes

- **Increment Version**: Always increment the schema version when making schema changes
- **Test Migrations**: Test migrations thoroughly before deploying
- **Backup Before Migration**: Always create a backup before migrating the schema

## Troubleshooting

### Common Issues

#### Database Locked

**Symptom**: "database is locked" error

**Causes**:
- Multiple processes accessing the database simultaneously
- A previous operation did not release the lock

**Solutions**:
- Ensure only one process accesses the database at a time
- Use a timeout for database operations
- Check for unclosed connections

#### Corrupt Database

**Symptom**: "database disk image is malformed" error

**Causes**:
- Improper shutdown
- Disk errors
- Power failure during write operations

**Solutions**:
- Restore from a backup
- Use the SQLite recovery tools
- Enable WAL mode for more robust transactions

#### Migration Errors

**Symptom**: Errors during schema migration

**Causes**:
- Incompatible schema changes
- Errors in migration scripts

**Solutions**:
- Restore from a backup
- Fix migration scripts and retry
- Consider a more gradual migration approach

### Diagnostic Tools

#### Database Integrity Check

```python
import sqlite3

conn = sqlite3.connect("data/eternia.db")
result = conn.execute("PRAGMA integrity_check").fetchone()[0]
print(f"Integrity check result: {result}")
conn.close()
```

#### Database Information

```python
import sqlite3

conn = sqlite3.connect("data/eternia.db")
print("Database size:", os.path.getsize("data/eternia.db"), "bytes")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [table[0] for table in tables])
conn.close()
```

## Testing

The Eternia database system includes a comprehensive test suite to ensure its functionality and reliability. The tests are located in the `tests/test_database.py` file and cover both the `EternaDatabase` class and its integration with the `EternaStateTracker` class.

### Test Coverage

The test suite covers the following areas:

1. **Database Initialization and Connection**
   - Verifies that the database file is created
   - Checks that the connection is established
   - Ensures that the schema version is set correctly

2. **Schema Creation and Versioning**
   - Verifies that all required tables are created
   - Tests schema versioning and migration

3. **State Saving and Loading**
   - Tests saving state data to the database
   - Verifies that loaded state matches the original

4. **Lazy Loading**
   - Tests lazy loading of collections
   - Verifies that collections are loaded only when accessed

5. **Backup and Restore**
   - Tests creating backups of the database
   - Verifies restoration from backups

6. **Data Migration and Export/Import**
   - Tests exporting data to JSON
   - Verifies importing data from JSON

7. **Integration with EternaStateTracker**
   - Tests database persistence through EternaStateTracker
   - Verifies switching between database and JSON persistence

### Running the Tests

To run the database tests, use the following command from the project root:

```bash
python -m pytest tests/test_database.py -v
```

### Test Fixtures

The test suite includes several fixtures to facilitate testing:

- `temp_db_path`: Creates a temporary database path for testing
- `temp_json_path`: Creates a temporary JSON file path for testing
- `temp_backup_dir`: Creates a temporary directory for backup testing
- `sample_state_data`: Provides sample state data for testing
- `db_instance`: Returns an initialized EternaDatabase instance
- `state_tracker_with_db`: Returns an initialized EternaStateTracker instance with database enabled
- `state_tracker_with_json`: Returns an initialized EternaStateTracker instance with JSON persistence

These fixtures handle setup and teardown automatically, including cleaning up temporary files and directories after tests.

---

_Authored: June 25, 2025_
_Last Updated: June 26, 2025_
