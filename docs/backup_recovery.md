# Backup and Recovery System

This document provides information about the automated backup and recovery system in Eternia.

## Overview

The Eternia backup system provides automated, scheduled backups of application state with configurable frequency, retention policies, and cloud storage integration. It also includes tools for restoring from backups when needed.

## Configuration

Backup settings are configured in the application's configuration files. The following settings are available:

```yaml
backup:
  enabled: true                # Enable or disable automated backups
  frequency: daily             # Backup frequency: hourly, daily, weekly, monthly
  retention_days: 7            # Number of days to keep backups (0 = keep forever)
  storage_path: backups        # Local directory to store backups
  
  cloud_backup:
    enabled: true              # Enable or disable cloud backups
    provider: aws              # Cloud provider (currently only 'aws' is supported)
    bucket: eternia-backups    # S3 bucket name
    region: us-west-2          # AWS region
```

## Automated Backups

When enabled, the backup system automatically creates backups according to the configured frequency:

- **Hourly**: Backups are created at the start of each hour
- **Daily**: Backups are created at midnight each day
- **Weekly**: Backups are created at midnight on Monday
- **Monthly**: Backups are created at midnight on the first day of each month

Backups are stored in the configured `storage_path` directory. Old backups are automatically deleted based on the `retention_days` setting.

## Cloud Backups

When cloud backups are enabled, each backup is automatically uploaded to the configured cloud storage provider. Currently, only AWS S3 is supported.

AWS credentials should be provided through environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) or through an IAM role if running on AWS infrastructure.

## Manual Backup and Recovery

### Creating a Manual Backup

You can create a manual backup using the backup manager API:

```python
from modules.backup_manager import backup_manager

# Create a backup
backup_path = backup_manager.create_backup()
print(f"Backup created at: {backup_path}")
```

### Restoring from a Backup

To restore from a backup, use the restore_backup.py script:

```bash
# List available backups
python scripts/restore_backup.py list

# Restore from a specific backup
python scripts/restore_backup.py restore /path/to/backup/file

# Download a backup from S3 and restore
python scripts/restore_backup.py download s3://bucket/key
python scripts/restore_backup.py restore /path/to/downloaded/backup
```

## Backup Rotation and Cleanup

The backup system automatically manages backup rotation based on the `retention_days` setting. Backups older than the specified number of days are automatically deleted during the scheduled backup process.

You can also manually trigger cleanup:

```python
from modules.backup_manager import backup_manager

# Clean up old backups
deleted_count = backup_manager.cleanup_old_backups()
print(f"Deleted {deleted_count} old backups")
```

## Monitoring Backup Status

The backup system logs all activities using the Python logging system. You can monitor backup operations in the application logs.

## Troubleshooting

### Common Issues

1. **Backups not being created automatically**
   - Check if `backup.enabled` is set to `true` in the configuration
   - Verify that the application is running continuously (backups only occur while the application is running)
   - Check the logs for any errors during backup creation

2. **Cloud backups failing**
   - Verify that `backup.cloud_backup.enabled` is set to `true`
   - Check AWS credentials and permissions
   - Ensure the S3 bucket exists and is accessible
   - Check the logs for specific error messages

3. **Restore failing**
   - Verify that the backup file exists and is accessible
   - Check if the backup file is corrupted
   - Check the logs for specific error messages during restore

### Backup File Locations

- Local backups are stored in the directory specified by `backup.storage_path` (default: `backups/`)
- Cloud backups are stored in the specified S3 bucket under a path that includes the environment name

## Best Practices

1. **Regular Testing**: Periodically test the restore process to ensure backups are valid and can be restored successfully
2. **Monitoring**: Set up alerts for backup failures
3. **Redundancy**: Enable cloud backups for an additional layer of protection
4. **Security**: Secure access to backup files and ensure cloud storage is properly secured
5. **Documentation**: Keep track of any manual backups created and their purpose