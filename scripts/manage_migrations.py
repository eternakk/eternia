#!/usr/bin/env python
"""
Migration management script for Eternia database.

This script provides a command-line interface for managing database migrations.
It allows creating, applying, and rolling back migrations.
"""

import argparse
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.database import EternaDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("migration_manager")


def create_migration(args):
    """Create a new migration file."""
    db = EternaDatabase(args.db_path, args.migrations_path)
    migration_path = db.create_migration(args.name)
    print(f"Created migration file: {migration_path}")
    print("Edit this file to define your migration steps.")


def apply_migrations(args):
    """Apply pending migrations."""
    db = EternaDatabase(args.db_path, args.migrations_path)
    
    if args.target:
        print(f"Applying migrations up to target: {args.target}")
        count = db.apply_migrations(args.target)
    else:
        print("Applying all pending migrations")
        count = db.apply_migrations()
    
    if count > 0:
        print(f"Applied {count} migrations")
    else:
        print("No migrations to apply")


def rollback_migrations(args):
    """Roll back applied migrations."""
    db = EternaDatabase(args.db_path, args.migrations_path)
    
    if args.target:
        print(f"Rolling back migrations to target: {args.target}")
        count = db.rollback_migrations(args.target)
    else:
        print(f"Rolling back {args.steps} migrations")
        count = db.rollback_migrations(steps=args.steps)
    
    if count > 0:
        print(f"Rolled back {count} migrations")
    else:
        print("No migrations to roll back")


def show_status(args):
    """Show the status of all migrations."""
    db = EternaDatabase(args.db_path, args.migrations_path)
    
    # Get the current version
    current_version = db.get_schema_version()
    if current_version:
        print(f"Current schema version: {current_version}")
    else:
        print("No migrations have been applied")
    
    # Get the status of all migrations
    status = db.get_migration_status()
    
    if not status:
        print("No migrations found")
        return
    
    print("\nMigration status:")
    print("-" * 80)
    print(f"{'ID':<20} {'Applied':<10} {'Description'}")
    print("-" * 80)
    
    for migration_id, is_applied, description in status:
        applied_str = "✓" if is_applied else "✗"
        print(f"{migration_id:<20} {applied_str:<10} {os.path.basename(description)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Manage database migrations for Eternia"
    )
    
    # Common arguments
    parser.add_argument(
        "--db-path",
        default="data/eternia.db",
        help="Path to the SQLite database file",
    )
    parser.add_argument(
        "--migrations-path",
        default="migrations",
        help="Path to the directory containing migration scripts",
    )
    
    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create migration command
    create_parser = subparsers.add_parser(
        "create", help="Create a new migration file"
    )
    create_parser.add_argument("name", help="Name of the migration")
    create_parser.set_defaults(func=create_migration)
    
    # Apply migrations command
    apply_parser = subparsers.add_parser(
        "apply", help="Apply pending migrations"
    )
    apply_parser.add_argument(
        "--target",
        help="Target migration ID to migrate to",
    )
    apply_parser.set_defaults(func=apply_migrations)
    
    # Rollback migrations command
    rollback_parser = subparsers.add_parser(
        "rollback", help="Roll back applied migrations"
    )
    rollback_parser.add_argument(
        "--target",
        help="Target migration ID to rollback to",
    )
    rollback_parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of migrations to roll back",
    )
    rollback_parser.set_defaults(func=rollback_migrations)
    
    # Show status command
    status_parser = subparsers.add_parser(
        "status", help="Show the status of all migrations"
    )
    status_parser.set_defaults(func=show_status)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()