# Backup and Recovery Procedures for Eternia

This document describes the backup and recovery procedures for the Eternia project. It covers the automated backup system, backup configuration, cloud backups, and recovery procedures.

## Overview

The Eternia backup system provides:

- **Automated Backups**: Scheduled backups based on configuration settings
- **Backup Rotation**: Automatic cleanup of old backups based on retention policy
- **Cloud Backups**: Optional backup to cloud storage (AWS S3)
- **Backup Recovery**: Tools for restoring from backups

## Architecture

The backup system consists of the following components:

- **Backup Manager**: Manages the backup process, including scheduling, rotation, and cloud uploads
- **State Tracker**: Provides the actual backup and restore functionality
- **Recovery Script**: Command-line tool for backup recovery operations

## Configuration

Backup settings are configured in the environment-specific YAML files:

```yaml
# Backup configurations
backup:
  enabled: true                # Enable or disable backups
  frequency: "hourly"          # Backup frequency (hourly, daily, weekly, monthly)
  retention_days: 30           # Number of days to retain backups
  storage_path: "/backups"     # Path where backups are stored
  cloud_backup:
    enabled: true              # Enable or disable cloud backups
    provider: "aws"            # Cloud provider (currently only AWS is supported)
    bucket: "eternia-backups"  # S3 bucket name
    region: "us-west-2"        # AWS region
```

### Configuration Options

#### Backup Frequency

- `hourly`: Backups are performed at the start of each hour
- `daily`: Backups are performed at midnight each day
- `weekly`: Backups are performed at midnight on Monday
- `monthly`: Backups are performed at midnight on the first day of each month

#### Retention Policy

The `retention_days` setting determines how long backups are kept before being automatically deleted. Set to 0 to disable automatic cleanup.

#### Cloud Backup

Cloud backups are uploaded to the specified cloud provider. Currently, only AWS S3 is supported. AWS credentials should be provided via environment variables or IAM roles:

- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key

## Automated Backup Process

The backup process works as follows:

1. The backup manager is initialized when the application starts
2. The backup scheduler runs in a background thread
3. At the scheduled time, the backup manager:
   - Creates a backup using the state tracker
   - Uploads the backup to cloud storage (if enabled)
   - Cleans up old backups based on the retention policy

## Backup Types

The system supports two types of backups:

- **Database Backups**: If the application is configured to use a database, the backup is a copy of the database file
- **State Snapshot Backups**: If the application is using JSON files for state storage, the backup is a copy of the state snapshot file

## Backup Storage

Backups are stored in the configured storage path. The default paths are:

- **Development**: `backups/development`
- **Staging**: `backups/staging`
- **Production**: `backups/production`

Each backup file is named with a timestamp, e.g., `eternia_backup_20230101_120000.db` or `eternia_state_20230101_120000.json`.

## Cloud Backups

If cloud backups are enabled, backups are uploaded to the configured cloud provider. Currently, only AWS S3 is supported.

Backups are stored in the S3 bucket with a key that includes the environment and the backup filename, e.g., `production/eternia_backup_20230101_120000.db`.

## Recovery Procedures

### Using the Recovery Script

The recovery script (`scripts/restore_backup.py`) provides a command-line interface for backup recovery operations:

```bash
# List available backups
python scripts/restore_backup.py list

# Download a backup from S3
python scripts/restore_backup.py download s3://eternia-backups/production/eternia_backup_20230101_120000.db

# Restore from a backup
python scripts/restore_backup.py restore backups/production/eternia_backup_20230101_120000.db
```

### Manual Recovery

If the recovery script is not available or not working, you can manually restore from a backup:

1. Stop the application
2. Copy the backup file to the appropriate location:
   - For database backups: Copy to the database file path (default: `data/eternia.db`)
   - For state snapshot backups: Copy to the state snapshot file path (default: `logs/state_snapshot.json`)
3. Start the application

## Backup Verification

It's important to regularly verify that backups are being created and that they can be restored. The following steps should be performed periodically:

1. List the available backups to ensure they are being created
2. Download a backup from cloud storage to verify cloud backups are working
3. Restore from a backup in a test environment to verify the restore process works

## Disaster Recovery

In case of a disaster (e.g., data corruption, hardware failure), follow these steps:

1. Stop the application
2. Identify the most recent valid backup
3. Restore from the backup using the recovery script or manual recovery procedure
4. Start the application
5. Verify that the application is working correctly

## Troubleshooting

### Common Issues

- **Backups not being created**: Check that backups are enabled in the configuration and that the backup scheduler is running
- **Cloud backups not working**: Check the AWS credentials and S3 bucket configuration
- **Restore failing**: Check that the backup file exists and is not corrupted

### Logs

Backup and recovery operations are logged to the application log file. Look for log messages with the prefix `[backup_manager]` or `[backup_recovery]`.

## Best Practices

- Regularly verify that backups are being created and can be restored
- Store backups in multiple locations (local and cloud)
- Test the recovery process periodically
- Monitor the backup process and set up alerts for backup failures
- Document any changes to the backup configuration or recovery procedures

## Conclusion

The automated backup and recovery system provides a robust solution for protecting Eternia's data. By following the procedures outlined in this document, you can ensure that your data is safe and can be recovered in case of a failure.