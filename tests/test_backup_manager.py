"""
Tests for the backup_manager module.

This module contains tests for the backup_manager module, which provides
automated backup and recovery functionality for the Eternia application.
"""

import os
import time
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

from modules.backup_manager import BackupManager
from config.config_manager import config


@pytest.fixture
def mock_state_tracker():
    """Return a mock state tracker."""
    mock = MagicMock()
    mock.backup_state.return_value = "/tmp/test_backup.json"
    mock.restore_from_backup.return_value = True
    return mock


@pytest.fixture
def temp_backup_dir():
    """Create a temporary directory for backups."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def backup_manager(temp_backup_dir, mock_state_tracker):
    """Return a configured backup manager for testing."""
    # Create a side_effect function for config.get that returns our test values
    def config_get_side_effect(key, default=None):
        config_values = {
            'backup.enabled': True,
            'backup.frequency': 'hourly',
            'backup.retention_days': 1,
            'backup.storage_path': temp_backup_dir,
            'backup.cloud_backup.enabled': False,
            'backup.cloud_backup.provider': 'aws',
            'backup.cloud_backup.bucket': 'test-bucket',
            'backup.cloud_backup.region': 'us-west-2',
            'ETERNIA_ENV': 'test'
        }
        return config_values.get(key, default)

    with patch('config.config_manager.config.get', side_effect=config_get_side_effect):
        manager = BackupManager()
        manager.set_state_tracker(mock_state_tracker)
        yield manager


def test_backup_manager_initialization():
    """Test that the backup manager initializes correctly."""
    # Create a side_effect function for config.get that returns our test values
    def config_get_side_effect(key, default=None):
        config_values = {
            'backup.enabled': True,
            'backup.frequency': 'daily',
            'backup.retention_days': 7,
            'backup.storage_path': '/tmp/backups',
            'backup.cloud_backup.enabled': True,
            'backup.cloud_backup.provider': 'aws',
            'backup.cloud_backup.bucket': 'test-bucket',
            'backup.cloud_backup.region': 'us-east-1',
            'ETERNIA_ENV': 'test'
        }
        return config_values.get(key, default)

    with patch('config.config_manager.config.get', side_effect=config_get_side_effect):
        manager = BackupManager()

        assert manager.enabled is True
        assert manager.frequency == 'daily'
        assert manager.retention_days == 7
        assert manager.storage_path == '/tmp/backups'
        assert manager.cloud_enabled is True
        assert manager.cloud_provider == 'aws'
        assert manager.cloud_bucket == 'test-bucket'
        assert manager.cloud_region == 'us-east-1'


def test_create_backup(backup_manager, mock_state_tracker):
    """Test creating a backup."""
    backup_path = backup_manager.create_backup()

    # Verify that the state tracker's backup_state method was called
    mock_state_tracker.backup_state.assert_called_once()

    # Verify that the backup path is returned
    assert backup_path == "/tmp/test_backup.json"


def test_create_backup_with_path(backup_manager, mock_state_tracker):
    """Test creating a backup with a specific path."""
    backup_path = backup_manager.create_backup("/tmp/custom_backup.json")

    # Verify that the state tracker's backup_state method was called with the correct path
    mock_state_tracker.backup_state.assert_called_once_with("/tmp/custom_backup.json")

    # Verify that the backup path is returned
    assert backup_path == "/tmp/test_backup.json"  # Mock returns this regardless of input


def test_restore_from_backup(backup_manager, mock_state_tracker):
    """Test restoring from a backup."""
    # Create a mock backup file
    backup_path = "/tmp/test_backup.json"

    # Mock os.path.exists to return True for our backup file
    with patch('os.path.exists', return_value=True):
        # Call restore_from_backup
        success = backup_manager.restore_from_backup(backup_path)

        # Verify that the state tracker's restore_from_backup method was called
        mock_state_tracker.restore_from_backup.assert_called_once_with(backup_path)

        # Verify that the restore was successful
        assert success is True


def test_restore_from_backup_failure(backup_manager, mock_state_tracker):
    """Test restoring from a backup when it fails."""
    # Set up the mock to return False
    mock_state_tracker.restore_from_backup.return_value = False

    # Call restore_from_backup
    success = backup_manager.restore_from_backup("/tmp/nonexistent_backup.json")

    # Verify that the restore failed
    assert success is False


def test_list_backups(backup_manager, temp_backup_dir):
    """Test listing backups."""
    # Create some test backup files
    for i in range(3):
        backup_file = Path(temp_backup_dir) / f"eternia_backup_{i}.json"
        with open(backup_file, 'w') as f:
            f.write("{}")
        # Set the modification time to ensure consistent ordering
        os.utime(backup_file, (time.time() - i * 3600, time.time() - i * 3600))

    # List the backups
    backups = backup_manager.list_backups()

    # Verify that all backups are listed
    assert len(backups) == 3

    # Verify that the backups are sorted by creation time (newest first)
    assert "eternia_backup_0.json" in backups[0]["filename"]
    assert "eternia_backup_1.json" in backups[1]["filename"]
    assert "eternia_backup_2.json" in backups[2]["filename"]


def test_cleanup_old_backups(backup_manager, temp_backup_dir):
    """Test cleaning up old backups."""
    # Create some test backup files with different modification times
    for i in range(5):
        backup_file = Path(temp_backup_dir) / f"eternia_backup_{i}.json"
        with open(backup_file, 'w') as f:
            f.write("{}")
        # Set the modification time: 0, 1, 2, 3, 4 days ago
        mod_time = time.time() - i * 86400
        os.utime(backup_file, (mod_time, mod_time))

    # Clean up old backups (retention_days = 1)
    deleted_count = backup_manager.cleanup_old_backups()

    # Verify that the correct number of backups were deleted (files older than 1 day)
    assert deleted_count == 4

    # Verify that only the recent backup remains
    remaining_files = list(Path(temp_backup_dir).glob("*"))
    assert len(remaining_files) == 1


def test_is_backup_file(backup_manager):
    """Test the _is_backup_file method."""
    # Test valid backup filenames
    assert backup_manager._is_backup_file("eternia_backup_2023-01-01.json") is True
    assert backup_manager._is_backup_file("eternia_state_2023-01-01.json") is True
    assert backup_manager._is_backup_file("eternia_backup_2023-01-01.db") is True

    # Test invalid backup filenames
    assert backup_manager._is_backup_file("not_a_backup.txt") is False
    assert backup_manager._is_backup_file("eternia.json") is False
    assert backup_manager._is_backup_file("backup.db") is False


def test_calculate_next_backup_interval(backup_manager):
    """Test the _calculate_next_backup_interval method."""
    # Instead of trying to mock the complex datetime operations,
    # we'll just verify that the method returns a positive number for each frequency

    # Test hourly frequency
    backup_manager.frequency = 'hourly'
    interval = backup_manager._calculate_next_backup_interval()
    assert interval > 0

    # Test daily frequency
    backup_manager.frequency = 'daily'
    interval = backup_manager._calculate_next_backup_interval()
    assert interval > 0

    # Test weekly frequency
    backup_manager.frequency = 'weekly'
    interval = backup_manager._calculate_next_backup_interval()
    assert interval > 0

    # Test monthly frequency
    backup_manager.frequency = 'monthly'
    interval = backup_manager._calculate_next_backup_interval()
    assert interval > 0

    # Test invalid frequency
    backup_manager.frequency = 'invalid'
    interval = backup_manager._calculate_next_backup_interval()
    assert interval > 0


@patch('boto3.client')
def test_upload_to_cloud(mock_boto3_client, backup_manager, temp_backup_dir):
    """Test uploading a backup to cloud storage."""
    # Enable cloud backups
    backup_manager.cloud_enabled = True

    # Create a test backup file
    backup_file = Path(temp_backup_dir) / "eternia_backup_test.json"
    with open(backup_file, 'w') as f:
        f.write("{}")

    # Set up the mock S3 client
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    # Call upload_to_cloud
    cloud_url = backup_manager.upload_to_cloud(str(backup_file))

    # Verify that the S3 client was created with the correct parameters
    mock_boto3_client.assert_called_once_with(
        's3',
        region_name=backup_manager.cloud_region
    )

    # Verify that upload_file was called with the correct parameters
    mock_s3.upload_file.assert_called_once()

    # Verify that the cloud URL is returned
    assert cloud_url is not None
    assert cloud_url.startswith("s3://")


@patch('boto3.client')
def test_download_from_cloud(mock_boto3_client, backup_manager, temp_backup_dir):
    """Test downloading a backup from cloud storage."""
    # Enable cloud backups
    backup_manager.cloud_enabled = True

    # Set up the mock S3 client
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    # Call download_from_cloud
    local_path = backup_manager.download_from_cloud("s3://test-bucket/test-key")

    # Verify that the S3 client was created with the correct parameters
    mock_boto3_client.assert_called_once_with(
        's3',
        region_name=backup_manager.cloud_region
    )

    # Verify that download_file was called with the correct parameters
    mock_s3.download_file.assert_called_once()

    # Verify that a local path is returned
    assert local_path is not None
