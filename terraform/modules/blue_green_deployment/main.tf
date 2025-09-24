# Eternia Infrastructure as Code
# Blue/Green Deployment Module

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

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "The IDs of the subnets"
  type        = list(string)
}

variable "backend_port" {
  description = "The port for the backend service"
  type        = number
  default     = 8000
}

variable "frontend_port" {
  description = "The port for the frontend service"
  type        = number
  default     = 80
}

variable "health_check_path" {
  description = "The path for health checks"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "The interval for health checks in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "The timeout for health checks in seconds"
  type        = number
  default     = 5
}

variable "health_check_healthy_threshold" {
  description = "The number of consecutive health checks to be considered healthy"
  type        = number
  default     = 2
}

variable "health_check_unhealthy_threshold" {
  description = "The number of consecutive health checks to be considered unhealthy"
  type        = number
  default     = 2
}

# Additional security/compliance variables
variable "lb_logs_bucket" {
  description = "S3 bucket name for ALB access logs"
  type        = string
}

variable "web_acl_arn" {
  description = "ARN of the WAFv2 Web ACL to associate with the public ALB"
  type        = string
  default     = ""
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC to restrict egress rules"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN for the HTTPS listener"
  type        = string
}

# Load balancer for the application
resource "aws_lb" "app_lb" {
  name               = "${var.app_name}-lb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = true
  drop_invalid_header_fields = true

  access_logs {
    bucket  = var.lb_logs_bucket
    prefix  = "${var.app_name}-alb"
    enabled = true
  }

  tags = {
    Name        = "${var.app_name}-lb-${var.environment}"
    Environment = var.environment
  }
}

# Security group for the load balancer
resource "aws_security_group" "lb_sg" {
  name        = "${var.app_name}-lb-sg-${var.environment}"
  description = "Security group for the load balancer"
  vpc_id      = var.vpc_id

  # Allow HTTPS from anywhere
  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Restrict egress to VPC only
  egress {
    description = "Allow all egress within VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "${var.app_name}-lb-sg-${var.environment}"
    Environment = var.environment
  }
}

# Target groups for blue/green deployment
resource "aws_lb_target_group" "blue" {
  name     = "${var.app_name}-blue-${var.environment}"
  port     = var.backend_port
  protocol = "HTTPS"
  vpc_id   = var.vpc_id

  health_check {
    path                = var.health_check_path
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = var.health_check_healthy_threshold
    unhealthy_threshold = var.health_check_unhealthy_threshold
    matcher             = "200"
    protocol            = "HTTPS"
  }

  tags = {
    Name        = "${var.app_name}-blue-${var.environment}"
    Environment = var.environment
    Color       = "blue"
  }
}

resource "aws_lb_target_group" "green" {
  name     = "${var.app_name}-green-${var.environment}"
  port     = var.backend_port
  protocol = "HTTPS"
  vpc_id   = var.vpc_id

  health_check {
    path                = var.health_check_path
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = var.health_check_healthy_threshold
    unhealthy_threshold = var.health_check_unhealthy_threshold
    matcher             = "200"
    protocol            = "HTTPS"
  }

  tags = {
    Name        = "${var.app_name}-green-${var.environment}"
    Environment = var.environment
    Color       = "green"
  }
}

# Listener for HTTPS traffic
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_arn
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue.arn
  }
}

# Listener rule for the frontend
resource "aws_lb_listener_rule" "frontend" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue.arn
  }

  condition {
    path_pattern {
      values = ["/"]
    }
  }

  lifecycle {
    ignore_changes = [action]
  }
}

# Listener rule for the backend API
resource "aws_lb_listener_rule" "backend" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }

  lifecycle {
    ignore_changes = [action]
  }
}

# CodeDeploy application for blue/green deployment
resource "aws_codedeploy_app" "app" {
  name = "${var.app_name}-${var.environment}"
}

# CodeDeploy deployment group for blue/green deployment
resource "aws_codedeploy_deployment_group" "deployment_group" {
  app_name               = aws_codedeploy_app.app.name
  deployment_group_name  = "${var.app_name}-deployment-group-${var.environment}"
  service_role_arn       = aws_iam_role.codedeploy_role.arn
  deployment_config_name = "CodeDeployDefault.AllAtOnce"

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }

    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 5
    }
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  load_balancer_info {
    target_group_info {
      name = aws_lb_target_group.blue.name
    }
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  tags = {
    Name        = "${var.app_name}-deployment-group-${var.environment}"
    Environment = var.environment
  }
}

# IAM role for CodeDeploy
resource "aws_iam_role" "codedeploy_role" {
  name = "${var.app_name}-codedeploy-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-codedeploy-role-${var.environment}"
    Environment = var.environment
  }
}

