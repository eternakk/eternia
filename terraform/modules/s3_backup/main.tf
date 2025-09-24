# Eternia Infrastructure as Code
# S3 Backup Module

# Variables for the module
variable "bucket_name" {
  description = "The name of the S3 bucket for backups"
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

# Additional security/compliance variables
variable "s3_log_bucket" {
  description = "S3 bucket for access logs"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID/ARN for S3 default encryption"
  type        = string
}

variable "replication_role_arn" {
  description = "IAM role ARN for S3 replication"
  type        = string
}

variable "replication_destination_bucket_arn" {
  description = "Destination bucket ARN for cross-region replication"
  type        = string
}

# S3 bucket for backups
resource "aws_s3_bucket" "backup_bucket" {
  bucket = "${var.bucket_name}-${var.environment}"

  logging {
    target_bucket = var.s3_log_bucket
    target_prefix = "s3-backups/"
  }

  tags = {
    Name        = "Eternia Backups"
    Environment = var.environment
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "backup_bucket_versioning" {
  bucket = aws_s3_bucket.backup_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket lifecycle policy for backup retention
resource "aws_s3_bucket_lifecycle_configuration" "backup_lifecycle" {
  bucket = aws_s3_bucket.backup_bucket.id

  rule {
    id     = "backup-retention"
    status = "Enabled"

    expiration {
      days = var.retention_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 bucket server-side encryption (KMS)
resource "aws_s3_bucket_server_side_encryption_configuration" "backup_encryption" {
  bucket = aws_s3_bucket.backup_bucket.id

  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
  }
}

# IAM policy for backup access
resource "aws_iam_policy" "backup_policy" {
  name        = "eternia-backup-policy-${var.environment}"
  description = "Policy for Eternia backup access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.backup_bucket.arn,
          "${aws_s3_bucket.backup_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Outputs
output "backup_bucket_name" {
  description = "The name of the backup S3 bucket"
  value       = aws_s3_bucket.backup_bucket.id
}

output "backup_bucket_arn" {
  description = "The ARN of the backup S3 bucket"
  value       = aws_s3_bucket.backup_bucket.arn
}

output "backup_policy_arn" {
  description = "The ARN of the backup IAM policy"
  value       = aws_iam_policy.backup_policy.arn
}
# S3 public access block for the backup bucket
resource "aws_s3_bucket_public_access_block" "backup_bucket_pab" {
  bucket = aws_s3_bucket.backup_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enforce bucket owner as object owner to disable ACLs
resource "aws_s3_bucket_ownership_controls" "backup_bucket_ownership" {
  bucket = aws_s3_bucket.backup_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Require SSL for all requests to the backup bucket
resource "aws_s3_bucket_policy" "backup_bucket_ssl_policy" {
  bucket = aws_s3_bucket.backup_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "DenyInsecureTransport",
        Effect = "Deny",
        Principal = "*",
        Action   = "s3:*",
        Resource = [
          aws_s3_bucket.backup_bucket.arn,
          "${aws_s3_bucket.backup_bucket.arn}/*"
        ],
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}

# Enable S3 bucket notifications via EventBridge
resource "aws_s3_bucket_notification" "backup_notifications" {
  bucket      = aws_s3_bucket.backup_bucket.id
  eventbridge = true
}

# S3 bucket cross-region replication configuration
resource "aws_s3_bucket_replication_configuration" "backup_replication" {
  bucket = aws_s3_bucket.backup_bucket.id
  role   = var.replication_role_arn

  rule {
    id     = "crr"
    status = "Enabled"

    destination {
      bucket        = var.replication_destination_bucket_arn
      storage_class = "STANDARD"
    }
  }
}
