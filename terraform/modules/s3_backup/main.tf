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

# S3 bucket for backups
resource "aws_s3_bucket" "backup_bucket" {
  bucket = "${var.bucket_name}-${var.environment}"

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
  }
}

# S3 bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "backup_encryption" {
  bucket = aws_s3_bucket.backup_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
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