# IAM policy attachment for CodeDeploy
resource "aws_iam_role_policy_attachment" "codedeploy_policy" {
  role       = aws_iam_role.codedeploy_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
}

# Outputs
output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.app_lb.dns_name
}

output "blue_target_group_arn" {
  description = "The ARN of the blue target group"
  value       = aws_lb_target_group.blue.arn
}

output "green_target_group_arn" {
  description = "The ARN of the green target group"
  value       = aws_lb_target_group.green.arn
}

output "codedeploy_app_name" {
  description = "The name of the CodeDeploy application"
  value       = aws_codedeploy_app.app.name
}

output "codedeploy_deployment_group_name" {
  description = "The name of the CodeDeploy deployment group"
  value       = aws_codedeploy_deployment_group.deployment_group.deployment_group_name
}
# Associate public ALB with WAFv2 Web ACL for protection.
resource "aws_wafv2_web_acl_association" "lb_waf" {
  resource_arn = aws_lb.app_lb.arn
  web_acl_arn  = var.web_acl_arn != "" ? var.web_acl_arn : aws_wafv2_web_acl.lb_web_acl.arn
}

# WAFv2 Web ACL with AWS Managed Rules including Log4j mitigation (used if no external ACL ARN provided)
resource "aws_wafv2_web_acl" "lb_web_acl" {
  name        = "${var.app_name}-alb-web-acl-${var.environment}"
  description = "WAFv2 Web ACL with AWS Managed Rules for external ALB protection"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 0

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-alb-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-alb-anonymous-ip"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesLog4JRCRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLog4JRCRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-alb-log4j"
      sampled_requests_enabled   = true
    }
  }

  # Optionally include the Core rule set for broader coverage
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-alb-common"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-alb-web-acl"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "${var.app_name}-alb-web-acl-${var.environment}"
    Environment = var.environment
  }
}

# IAM role for Kinesis Firehose to deliver WAF logs to S3
resource "aws_iam_role" "waf_firehose_role" {
  name = "${var.app_name}-waf-firehose-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "firehose.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-waf-firehose-role-${var.environment}"
    Environment = var.environment
  }
}

# Minimal S3 permissions for Firehose to write objects
resource "aws_iam_role_policy" "waf_firehose_s3_policy" {
  name = "${var.app_name}-waf-firehose-s3-${var.environment}"
  role = aws_iam_role.waf_firehose_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:::${var.lb_logs_bucket}",
          "arn:aws:s3:::${var.lb_logs_bucket}/*"
        ]
      }
    ]
  })
}

# Kinesis Firehose delivery stream for WAF logs
resource "aws_kinesis_firehose_delivery_stream" "waf_logs" {
  name        = "${var.app_name}-waf-logs-${var.environment}"
  destination = "s3"

  server_side_encryption {
    enabled = true
    key_type = "CUSTOMER_MANAGED_CMK"
    key_arn = aws_kms_key.firehose.arn
  }

  s3_configuration {
    role_arn           = aws_iam_role.waf_firehose_role.arn
    bucket_arn         = "arn:aws:s3:::${var.lb_logs_bucket}"
    prefix             = "waf-logs/"
    buffering_size     = 5
    buffering_interval = 300
    compression_format = "GZIP"
    kms_key_arn        = aws_kms_key.firehose.arn
  }

  tags = {
    Name        = "${var.app_name}-waf-logs-${var.environment}"
    Environment = var.environment
  }
}

# Enable WAFv2 logging to the Firehose stream
resource "aws_wafv2_web_acl_logging_configuration" "lb_waf_logging" {
  resource_arn          = aws_wafv2_web_acl.lb_web_acl.arn
  log_destination_configs = [aws_kinesis_firehose_delivery_stream.waf_logs.arn]

  redacted_fields {
    single_header { name = "authorization" }
  }
}

# KMS key for encrypting Kinesis Firehose delivery stream for WAF logs
data "aws_caller_identity" "current" {}

resource "aws_kms_key" "firehose" {
  description         = "KMS key for encrypting Kinesis Firehose WAF logs stream"
  enable_key_rotation = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowRootAccountAdministrators"
        Effect    = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowFirehoseUsage"
        Effect = "Allow"
        Principal = {
          Service = "firehose.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource  = "*"
        Condition = {
          StringEquals = {
            "kms:EncryptionContext:aws:kinesis:arn" = aws_kinesis_firehose_delivery_stream.waf_logs.arn
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-firehose-kms-${var.environment}"
    Environment = var.environment
  }
}
