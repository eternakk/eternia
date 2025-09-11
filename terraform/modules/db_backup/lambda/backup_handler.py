"""
Lambda function for automated database backups.

This function is triggered by a CloudWatch scheduled event and performs
a backup of the Eternia database, either RDS or SQLite.
"""

import os
import json
import boto3
import logging
import sqlite3
import tempfile
import datetime
import subprocess
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')
rds = boto3.client('rds')

def lambda_handler(event, context):
    """
    Lambda function handler for database backups.
    
    Args:
        event: The event dict that contains the parameters passed when the function
               is invoked.
        context: The context in which the function is called.
        
    Returns:
        The result of the backup operation.
    """
    # Get environment variables
    backup_bucket = os.environ.get('BACKUP_BUCKET')
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    environment = os.environ.get('ENVIRONMENT')
    use_rds = os.environ.get('USE_RDS', 'false').lower() == 'true'
    db_instance_id = os.environ.get('DB_INSTANCE_ID', '')
    db_path = os.environ.get('DB_PATH', 'data/eternia.db')
    
    # Generate timestamp for the backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # Perform the backup based on the database type
        if use_rds:
            backup_id = backup_rds_database(db_instance_id, timestamp)
            backup_key = f"backups/rds/{environment}/{db_instance_id}_{timestamp}.snapshot"
            
            # Send success notification
            send_notification(
                sns_topic_arn,
                f"Database backup successful: {db_instance_id}",
                f"RDS snapshot created with ID: {backup_id}"
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'RDS backup successful',
                    'backup_id': backup_id
                })
            }
        else:
            # SQLite backup
            backup_file = backup_sqlite_database(db_path, timestamp)
            backup_key = f"backups/sqlite/{environment}/{os.path.basename(backup_file)}"
            
            # Upload the backup to S3
            upload_to_s3(backup_file, backup_bucket, backup_key)
            
            # Send success notification
            send_notification(
                sns_topic_arn,
                f"Database backup successful: {os.path.basename(db_path)}",
                f"Backup uploaded to S3: {backup_bucket}/{backup_key}"
            )
            
            # Clean up the local backup file
            os.remove(backup_file)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'SQLite backup successful',
                    'backup_key': backup_key
                })
            }
    
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        
        # Send failure notification
        send_notification(
            sns_topic_arn,
            f"Database backup failed: {db_instance_id if use_rds else os.path.basename(db_path)}",
            f"Error: {str(e)}"
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Backup failed',
                'error': str(e)
            })
        }

def backup_rds_database(db_instance_id, timestamp):
    """
    Create a snapshot of an RDS database.
    
    Args:
        db_instance_id: The identifier of the RDS instance.
        timestamp: Timestamp string for the backup.
        
    Returns:
        The identifier of the created snapshot.
    """
    if not db_instance_id:
        raise ValueError("DB instance ID is required for RDS backups")
    
    # Create a snapshot
    snapshot_id = f"{db_instance_id}-backup-{timestamp}"
    
    logger.info(f"Creating RDS snapshot: {snapshot_id}")
    
    response = rds.create_db_snapshot(
        DBSnapshotIdentifier=snapshot_id,
        DBInstanceIdentifier=db_instance_id
    )
    
    return response['DBSnapshot']['DBSnapshotIdentifier']

def backup_sqlite_database(db_path, timestamp):
    """
    Create a backup of a SQLite database.
    
    Args:
        db_path: Path to the SQLite database file.
        timestamp: Timestamp string for the backup.
        
    Returns:
        The path to the backup file.
    """
    # Create a temporary directory for the backup
    temp_dir = tempfile.mkdtemp()
    backup_file = os.path.join(temp_dir, f"eternia_backup_{timestamp}.db")
    
    logger.info(f"Creating SQLite backup: {backup_file}")
    
    # Check if the database file exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    # Create a backup using SQLite's backup API
    conn = sqlite3.connect(db_path)
    backup_conn = sqlite3.connect(backup_file)
    
    try:
        # Perform the backup
        conn.backup(backup_conn)
        
        # Verify the backup
        verify_sqlite_backup(backup_file)
        
        return backup_file
    finally:
        conn.close()
        backup_conn.close()

def verify_sqlite_backup(backup_file):
    """
    Verify the integrity of a SQLite backup.
    
    Args:
        backup_file: Path to the SQLite backup file.
        
    Raises:
        ValueError: If the backup verification fails.
    """
    logger.info(f"Verifying SQLite backup: {backup_file}")
    
    # Connect to the backup file
    conn = sqlite3.connect(backup_file)
    
    try:
        # Run integrity check
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        if result != "ok":
            raise ValueError(f"SQLite integrity check failed: {result}")
        
        logger.info("SQLite backup verification successful")
    finally:
        conn.close()

def upload_to_s3(file_path, bucket, key):
    """
    Upload a file to S3.
    
    Args:
        file_path: Path to the file to upload.
        bucket: S3 bucket name.
        key: S3 object key.
    """
    logger.info(f"Uploading to S3: {bucket}/{key}")
    
    try:
        s3.upload_file(file_path, bucket, key)
        logger.info("Upload successful")
    except ClientError as e:
        logger.error(f"S3 upload failed: {str(e)}")
        raise

def send_notification(topic_arn, subject, message):
    """
    Send a notification to an SNS topic.
    
    Args:
        topic_arn: ARN of the SNS topic.
        subject: Subject of the notification.
        message: Message body.
    """
    if not topic_arn:
        logger.warning("No SNS topic ARN provided, skipping notification")
        return
    
    logger.info(f"Sending notification: {subject}")
    
    try:
        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        logger.info("Notification sent")
    except ClientError as e:
        logger.error(f"Failed to send notification: {str(e)}")
        # Don't raise the exception, as this is a non-critical operation