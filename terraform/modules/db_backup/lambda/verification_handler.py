"""
Lambda function for verifying database backups.

This function is triggered by S3 events when a new backup is uploaded
and verifies the integrity of the backup.
"""

import os
import json
import boto3
import logging
import sqlite3
import tempfile
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
    Lambda function handler for backup verification.
    
    Args:
        event: The event dict that contains the parameters passed when the function
               is invoked.
        context: The context in which the function is called.
        
    Returns:
        The result of the verification operation.
    """
    # Get environment variables
    backup_bucket = os.environ.get('BACKUP_BUCKET')
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    environment = os.environ.get('ENVIRONMENT')
    use_rds = os.environ.get('USE_RDS', 'false').lower() == 'true'
    
    try:
        # Extract bucket and key from the S3 event
        s3_event = event['Records'][0]['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        logger.info(f"Processing backup verification for {bucket}/{key}")
        
        # Determine the type of backup based on the key
        if 'rds' in key:
            # RDS snapshot verification
            if use_rds:
                snapshot_id = os.path.basename(key).split('.')[0]
                verify_rds_snapshot(snapshot_id)
                
                # Send success notification
                send_notification(
                    sns_topic_arn,
                    f"Database backup verification successful: {snapshot_id}",
                    f"RDS snapshot verified: {snapshot_id}"
                )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'RDS backup verification successful',
                        'snapshot_id': snapshot_id
                    })
                }
            else:
                logger.warning("RDS backup found but RDS is not enabled")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Skipping RDS backup verification (RDS not enabled)'
                    })
                }
        else:
            # SQLite backup verification
            temp_file = download_from_s3(bucket, key)
            verify_sqlite_backup(temp_file)
            
            # Clean up the temporary file
            os.remove(temp_file)
            
            # Send success notification
            send_notification(
                sns_topic_arn,
                f"Database backup verification successful: {os.path.basename(key)}",
                f"SQLite backup verified: {bucket}/{key}"
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'SQLite backup verification successful',
                    'backup_key': key
                })
            }
    
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        
        # Send failure notification
        send_notification(
            sns_topic_arn,
            f"Database backup verification failed",
            f"Error: {str(e)}"
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Verification failed',
                'error': str(e)
            })
        }

def verify_rds_snapshot(snapshot_id):
    """
    Verify an RDS snapshot.
    
    Args:
        snapshot_id: The identifier of the RDS snapshot.
        
    Raises:
        ValueError: If the snapshot verification fails.
    """
    logger.info(f"Verifying RDS snapshot: {snapshot_id}")
    
    # Check if the snapshot exists and is available
    response = rds.describe_db_snapshots(
        DBSnapshotIdentifier=snapshot_id
    )
    
    if not response['DBSnapshots']:
        raise ValueError(f"Snapshot not found: {snapshot_id}")
    
    snapshot = response['DBSnapshots'][0]
    status = snapshot['Status']
    
    if status != 'available':
        raise ValueError(f"Snapshot is not available (status: {status})")
    
    logger.info(f"RDS snapshot verification successful: {snapshot_id}")

def download_from_s3(bucket, key):
    """
    Download a file from S3 to a temporary location.
    
    Args:
        bucket: S3 bucket name.
        key: S3 object key.
        
    Returns:
        The path to the downloaded file.
    """
    logger.info(f"Downloading from S3: {bucket}/{key}")
    
    # Create a temporary file
    temp_file = tempfile.mktemp(suffix='.db')
    
    try:
        s3.download_file(bucket, key, temp_file)
        logger.info(f"Download successful: {temp_file}")
        return temp_file
    except ClientError as e:
        logger.error(f"S3 download failed: {str(e)}")
        raise

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
        
        # Check if the database has the expected tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['state', 'memories', 'discoveries', 'explored_zones', 'modifiers', 'checkpoints']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            raise ValueError(f"SQLite backup is missing required tables: {', '.join(missing_tables)}")
        
        logger.info("SQLite backup verification successful")
    finally:
        conn.close()

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