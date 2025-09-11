# Eternia Infrastructure as Code
# Main Terraform configuration file

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }

  # Uncomment this block to use Terraform Cloud for state management
  # backend "remote" {
  #   organization = "eternia"
  #   workspaces {
  #     name = "eternia-infrastructure"
  #   }
  # }

  required_version = ">= 1.0.0"
}

# AWS Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Eternia"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Docker Provider configuration
provider "docker" {
  host = var.docker_host
}

# Local variables
locals {
  common_tags = {
    Project     = "Eternia"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Include other Terraform configuration files
module "s3_backup" {
  source = "./modules/s3_backup"

  bucket_name    = var.backup_bucket_name
  environment    = var.environment
  retention_days = var.backup_retention_days
}

module "monitoring" {
  source = "./modules/monitoring"

  environment = var.environment
  prometheus_port = var.prometheus_port
  alertmanager_port = var.alertmanager_port
  grafana_port = var.grafana_port
}

module "blue_green_deployment" {
  source = "./modules/blue_green_deployment"

  environment = var.environment
  app_name    = var.app_name
  vpc_id      = var.vpc_id
  subnet_ids  = var.subnet_ids

  backend_port  = var.backend_port
  frontend_port = var.frontend_port

  health_check_path = var.health_check_path
}

module "db_backup" {
  source = "./modules/db_backup"

  environment = var.environment
  app_name    = var.app_name
  backup_bucket_name = var.db_backup_bucket_name
  backup_retention_days = var.db_backup_retention_days
  backup_schedule = var.db_backup_schedule
  notification_email = var.db_backup_notification_email

  # Database configuration
  use_rds = var.use_rds
  db_instance_id = var.db_instance_id
  db_path = var.db_path
}

module "opentelemetry" {
  source = "./modules/opentelemetry"

  environment = var.environment
  app_name    = var.app_name
  vpc_id      = var.vpc_id
  subnet_ids  = var.subnet_ids

  # OpenTelemetry configuration
  otel_collector_port = var.otel_collector_port
  jaeger_port = var.jaeger_port
  jaeger_collector_port = var.jaeger_collector_port
  jaeger_agent_port = var.jaeger_agent_port
  retention_days = var.otel_retention_days
}
