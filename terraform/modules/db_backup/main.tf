# Eternia Infrastructure as Code
# Database Backup and Verification Module

# Variables for the module
variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "eternia"
}

variable "backup_bucket_name" {
  description = "The name of the S3 bucket for backups"
  type        = string
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "backup_schedule" {
  description = "Cron expression for backup schedule"
  type        = string
  default     = "0 2 * * ? *"  # Default: 2 AM every day
}

variable "notification_email" {
  description = "Email address for backup notifications"
  type        = string
}

variable "db_instance_id" {
  description = "The ID of the database instance (if using RDS)"
  type        = string
  default     = null
}

variable "db_path" {
  description = "Path to the SQLite database file (if using SQLite)"
  type        = string
  default     = "data/eternia.db"
}

variable "use_rds" {
  description = "Whether to use RDS or SQLite"
  type        = bool
  default     = false
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

variable "lambda_subnet_ids" {
  description = "Private subnet IDs for Lambda VPC config"
  type        = list(string)
}

variable "lambda_security_group_ids" {
  description = "Security group IDs for Lambda VPC config"
  type        = list(string)
}

variable "lambda_code_signing_config_arn" {
  description = "Lambda code signing configuration ARN"
  type        = string
}

variable "lambda_dlq_target_arn" {
  description = "ARN of the DLQ (SNS/SQS) for Lambda"
  type        = string
}

variable "lambda_reserved_concurrent_executions" {
  description = "Reserved concurrency limit for Lambda"
  type        = number
  default     = 5
}

variable "lambda_env_kms_key_arn" {
  description = "KMS key ARN for encrypting Lambda environment variables"
  type        = string
}

variable "sns_kms_key_id" {
  description = "KMS key ID/ARN for SNS topic encryption"
  type        = string
}

# S3 bucket for database backups
resource "aws_s3_bucket" "db_backup_bucket" {
  bucket = "${var.backup_bucket_name}-${var.environment}"

  logging {
    target_bucket = var.s3_log_bucket
    target_prefix = "${var.app_name}/db-backups/"
  }

  tags = {
    Name        = "Eternia Database Backups"
    Environment = var.environment
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "db_backup_bucket_versioning" {
  bucket = aws_s3_bucket.db_backup_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket lifecycle policy for backup retention
resource "aws_s3_bucket_lifecycle_configuration" "db_backup_lifecycle" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  rule {
    id     = "backup-retention"
    status = "Enabled"

    expiration {
      days = var.backup_retention_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 bucket server-side encryption (KMS)
resource "aws_s3_bucket_server_side_encryption_configuration" "db_backup_encryption" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
  }
}

# SNS topic for backup notifications
resource "aws_sns_topic" "db_backup_notifications" {
  name              = "${var.app_name}-db-backup-notifications-${var.environment}"
  kms_master_key_id = var.sns_kms_key_id
}

# SNS subscription for email notifications
resource "aws_sns_topic_subscription" "db_backup_email_subscription" {
  topic_arn = aws_sns_topic.db_backup_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# IAM role for the backup Lambda function
resource "aws_iam_role" "db_backup_lambda_role" {
  name = "${var.app_name}-db-backup-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for the backup Lambda function
resource "aws_iam_policy" "db_backup_lambda_policy" {
  name        = "${var.app_name}-db-backup-lambda-policy-${var.environment}"
  description = "Policy for the database backup Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.db_backup_bucket.arn,
          "${aws_s3_bucket.db_backup_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "sns:Publish"
        ]
        Effect   = "Allow"
        Resource = aws_sns_topic.db_backup_notifications.arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = [
          aws_cloudwatch_log_group.db_backup_lambda_logs.arn,
          "${aws_cloudwatch_log_group.db_backup_lambda_logs.arn}:*",
          aws_cloudwatch_log_group.db_backup_verification_lambda_logs.arn,
          "${aws_cloudwatch_log_group.db_backup_verification_lambda_logs.arn}:*"
        ]
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "db_backup_lambda_policy_attachment" {
  role       = aws_iam_role.db_backup_lambda_role.name
  policy_arn = aws_iam_policy.db_backup_lambda_policy.arn
}

# Lambda function for database backup
resource "aws_lambda_function" "db_backup_lambda" {
  function_name    = "${var.app_name}-db-backup-${var.environment}"
  role             = aws_iam_role.db_backup_lambda_role.arn
  handler          = "backup_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 300
  memory_size      = 512
  filename         = "${path.module}/lambda/db_backup_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/db_backup_lambda.zip")

  tracing_config {
    mode = "Active"
  }

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = var.lambda_security_group_ids
  }

  dead_letter_config {
    target_arn = var.lambda_dlq_target_arn
  }

  reserved_concurrent_executions = var.lambda_reserved_concurrent_executions
  code_signing_config_arn        = var.lambda_code_signing_config_arn
  kms_key_arn                    = var.lambda_env_kms_key_arn

  environment {
    variables = {
      BACKUP_BUCKET      = aws_s3_bucket.db_backup_bucket.id
      SNS_TOPIC_ARN      = aws_sns_topic.db_backup_notifications.arn
      ENVIRONMENT        = var.environment
      USE_RDS            = var.use_rds ? "true" : "false"
      DB_INSTANCE_ID     = var.use_rds ? var.db_instance_id : ""
      DB_PATH            = var.use_rds ? "" : var.db_path
      RETENTION_DAYS     = var.backup_retention_days
    }
  }
}

# CloudWatch event rule for scheduled backups
resource "aws_cloudwatch_event_rule" "db_backup_schedule" {
  name                = "${var.app_name}-db-backup-schedule-${var.environment}"
  description         = "Schedule for database backups"
  schedule_expression = "cron(${var.backup_schedule})"
}

# CloudWatch event target for the Lambda function
resource "aws_cloudwatch_event_target" "db_backup_target" {
  rule      = aws_cloudwatch_event_rule.db_backup_schedule.name
  target_id = "db-backup-lambda"
  arn       = aws_lambda_function.db_backup_lambda.arn
}

# Permission for CloudWatch to invoke the Lambda function
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.db_backup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.db_backup_schedule.arn
}

# Lambda function for backup verification
resource "aws_lambda_function" "db_backup_verification_lambda" {
  function_name    = "${var.app_name}-db-backup-verification-${var.environment}"
  role             = aws_iam_role.db_backup_lambda_role.arn
  handler          = "verification_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 300
  memory_size      = 512
  filename         = "${path.module}/lambda/db_backup_verification_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/db_backup_verification_lambda.zip")

  tracing_config {
    mode = "Active"
  }

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = var.lambda_security_group_ids
  }

  dead_letter_config {
    target_arn = var.lambda_dlq_target_arn
  }

  reserved_concurrent_executions = var.lambda_reserved_concurrent_executions
  code_signing_config_arn        = var.lambda_code_signing_config_arn
  kms_key_arn                    = var.lambda_env_kms_key_arn

  environment {
    variables = {
      BACKUP_BUCKET      = aws_s3_bucket.db_backup_bucket.id
      SNS_TOPIC_ARN      = aws_sns_topic.db_backup_notifications.arn
      ENVIRONMENT        = var.environment
      USE_RDS            = var.use_rds ? "true" : "false"
    }
  }
}

# S3 event notification for backup verification
resource "aws_s3_bucket_notification" "backup_verification_notification" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.db_backup_verification_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "backups/"
    filter_suffix       = ".db"
  }
}

