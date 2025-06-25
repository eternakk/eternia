# Eternia Migration Manager

This document provides comprehensive information about the Eternia Migration Manager, a component that handles database schema migrations using the [yoyo-migrations](https://ollycope.com/software/yoyo/latest/) package.

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Implementation](#implementation)
4. [Usage](#usage)
5. [Migration Files](#migration-files)
6. [Command-Line Interface](#command-line-interface)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The Migration Manager is responsible for managing database schema migrations in the Eternia project. It provides a clean interface to the yoyo-migrations package and handles all the details of applying, rolling back, and tracking migrations.

The Migration Manager is implemented in the `modules/migration_manager.py` file through the `MigrationManager` class.

## Key Features

- **Apply Migrations**: Apply pending migrations to update the database schema
- **Rollback Migrations**: Roll back applied migrations to revert schema changes
- **Migration Status**: Check the status of all migrations
- **Version Tracking**: Track the current database schema version
- **Migration Creation**: Create new migration files with templates

## Implementation

The Migration Manager is implemented as a Python class called `MigrationManager` in the `modules/migration_manager.py` file. It uses the yoyo-migrations package to handle the actual migration operations.

### Class Structure

```python
class MigrationManager:
    def __init__(self, db_path: str, migrations_path: str = "migrations"):
        # Initialize the migration manager
        
    def apply_migrations(self, target: Optional[str] = None) -> int:
        # Apply pending migrations
        
    def rollback_migrations(self, target: Optional[str] = None, steps: int = 1) -> int:
        # Roll back applied migrations
        
    def get_migration_status(self) -> List[Tuple[str, bool, str]]:
        # Get the status of all migrations
        
    def get_current_version(self) -> Optional[str]:
        # Get the ID of the most recently applied migration
        
    def create_migration(self, name: str) -> str:
        # Create a new migration file
```

## Usage

### Initializing the Migration Manager

```python
from modules.migration_manager import MigrationManager

# Initialize with default settings
manager = MigrationManager(db_path="data/eternia.db")

# Initialize with custom migrations path
manager = MigrationManager(
    db_path="data/eternia.db",
    migrations_path="custom/migrations"
)
```

### Applying Migrations

```python
# Apply all pending migrations
count = manager.apply_migrations()
print(f"Applied {count} migrations")

# Apply migrations up to a specific target
count = manager.apply_migrations(target="20250625_123456")
print(f"Applied {count} migrations")
```

### Rolling Back Migrations

```python
# Roll back the most recent migration
count = manager.rollback_migrations()
print(f"Rolled back {count} migrations")

# Roll back multiple migrations
count = manager.rollback_migrations(steps=3)
print(f"Rolled back {count} migrations")

# Roll back to a specific target
count = manager.rollback_migrations(target="20250625_123456")
print(f"Rolled back {count} migrations")
```

### Checking Migration Status

```python
# Get the status of all migrations
status = manager.get_migration_status()
for migration_id, is_applied, description in status:
    status_text = "Applied" if is_applied else "Pending"
    print(f"{migration_id}: {status_text} - {description}")

# Get the current schema version
version = manager.get_current_version()
print(f"Current schema version: {version}")
```

### Creating New Migrations

```python
# Create a new migration file
migration_path = manager.create_migration("add_user_table")
print(f"Created migration file: {migration_path}")
```

## Migration Files

Migration files are Python scripts that define a series of steps to apply and roll back changes to the database schema. Each migration file has a unique ID (based on the timestamp) and a descriptive name.

### Example Migration File

```python
"""
Add User Table.

This migration adds a new table for storing user information.
"""

from yoyo import step

__depends__ = {}  # Dependencies on other migrations

steps = [
    step(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """,
        """
        DROP TABLE users
        """
    )
]
```

## Command-Line Interface

The Eternia project provides a command-line script for managing migrations in `scripts/manage_migrations.py`:

```bash
# Show migration status
./scripts/manage_migrations.py status

# Create a new migration
./scripts/manage_migrations.py create add_user_table

# Apply all pending migrations
./scripts/manage_migrations.py apply

# Apply migrations up to a specific target
./scripts/manage_migrations.py apply --target 20250625_123456

# Roll back the most recent migration
./scripts/manage_migrations.py rollback

# Roll back multiple migrations
./scripts/manage_migrations.py rollback --steps 3

# Roll back to a specific target
./scripts/manage_migrations.py rollback --target 20250625_123456
```

## Best Practices

### Migration Design

- **Small, Focused Migrations**: Keep migrations small and focused on a single change
- **Idempotent Migrations**: Design migrations to be idempotent (can be applied multiple times without side effects)
- **Test Migrations**: Test migrations thoroughly before applying them to production
- **Descriptive Names**: Use descriptive names for migration files
- **Document Migrations**: Include detailed documentation in migration files

### Migration Management

- **Regular Backups**: Create regular backups of the database, especially before applying migrations
- **Version Control**: Keep migration files in version control
- **Coordinate Migrations**: Coordinate migrations with code changes
- **Review Migrations**: Have team members review migrations before applying them

## Troubleshooting

### Common Issues

#### Migration Conflicts

**Symptom**: Conflicts between migrations

**Causes**:
- Multiple developers creating migrations simultaneously
- Branching and merging in version control

**Solutions**:
- Coordinate migration creation among team members
- Use the `__depends__` attribute to specify dependencies
- Resolve conflicts manually by editing migration files

#### Failed Migrations

**Symptom**: Migrations fail to apply

**Causes**:
- Errors in SQL statements
- Database constraints
- Insufficient permissions

**Solutions**:
- Check SQL syntax
- Ensure database constraints are satisfied
- Verify database permissions
- Roll back to a known good state

#### Database Locked

**Symptom**: "database is locked" error

**Causes**:
- Multiple processes accessing the database simultaneously
- A previous operation did not release the lock

**Solutions**:
- Ensure only one process applies migrations at a time
- Use a timeout for database operations
- Check for unclosed connections

---

_Authored: June 25, 2025_
_Last Updated: June 25, 2025_