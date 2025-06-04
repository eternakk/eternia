#!/usr/bin/env python3
"""
Backup Recovery Script for Eternia

This script provides a command-line interface for restoring Eternia from a backup.
It can list available backups, download backups from cloud storage, and restore from a backup.

Usage:
    python restore_backup.py list                  # List available backups
    python restore_backup.py download <s3_url>     # Download a backup from S3
    python restore_backup.py restore <backup_path> # Restore from a backup
    python restore_backup.py help                  # Show help message
"""

import os
import sys
import logging
import argparse
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backup_recovery")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Eternia modules
from config.config_manager import config
from modules.state_tracker import EternaStateTracker
from modules.backup_manager import backup_manager


def list_backups() -> None:
    """List all available backups."""
    try:
        # Initialize the state tracker
        state_tracker = _initialize_state_tracker()
        
        # Set the state tracker in the backup manager
        backup_manager.set_state_tracker(state_tracker)
        
        # Get the list of backups
        backups = backup_manager.list_backups()
        
        if not backups:
            print("No backups found.")
            return
        
        # Print the backups
        print(f"Found {len(backups)} backups:")
        print("-" * 80)
        print(f"{'Index':<6} {'Type':<10} {'Size':<12} {'Created':<25} {'Filename'}")
        print("-" * 80)
        
        for i, backup in enumerate(backups):
            size_mb = backup["size"] / (1024 * 1024)
            print(f"{i:<6} {backup['type']:<10} {size_mb:.2f} MB {backup['created']:<25} {backup['filename']}")
    
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        sys.exit(1)


def download_backup(s3_url: str) -> None:
    """
    Download a backup from S3.
    
    Args:
        s3_url: The S3 URL of the backup file (e.g., s3://bucket/key)
    """
    try:
        # Initialize the state tracker
        state_tracker = _initialize_state_tracker()
        
        # Set the state tracker in the backup manager
        backup_manager.set_state_tracker(state_tracker)
        
        # Download the backup
        local_path = backup_manager.download_from_cloud(s3_url)
        
        if local_path:
            print(f"Backup downloaded to: {local_path}")
        else:
            print("Failed to download backup.")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error downloading backup: {e}")
        sys.exit(1)


def restore_backup(backup_path: str) -> None:
    """
    Restore from a backup.
    
    Args:
        backup_path: Path to the backup file to restore from
    """
    try:
        # Check if the backup file exists
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            sys.exit(1)
        
        # Initialize the state tracker
        state_tracker = _initialize_state_tracker()
        
        # Set the state tracker in the backup manager
        backup_manager.set_state_tracker(state_tracker)
        
        # Confirm the restore
        print(f"Are you sure you want to restore from {backup_path}? This will overwrite the current state.")
        confirmation = input("Type 'yes' to confirm: ")
        
        if confirmation.lower() != "yes":
            print("Restore cancelled.")
            return
        
        # Restore from the backup
        success = backup_manager.restore_from_backup(backup_path)
        
        if success:
            print(f"Successfully restored from backup: {backup_path}")
        else:
            print(f"Failed to restore from backup: {backup_path}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error restoring from backup: {e}")
        sys.exit(1)


def _initialize_state_tracker() -> EternaStateTracker:
    """
    Initialize the state tracker.
    
    Returns:
        EternaStateTracker: The initialized state tracker
    """
    try:
        # Get the save path from configuration
        save_path = config.get("state_tracker.save_path", "logs/state_snapshot.json")
        
        # Get the database configuration
        use_database = config.get("state_tracker.use_database", False)
        db_path = config.get("state_tracker.db_path", "data/eternia.db")
        
        # Initialize the state tracker
        state_tracker = EternaStateTracker(
            save_path=save_path,
            use_database=use_database,
            db_path=db_path,
        )
        
        return state_tracker
    
    except Exception as e:
        logger.error(f"Error initializing state tracker: {e}")
        sys.exit(1)


def show_help() -> None:
    """Show help message."""
    print(__doc__)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Eternia Backup Recovery Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a backup from S3")
    download_parser.add_argument("s3_url", help="S3 URL of the backup file")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from a backup")
    restore_parser.add_argument("backup_path", help="Path to the backup file")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show help message")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "list":
        list_backups()
    elif args.command == "download":
        download_backup(args.s3_url)
    elif args.command == "restore":
        restore_backup(args.backup_path)
    elif args.command == "help" or args.command is None:
        show_help()
    else:
        print(f"Unknown command: {args.command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()