# Permission for S3 to invoke the verification Lambda function
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.db_backup_verification_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.db_backup_bucket.arn
}

# Outputs
output "backup_bucket_name" {
  description = "The name of the database backup S3 bucket"
  value       = aws_s3_bucket.db_backup_bucket.id
}

output "backup_sns_topic_arn" {
  description = "The ARN of the SNS topic for backup notifications"
  value       = aws_sns_topic.db_backup_notifications.arn
}

output "backup_schedule" {
  description = "The schedule for database backups"
  value       = var.backup_schedule
}
# S3 public access block for the backup bucket
resource "aws_s3_bucket_public_access_block" "db_backup_bucket_pab" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enforce bucket owner as object owner to disable ACLs
resource "aws_s3_bucket_ownership_controls" "db_backup_bucket_ownership" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Require SSL for all requests to the backup bucket
resource "aws_s3_bucket_policy" "db_backup_bucket_ssl_policy" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "DenyInsecureTransport",
        Effect = "Deny",
        Principal = "*",
        Action   = "s3:*",
        Resource = [
          aws_s3_bucket.db_backup_bucket.arn,
          "${aws_s3_bucket.db_backup_bucket.arn}/*"
        ],
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}

# S3 bucket cross-region replication configuration
resource "aws_s3_bucket_replication_configuration" "db_backup_replication" {
  bucket = aws_s3_bucket.db_backup_bucket.id
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
# CloudWatch Log Groups for Lambda functions
resource "aws_cloudwatch_log_group" "db_backup_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.db_backup_lambda.function_name}"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
}

resource "aws_cloudwatch_log_group" "db_backup_verification_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.db_backup_verification_lambda.function_name}"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
}

# KMS key for encrypting CloudWatch Log Groups for DB backup Lambdas
resource "aws_kms_key" "cloudwatch_logs" {
  description         = "KMS key for encrypting CloudWatch Log Groups for DB backup Lambdas"
  enable_key_rotation = true

  tags = {
    Name        = "${var.app_name}-cloudwatch-logs-kms-${var.environment}"
    Environment = var.environment
  }
}
