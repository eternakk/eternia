# Eternia Terraform Guide

This document explains how the Terraform in this repository is organized and how to use it to provision Eternia infrastructure.

## Overview

- Root directory: `terraform/`
- Entry point: `terraform/main.tf`
- Variables: `terraform/variables.tf`
- Example tfvars: `terraform/terraform.tfvars.example`
- Modules:
  - `modules/blue_green_deployment` — Public ALB, HTTPS, blue/green target groups, WAF association, CodeDeploy wiring.
  - `modules/db_backup` — S3 backups for DB, SNS notifications, two Lambda functions (backup + verification), secure-by-default.
  - `modules/s3_backup` — General S3 backup bucket with versioning, lifecycle, KMS, CRR, EventBridge notifications.
  - `modules/opentelemetry` — ECS Fargate deployment for OpenTelemetry Collector + Jaeger with KMS-encrypted logs.
  - `modules/monitoring` — Local monitoring stack variables/hooks (see module source).

The repository targets Terraform >= 1.0 and AWS provider ~> 4.0.

## Prerequisites

- Terraform CLI 1.0+
- AWS account and credentials with sufficient permissions
  - Configure via environment variables, shared credentials file, or SSO (e.g., `aws configure sso`).
- Optionally AWS CLI for profile management

Example environment variables (one option):

```bash
export AWS_PROFILE=your-profile
export AWS_REGION=us-west-2
```

## Providers and State

- Providers declared in `main.tf`:
  - `hashicorp/aws` (~> 4.0)
  - `kreuzwerker/docker` (~> 3.0) for any docker-based utilities
- Default state is local (in `terraform.tfstate`).
- Optional Terraform Cloud/Enterprise backend is scaffolded and commented in `main.tf`. To use it, uncomment the `backend "remote"` block and set your organization/workspace.

## Project Structure and Flow

At a high level, `main.tf` wires variables from `variables.tf` into the modules listed above. Each module encapsulates a specific concern and exposes outputs for downstream use.

Key tagging is applied via provider `default_tags` and/or resource-level `tags` to keep resources identifiable: `Project=Eternia`, `Environment=<env>`, `ManagedBy=Terraform`.

## Configuration

1) Copy the example tfvars and edit values

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars
```

2) Provide missing required values

- Networking for ALB/ECS/Lambda:
  - `vpc_id`
  - `subnet_ids` (private subnets for ECS/Lambdas; public subnets if you intentionally expose the ALB)
- Core app/infrastructure:
  - `app_name`
  - `environment` (e.g., dev, staging, prod)
- Security/compliance knobs (some are required by hardened modules; see Modules section):
  - `lb_logs_bucket` (S3 bucket name to receive ALB access logs)
  - `vpc_cidr` (CIDR used to restrict egress in SGs)
  - `certificate_arn` (ACM cert for HTTPS on ALB)
  - Optionally `web_acl_arn` to attach an existing AWS WAFv2 Web ACL; otherwise module can create one by default
  - KMS keys and replication settings for S3 and CloudWatch as needed

Note: The root `variables.tf` includes a baseline set. Some module hardening variables may not yet be surfaced at root level; you can either:
- Extend `variables.tf` and pass them through in `main.tf`, or
- Override at module call sites directly in `main.tf` for your environment.

## Environments (Workspaces)

We recommend Terraform workspaces to separate state per environment:

```bash
terraform workspace new dev      # one-time
terraform workspace select dev
terraform workspace new staging
terraform workspace new prod
```

Combine workspaces with `environment = "dev|staging|prod"` in `terraform.tfvars` to drive tags and resource naming.

## Usage

Typical workflow from `terraform/` directory:

```bash
terraform init           # install providers and configure backend
terraform validate       # optional sanity check
terraform plan -out tfplan
terraform apply tfplan   # or: terraform apply

