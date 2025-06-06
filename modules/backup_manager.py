"""
Backup Manager for Eternia

This module provides automated backup and recovery functionality for the Eternia application.
It implements scheduled backups, backup rotation, and cloud backups based on configuration settings.

Example usage:
    from modules.backup_manager import backup_manager
    
    # Start the backup scheduler
    backup_manager.start_scheduler()
    
    # Perform a manual backup
    backup_path = backup_manager.create_backup()
    
    # Upload a backup to cloud storage
    cloud_url = backup_manager.upload_to_cloud(backup_path)
    
    # Restore from a backup
    success = backup_manager.restore_from_backup(backup_path)
"""

import os
import time
import logging
import datetime
import threading
import shutil
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from config.config_manager import config
from modules.validation import validate_params, validate_type, validate_non_empty_string

# Configure logging
logger = logging.getLogger(__name__)

class BackupManager:
    """
    Manages automated backups and recovery for the Eternia application.
    
    This class provides functionality for:
    - Scheduled backups based on configuration settings
    - Backup rotation and cleanup based on retention policy
    - Cloud backups to AWS S3 or other providers
    - Backup recovery
    """
    
    def __init__(self) -> None:
        """Initialize the backup manager."""
        # Load configuration
        self.enabled = config.get('backup.enabled', False)
        self.frequency = config.get('backup.frequency', 'daily')
        self.retention_days = config.get('backup.retention_days', 7)
        self.storage_path = config.get('backup.storage_path', 'backups')
        
        # Cloud backup configuration
        self.cloud_enabled = config.get('backup.cloud_backup.enabled', False)
        self.cloud_provider = config.get('backup.cloud_backup.provider', 'aws')
        self.cloud_bucket = config.get('backup.cloud_backup.bucket', 'eternia-backups')
        self.cloud_region = config.get('backup.cloud_backup.region', 'us-west-2')
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize scheduler
        self.scheduler_thread = None
        self.scheduler_running = False
        
        # Initialize state tracker reference (will be set later)
        self.state_tracker = None
        
        logger.info("Backup manager initialized")
    
    def set_state_tracker(self, state_tracker) -> None:
        """
        Set the state tracker reference.
        
        Args:
            state_tracker: The state tracker instance
        """
        self.state_tracker = state_tracker
        logger.info("State tracker reference set in backup manager")
    
    def start_scheduler(self) -> None:
        """
        Start the backup scheduler.
        
        This method starts a background thread that performs backups according to the
        configured frequency.
        """
        if not self.enabled:
            logger.info("Backup scheduler not started because backups are disabled")
            return
        
        if self.scheduler_running:
            logger.warning("Backup scheduler is already running")
            return
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"Backup scheduler started with frequency: {self.frequency}")
    
    def stop_scheduler(self) -> None:
        """Stop the backup scheduler."""
        if not self.scheduler_running:
            logger.warning("Backup scheduler is not running")
            return
        
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            self.scheduler_thread = None
        
        logger.info("Backup scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """
        Background thread that performs scheduled backups.
        
        This method runs in a loop, sleeping for the appropriate interval between backups
        based on the configured frequency.
        """
        while self.scheduler_running:
            try:
                # Perform a backup
                self.create_backup()
                
                # Clean up old backups
                self.cleanup_old_backups()
                
                # Calculate the next backup time based on frequency
                sleep_seconds = self._calculate_next_backup_interval()
                
                # Sleep until the next backup
                for _ in range(int(sleep_seconds / 10)):  # Check every 10 seconds if we should stop
                    if not self.scheduler_running:
                        break
                    time.sleep(10)
                
                # Sleep any remaining seconds
                remaining_seconds = sleep_seconds % 10
                if remaining_seconds > 0 and self.scheduler_running:
                    time.sleep(remaining_seconds)
                    
            except Exception as e:
                logger.error(f"Error in backup scheduler: {e}")
                # Sleep for a minute before retrying
                time.sleep(60)
    
    def _calculate_next_backup_interval(self) -> int:
        """
        Calculate the number of seconds until the next backup.
        
        Returns:
            int: Number of seconds until the next backup
        """
        now = datetime.datetime.now()
        
        if self.frequency == 'hourly':
            # Next hour
            next_backup = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            return (next_backup - now).total_seconds()
        
        elif self.frequency == 'daily':
            # Next day at midnight
            next_backup = (now.replace(hour=0, minute=0, second=0, microsecond=0) 
                          + datetime.timedelta(days=1))
            return (next_backup - now).total_seconds()
        
        elif self.frequency == 'weekly':
            # Next Monday at midnight
            days_ahead = 7 - now.weekday()  # 0 = Monday, 6 = Sunday
            if days_ahead == 0:  # Today is Monday
                days_ahead = 7
            next_backup = (now.replace(hour=0, minute=0, second=0, microsecond=0) 
                          + datetime.timedelta(days=days_ahead))
            return (next_backup - now).total_seconds()
        
        elif self.frequency == 'monthly':
            # First day of next month at midnight
            if now.month == 12:
                next_backup = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0)
            else:
                next_backup = datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0)
            return (next_backup - now).total_seconds()
        
        else:
            # Default to daily if frequency is not recognized
            logger.warning(f"Unrecognized backup frequency: {self.frequency}, defaulting to daily")
            next_backup = (now.replace(hour=0, minute=0, second=0, microsecond=0) 
                          + datetime.timedelta(days=1))
            return (next_backup - now).total_seconds()
    
    @validate_params(backup_path=lambda v, p: validate_type(v, (str, type(None)), p))
    def create_backup(self, backup_path: Optional[str] = None) -> Optional[str]:
        """
        Create a backup of the current state.
        
        Args:
            backup_path: Path where the backup will be saved. If None, a default path
                        will be generated based on the current timestamp.
        
        Returns:
            Optional[str]: The path to the backup file, or None if the backup failed.
            
        Raises:
            TypeValidationError: If backup_path is not a string or None
        """
        if not self.state_tracker:
            logger.error("Cannot create backup: state tracker not set")
            return None
        
        try:
            # Use the state tracker to create a backup
            backup_path = self.state_tracker.backup_state(backup_path)
            
            if backup_path and self.cloud_enabled:
                # Upload to cloud storage
                cloud_url = self.upload_to_cloud(backup_path)
                if cloud_url:
                    logger.info(f"Backup uploaded to cloud: {cloud_url}")
                else:
                    logger.warning("Failed to upload backup to cloud")
            
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    @validate_params(backup_path=lambda v, p: validate_non_empty_string(v, p))
    def upload_to_cloud(self, backup_path: str) -> Optional[str]:
        """
        Upload a backup file to cloud storage.
        
        Args:
            backup_path: Path to the backup file to upload
            
        Returns:
            Optional[str]: The URL of the uploaded file, or None if the upload failed
            
        Raises:
            TypeValidationError: If backup_path is not a string
            ValueValidationError: If backup_path is an empty string
        """
        if not self.cloud_enabled:
            logger.warning("Cloud backup is disabled")
            return None
        
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return None
        
        try:
            if self.cloud_provider.lower() == 'aws':
                return self._upload_to_aws_s3(backup_path)
            else:
                logger.error(f"Unsupported cloud provider: {self.cloud_provider}")
                return None
        except Exception as e:
            logger.error(f"Error uploading to cloud: {e}")
            return None
    
    def _upload_to_aws_s3(self, backup_path: str) -> Optional[str]:
        """
        Upload a backup file to AWS S3.
        
        Args:
            backup_path: Path to the backup file to upload
            
        Returns:
            Optional[str]: The S3 URL of the uploaded file, or None if the upload failed
        """
        try:
            # Create an S3 client
            s3_client = boto3.client(
                's3',
                region_name=self.cloud_region,
                # AWS credentials should be provided via environment variables or IAM role
            )
            
            # Generate a key for the S3 object
            backup_filename = os.path.basename(backup_path)
            environment = config.get('ETERNIA_ENV', 'development')
            s3_key = f"{environment}/{backup_filename}"
            
            # Upload the file
            s3_client.upload_file(
                backup_path,
                self.cloud_bucket,
                s3_key
            )
            
            # Return the S3 URL
            return f"s3://{self.cloud_bucket}/{s3_key}"
        except ClientError as e:
            logger.error(f"Error uploading to AWS S3: {e}")
            return None
    
    def cleanup_old_backups(self) -> int:
        """
        Delete backups older than the retention period.
        
        Returns:
            int: Number of backups deleted
        """
        if self.retention_days <= 0:
            logger.info("Backup retention is disabled (retention_days <= 0)")
            return 0
        
        try:
            # Calculate the cutoff date
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            
            # Get all backup files
            backup_dir = Path(self.storage_path)
            if not backup_dir.exists():
                return 0
            
            # Find and delete old backups
            deleted_count = 0
            for backup_file in backup_dir.glob("*"):
                if not backup_file.is_file():
                    continue
                
                # Check if the file is a backup (has a timestamp in the filename)
                if not self._is_backup_file(backup_file.name):
                    continue
                
                # Get the file's modification time
                mod_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                # Delete if older than the cutoff date
                if mod_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_file}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backups")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    def _is_backup_file(self, filename: str) -> bool:
        """
        Check if a filename is a backup file.
        
        Args:
            filename: The filename to check
            
        Returns:
            bool: True if the file is a backup file, False otherwise
        """
        # Check for common backup file patterns
        return (
            filename.startswith("eternia_backup_") or
            filename.startswith("eternia_state_") or
            (filename.endswith(".db") and "_" in filename) or
            (filename.endswith(".json") and "_" in filename)
        )
    
    @validate_params(backup_path=lambda v, p: validate_non_empty_string(v, p))
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore from
            
        Returns:
            bool: True if the restore was successful, False otherwise
            
        Raises:
            TypeValidationError: If backup_path is not a string
            ValueValidationError: If backup_path is an empty string
        """
        if not self.state_tracker:
            logger.error("Cannot restore backup: state tracker not set")
            return False
        
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Use the state tracker to restore from the backup
            success = self.state_tracker.restore_from_backup(backup_path)
            
            if success:
                logger.info(f"Successfully restored from backup: {backup_path}")
            else:
                logger.error(f"Failed to restore from backup: {backup_path}")
            
            return success
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups with metadata.
        
        Returns:
            List[Dict[str, Any]]: A list of backup information dictionaries
        """
        try:
            # Get all backup files
            backup_dir = Path(self.storage_path)
            if not backup_dir.exists():
                return []
            
            backups = []
            for backup_file in backup_dir.glob("*"):
                if not backup_file.is_file():
                    continue
                
                # Check if the file is a backup
                if not self._is_backup_file(backup_file.name):
                    continue
                
                # Get file metadata
                stat = backup_file.stat()
                
                # Add to the list
                backups.append({
                    "path": str(backup_file),
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "created": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": "database" if backup_file.suffix == ".db" else "state",
                })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
            return backups
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    @validate_params(backup_path=lambda v, p: validate_non_empty_string(v, p))
    def download_from_cloud(self, backup_path: str) -> Optional[str]:
        """
        Download a backup file from cloud storage.
        
        Args:
            backup_path: The cloud path of the backup file (e.g., s3://bucket/key)
            
        Returns:
            Optional[str]: The local path of the downloaded file, or None if the download failed
            
        Raises:
            TypeValidationError: If backup_path is not a string
            ValueValidationError: If backup_path is an empty string
        """
        if not self.cloud_enabled:
            logger.warning("Cloud backup is disabled")
            return None
        
        try:
            if backup_path.startswith("s3://"):
                return self._download_from_aws_s3(backup_path)
            else:
                logger.error(f"Unsupported cloud path: {backup_path}")
                return None
        except Exception as e:
            logger.error(f"Error downloading from cloud: {e}")
            return None
    
    def _download_from_aws_s3(self, s3_url: str) -> Optional[str]:
        """
        Download a backup file from AWS S3.
        
        Args:
            s3_url: The S3 URL of the backup file (e.g., s3://bucket/key)
            
        Returns:
            Optional[str]: The local path of the downloaded file, or None if the download failed
        """
        try:
            # Parse the S3 URL
            if not s3_url.startswith("s3://"):
                logger.error(f"Invalid S3 URL: {s3_url}")
                return None
            
            parts = s3_url[5:].split("/", 1)
            if len(parts) != 2:
                logger.error(f"Invalid S3 URL format: {s3_url}")
                return None
            
            bucket = parts[0]
            key = parts[1]
            
            # Create an S3 client
            s3_client = boto3.client(
                's3',
                region_name=self.cloud_region,
                # AWS credentials should be provided via environment variables or IAM role
            )
            
            # Generate a local path for the downloaded file
            filename = os.path.basename(key)
            local_path = os.path.join(self.storage_path, filename)
            
            # Download the file
            s3_client.download_file(
                bucket,
                key,
                local_path
            )
            
            logger.info(f"Downloaded backup from S3: {s3_url} to {local_path}")
            return local_path
        except ClientError as e:
            logger.error(f"Error downloading from AWS S3: {e}")
            return None


# Create a singleton instance
backup_manager = BackupManager()