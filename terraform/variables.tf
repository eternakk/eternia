# Eternia Infrastructure as Code
# Variables definition file

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-west-2"  # Default region, can be overridden
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "docker_host" {
  description = "The Docker host to connect to"
  type        = string
  default     = "unix:///var/run/docker.sock"  # Default for local Docker
}

# S3 Backup variables
variable "backup_bucket_name" {
  description = "The name of the S3 bucket for backups"
  type        = string
  default     = "eternia-backups"  # Should be globally unique
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

# Monitoring variables
variable "prometheus_port" {
  description = "The port for Prometheus"
  type        = number
  default     = 9090
}

variable "alertmanager_port" {
  description = "The port for Alertmanager"
  type        = number
  default     = 9093
}

variable "grafana_port" {
  description = "The port for Grafana"
  type        = number
  default     = 3000
}

# Blue/Green Deployment variables
variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "eternia"
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
  default     = ""  # This should be set in terraform.tfvars
}

variable "subnet_ids" {
  description = "The IDs of the subnets"
  type        = list(string)
  default     = []  # This should be set in terraform.tfvars
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

# Database Backup variables
variable "db_backup_bucket_name" {
  description = "The name of the S3 bucket for database backups"
  type        = string
  default     = "eternia-db-backups"
}

variable "db_backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

variable "db_backup_schedule" {
  description = "Cron expression for database backup schedule"
  type        = string
  default     = "0 2 * * ? *"  # Default: 2 AM every day
}

variable "db_backup_notification_email" {
  description = "Email address for database backup notifications"
  type        = string
  default     = "admin@example.com"  # This should be set in terraform.tfvars
}

variable "use_rds" {
  description = "Whether to use RDS or SQLite for the database"
  type        = bool
  default     = false
}

variable "db_instance_id" {
  description = "The ID of the RDS instance (if using RDS)"
  type        = string
  default     = null
}

variable "db_path" {
  description = "Path to the SQLite database file (if using SQLite)"
  type        = string
  default     = "data/eternia.db"
}

# OpenTelemetry variables
variable "otel_collector_port" {
  description = "The port for the OpenTelemetry Collector"
  type        = number
  default     = 4317
}

variable "jaeger_port" {
  description = "The port for Jaeger UI"
  type        = number
  default     = 16686
}

variable "jaeger_collector_port" {
  description = "The port for Jaeger Collector"
  type        = number
  default     = 14250
}

variable "jaeger_agent_port" {
  description = "The port for Jaeger Agent"
  type        = number
  default     = 6831
}

variable "otel_retention_days" {
  description = "Number of days to retain traces"
  type        = number
  default     = 7
}

# Additional variables can be added here as needed
