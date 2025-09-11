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

# S3 bucket for database backups
resource "aws_s3_bucket" "db_backup_bucket" {
  bucket = "${var.backup_bucket_name}-${var.environment}"

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
  }
}

# S3 bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "db_backup_encryption" {
  bucket = aws_s3_bucket.db_backup_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# SNS topic for backup notifications
resource "aws_sns_topic" "db_backup_notifications" {
  name = "${var.app_name}-db-backup-notifications-${var.environment}"
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
        Resource = "arn:aws:logs:*:*:*"
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
  runtime          = "python3.9"
  timeout          = 300
  memory_size      = 512
  filename         = "${path.module}/lambda/db_backup_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/db_backup_lambda.zip")

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
  runtime          = "python3.9"
  timeout          = 300
  memory_size      = 512
  filename         = "${path.module}/lambda/db_backup_verification_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/db_backup_verification_lambda.zip")

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