# When done
terraform destroy        # destroys resources in the current workspace
```

We recommend using `-out` to save a plan for review/approval. For CI, store plans as artifacts.

## Modules Overview and Important Settings

### blue_green_deployment

- Public Application Load Balancer (ALB) with:
  - HTTPS listener on 443 (TLS 1.2 policy)
  - Access logs enabled (requires `lb_logs_bucket`)
  - Deletion protection enabled
  - Invalid header drop enabled
  - WAFv2 association: pass `web_acl_arn` or the module can create a default ACL with AWS Managed Rules (including Log4j AMR) and associate it.
- Security Group:
  - Ingress 443 from 0.0.0.0/0 (public HTTPS)
  - Egress restricted to `vpc_cidr`
- Target groups for blue/green use HTTPS for traffic and health checks.
- Requires `certificate_arn` (ACM) and VPC/subnets.

Inputs of note (module variables): `environment`, `app_name`, `vpc_id`, `subnet_ids`, `vpc_cidr`, `lb_logs_bucket`, `certificate_arn`, `web_acl_arn` (optional), plus backend/frontend and health-check tunables.

Outputs (examples): target group ARNs, CodeDeploy app/group names.

### db_backup

- S3 bucket for DB backups with:
  - Server-side encryption using KMS (default encryption)
  - Access logging to a logs bucket
  - Versioning enabled
  - Lifecycle rules, including `abort_incomplete_multipart_upload`
  - Public access block
  - Optional cross-region replication (if role and destination provided)
- SNS topic for notifications encrypted with KMS.
- Two Lambda functions:
  - Backup Lambda (scheduled) and Verification Lambda (triggered on S3 object created)
  - X-Ray tracing enabled
  - VPC configuration (private subnets + SGs)
  - DLQ configured
  - Code signing enforced
  - Reserved concurrency set
  - Environment variables encrypted with KMS

Important inputs include: `s3_log_bucket`, `kms_key_id`, `sns_kms_key_id`, `lambda_subnet_ids`, `lambda_security_group_ids`, `lambda_code_signing_config_arn`, `lambda_dlq_target_arn`, `lambda_reserved_concurrent_executions`, `lambda_env_kms_key_arn`, and replication settings if used.

### s3_backup

- General-purpose backup bucket with:
  - Versioning
  - Lifecycle retention
  - KMS default encryption
  - Public access block
  - EventBridge notifications enabled
  - Optional cross-region replication

Inputs include: `s3_log_bucket`, `kms_key_id`, `replication_role_arn`, `replication_destination_bucket_arn`.

### opentelemetry

- ECS Fargate cluster with OpenTelemetry Collector and Jaeger services.
- Security group allows inbound on necessary ports; egress restricted to `vpc_cidr`.
- CloudWatch Log Group:
  - 365-day retention
  - Encrypted with a provided KMS key (`cloudwatch_kms_key_id`).
- ECS services run without public IPs and use AWS Logs drivers.

Inputs include: `vpc_id`, `subnet_ids`, `vpc_cidr`, ports, and `cloudwatch_kms_key_id` for log encryption.

## Secrets and Sensitive Values

- Provide ARNs/IDs for KMS keys, ACM certificates, and DLQs via `terraform.tfvars` or your preferred variable injection method.
- Do not commit real secrets. Use a secure secret manager for shared CI/CD pipelines.

## Checking Security and Compliance

We use hardened defaults. You can also run static checks locally with Checkov:

```bash
pip install checkov
checkov -d .
```

Resolve flagged findings by supplying required variables (e.g., log buckets, KMS keys) or adjusting module inputs.

## Troubleshooting

- Provider authentication errors: verify your AWS profile/role and `AWS_REGION`/`aws_region`.
- ALB HTTPS listener fails to create: ensure `certificate_arn` is in the same region and validated.
- Missing variables for hardened modules: update root `variables.tf` and pass-through in `main.tf`, or set directly at the module call site.
- Lambda packaging: the `db_backup` module expects prebuilt ZIPs under the module `lambda/` paths. Ensure the artifacts exist or adapt the module to build them in CI.

## Destroy and Cleanup

Always select the correct workspace before destroying:

```bash
terraform workspace select dev
terraform destroy
```

Confirm that shared resources (e.g., KMS keys, log buckets, or WAF shared ACLs) are not used by other environments before destroying.

---

For questions or to propose improvements, open an issue or PR. Keep environment-specific defaults in `terraform.tfvars` and avoid hardcoding account-specific values in code.