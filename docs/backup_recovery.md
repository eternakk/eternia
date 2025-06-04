# Backup and Recovery Documentation for Eternia

This document explains the backup and recovery procedures for the Eternia project.

## Overview

The Eternia backup system provides automated daily backups of:
- Database data
- Kubernetes ConfigMaps and Secrets

Backups are stored both locally in the cluster and optionally in an S3-compatible cloud storage service for off-site redundancy.

## Architecture

The backup system is deployed in Kubernetes in a dedicated `backup` namespace. The components are:

- **PersistentVolumeClaim**: Provides persistent storage for backups
- **ConfigMap**: Contains backup and restore scripts
- **CronJob**: Runs the backup script on a schedule
- **Secret**: Stores database credentials and cloud storage configuration
- **ServiceAccount, ClusterRole, ClusterRoleBinding**: Provides necessary permissions

## Backup Schedule

By default, backups run daily at 2:00 AM UTC. This schedule can be modified by editing the CronJob manifest:

```yaml
spec:
  schedule: "0 2 * * *"  # Run daily at 2 AM
```

## Backup Storage

Backups are stored in two locations:

1. **Local Storage**: A PersistentVolumeClaim in the Kubernetes cluster
2. **Cloud Storage** (optional): An S3-compatible bucket

### Local Storage

Local backups are stored on a PersistentVolumeClaim with a default size of 10Gi. This can be modified by editing the PVC manifest:

```yaml
spec:
  resources:
    requests:
      storage: 10Gi
```

### Cloud Storage

To enable cloud storage backups, configure the following in the `backup-credentials` Secret:

```yaml
stringData:
  s3-bucket: "eternia-backups"
  aws-access-key: "your-access-key"
  aws-secret-key: "your-secret-key"
```

## Backup Retention

By default, backups are kept for 7 days, after which they are automatically deleted. This retention period can be modified by editing the backup script in the ConfigMap:

```bash
# Rotate old backups (keep last 7 days)
find ${BACKUP_DIR} -name "eternia-backup-*.tar.gz" -type f -mtime +7 -delete
```

## Backup Contents

Each backup includes:

1. **Database Dump**: A complete dump of the PostgreSQL database
2. **Configuration**: Kubernetes ConfigMaps and Secrets from the production namespace

## Manual Backups

To trigger a manual backup:

```bash
# Create a job from the CronJob
kubectl create job --from=cronjob/database-backup manual-backup -n backup
```

## Viewing Backups

To list available backups:

```bash
# Get the backup pod name
BACKUP_POD=$(kubectl get pods -n backup -l job-name=manual-restore -o jsonpath='{.items[0].metadata.name}')

# List backups
kubectl exec -it $BACKUP_POD -n backup -- ls -la /backups
```

## Recovery Procedures

### Preparing for Recovery

Before performing a recovery, ensure that:

1. You have identified the correct backup to restore from
2. You have communicated the downtime to users
3. You have a rollback plan if the restore fails

### Initiating a Recovery

To restore from a backup:

1. Start the manual restore job:

```bash
kubectl apply -f kubernetes/backup/20-cronjob.yaml
```

2. Wait for the job pod to be running:

```bash
kubectl get pods -n backup -l job-name=manual-restore
```

3. Execute the restore script with the backup file:

```bash
# Get the restore pod name
RESTORE_POD=$(kubectl get pods -n backup -l job-name=manual-restore -o jsonpath='{.items[0].metadata.name}')

# List available backups
kubectl exec -it $RESTORE_POD -n backup -- ls -la /backups

# Restore from a specific backup
kubectl exec -it $RESTORE_POD -n backup -- /scripts/restore-script.sh /backups/eternia-backup-YYYYMMDD-HHMMSS.tar.gz
```

4. Restart the affected deployments:

```bash
kubectl rollout restart deployment/eternia-backend -n eternia-production
```

### Verifying the Recovery

After the restore is complete:

1. Check the application logs for any errors:

```bash
kubectl logs -f deployment/eternia-backend -n eternia-production
```

2. Verify that the application is functioning correctly by accessing it through the browser or API

## Troubleshooting

### Common Issues

1. **Backup Job Fails**:
   - Check the job logs:
     ```bash
     kubectl logs job/database-backup-<timestamp> -n backup
     ```
   - Verify database credentials in the Secret
   - Check PVC storage capacity

2. **Restore Job Fails**:
   - Check the job logs:
     ```bash
     kubectl logs job/manual-restore -n backup
     ```
   - Verify the backup file exists and is not corrupted
   - Check database connection and credentials

3. **S3 Upload Fails**:
   - Verify AWS credentials in the Secret
   - Check S3 bucket permissions
   - Check network connectivity to S3

### Viewing Logs

To view logs for the backup components:

```bash
# Latest backup job logs
kubectl logs -l job-name=database-backup -n backup --tail=100

# Manual restore job logs
kubectl logs -l job-name=manual-restore -n backup --tail=100
```

## Maintenance

### Updating Backup Configuration

To update the backup configuration:

1. Edit the appropriate manifest file:
   - `kubernetes/backup/10-storage.yaml` for storage and scripts
   - `kubernetes/backup/20-cronjob.yaml` for schedule and credentials

2. Apply the changes:

```bash
kubectl apply -f kubernetes/backup/10-storage.yaml
kubectl apply -f kubernetes/backup/20-cronjob.yaml
```

### Testing Backups

It's recommended to periodically test the backup and restore process:

1. Create a test database with sample data
2. Perform a backup
3. Delete the test database
4. Restore from the backup
5. Verify the data is correctly restored

## Best Practices

1. **Regular Testing**: Test the backup and restore process regularly
2. **Off-site Storage**: Always enable cloud storage for off-site redundancy
3. **Encryption**: Consider encrypting sensitive backups
4. **Documentation**: Keep backup procedures and credentials documented in a secure location
5. **Monitoring**: Set up alerts for backup job failures
6. **Audit**: Periodically audit the backup system to ensure it's working correctly