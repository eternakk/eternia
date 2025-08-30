# Eternia Infrastructure as Code
# OpenTelemetry Module

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

variable "retention_days" {
  description = "Number of days to retain traces"
  type        = number
  default     = 7
}

# Security group for the OpenTelemetry services
resource "aws_security_group" "otel_sg" {
  name        = "${var.app_name}-otel-sg-${var.environment}"
  description = "Security group for OpenTelemetry services"
  vpc_id      = var.vpc_id

  # OpenTelemetry Collector
  ingress {
    from_port   = var.otel_collector_port
    to_port     = var.otel_collector_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Jaeger UI
  ingress {
    from_port   = var.jaeger_port
    to_port     = var.jaeger_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Jaeger Collector
  ingress {
    from_port   = var.jaeger_collector_port
    to_port     = var.jaeger_collector_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Jaeger Agent (UDP)
  ingress {
    from_port   = var.jaeger_agent_port
    to_port     = var.jaeger_agent_port
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-otel-sg-${var.environment}"
    Environment = var.environment
  }
}

# ECS Cluster for OpenTelemetry services
resource "aws_ecs_cluster" "otel_cluster" {
  name = "${var.app_name}-otel-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.app_name}-otel-cluster-${var.environment}"
    Environment = var.environment
  }
}

# CloudWatch Log Group for OpenTelemetry services
resource "aws_cloudwatch_log_group" "otel_logs" {
  name              = "/ecs/${var.app_name}-otel-${var.environment}"
  retention_in_days = var.retention_days

  tags = {
    Name        = "${var.app_name}-otel-logs-${var.environment}"
    Environment = var.environment
  }
}

# Task Definition for OpenTelemetry Collector
resource "aws_ecs_task_definition" "otel_collector" {
  family                   = "${var.app_name}-otel-collector-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "otel-collector"
      image     = "otel/opentelemetry-collector-contrib:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = var.otel_collector_port
          hostPort      = var.otel_collector_port
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      ]
      
      mountPoints = []
      
      volumesFrom = []
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.otel_logs.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "otel-collector"
        }
      }
      
      command = [
        "--config=/etc/otel-collector-config.yaml"
      ]
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:13133/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name        = "${var.app_name}-otel-collector-${var.environment}"
    Environment = var.environment
  }
}

# Task Definition for Jaeger
resource "aws_ecs_task_definition" "jaeger" {
  family                   = "${var.app_name}-jaeger-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "jaeger"
      image     = "jaegertracing/all-in-one:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = var.jaeger_port
          hostPort      = var.jaeger_port
          protocol      = "tcp"
        },
        {
          containerPort = var.jaeger_collector_port
          hostPort      = var.jaeger_collector_port
          protocol      = "tcp"
        },
        {
          containerPort = var.jaeger_agent_port
          hostPort      = var.jaeger_agent_port
          protocol      = "udp"
        }
      ]
      
      environment = [
        {
          name  = "COLLECTOR_ZIPKIN_HOST_PORT"
          value = "9411"
        },
        {
          name  = "SPAN_STORAGE_TYPE"
          value = "elasticsearch"
        }
      ]
      
      mountPoints = []
      
      volumesFrom = []
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.otel_logs.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "jaeger"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "wget -O- http://localhost:16686 || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name        = "${var.app_name}-jaeger-${var.environment}"
    Environment = var.environment
  }
}

# ECS Service for OpenTelemetry Collector
resource "aws_ecs_service" "otel_collector_service" {
  name            = "${var.app_name}-otel-collector-service-${var.environment}"
  cluster         = aws_ecs_cluster.otel_cluster.id
  task_definition = aws_ecs_task_definition.otel_collector.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.otel_sg.id]
    assign_public_ip = true
  }

  tags = {
    Name        = "${var.app_name}-otel-collector-service-${var.environment}"
    Environment = var.environment
  }
}

# ECS Service for Jaeger
resource "aws_ecs_service" "jaeger_service" {
  name            = "${var.app_name}-jaeger-service-${var.environment}"
  cluster         = aws_ecs_cluster.otel_cluster.id
  task_definition = aws_ecs_task_definition.jaeger.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.otel_sg.id]
    assign_public_ip = true
  }

  tags = {
    Name        = "${var.app_name}-jaeger-service-${var.environment}"
    Environment = var.environment
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.app_name}-otel-ecs-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-otel-ecs-execution-role-${var.environment}"
    Environment = var.environment
  }
}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-otel-ecs-task-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-otel-ecs-task-role-${var.environment}"
    Environment = var.environment
  }
}

# IAM Policy Attachment for ECS Task Execution
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Policy for ECS Task
resource "aws_iam_policy" "ecs_task_policy" {
  name        = "${var.app_name}-otel-ecs-task-policy-${var.environment}"
  description = "Policy for OpenTelemetry ECS tasks"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.otel_logs.arn}:*"
      }
    ]
  })
}

# IAM Policy Attachment for ECS Task
resource "aws_iam_role_policy_attachment" "ecs_task_role_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.arn
}

# Data source for current AWS region
data "aws_region" "current" {}

# Outputs
output "otel_collector_endpoint" {
  description = "The endpoint for the OpenTelemetry Collector"
  value       = "http://${aws_ecs_service.otel_collector_service.name}.${var.environment}.local:${var.otel_collector_port}"
}

output "jaeger_endpoint" {
  description = "The endpoint for Jaeger UI"
  value       = "http://${aws_ecs_service.jaeger_service.name}.${var.environment}.local:${var.jaeger_port}"
}

output "otel_cluster_id" {
  description = "The ID of the ECS cluster for OpenTelemetry services"
  value       = aws_ecs_cluster.otel_cluster.id
}