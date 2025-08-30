#!/bin/bash
# Blue/Green Deployment Script for Eternia
# This script performs a blue/green deployment using AWS CodeDeploy

set -e

# Default values
ENVIRONMENT="dev"
APP_NAME="eternia"
DEPLOYMENT_GROUP_NAME=""
S3_BUCKET=""
S3_KEY=""
DESCRIPTION="Deployment triggered by CI/CD pipeline"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --environment|-e)
      ENVIRONMENT="$2"
      shift
      shift
      ;;
    --app-name|-a)
      APP_NAME="$2"
      shift
      shift
      ;;
    --deployment-group|-d)
      DEPLOYMENT_GROUP_NAME="$2"
      shift
      shift
      ;;
    --s3-bucket|-b)
      S3_BUCKET="$2"
      shift
      shift
      ;;
    --s3-key|-k)
      S3_KEY="$2"
      shift
      shift
      ;;
    --description|-desc)
      DESCRIPTION="$2"
      shift
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --environment, -e     The deployment environment (dev, staging, prod)"
      echo "  --app-name, -a        The name of the application"
      echo "  --deployment-group, -d The name of the deployment group"
      echo "  --s3-bucket, -b       The S3 bucket containing the deployment package"
      echo "  --s3-key, -k          The S3 key of the deployment package"
      echo "  --description, -desc   A description for the deployment"
      echo "  --help, -h            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [ -z "$S3_BUCKET" ] || [ -z "$S3_KEY" ]; then
  echo "Error: S3 bucket and key are required"
  exit 1
fi

# If deployment group name is not provided, use the default format
if [ -z "$DEPLOYMENT_GROUP_NAME" ]; then
  DEPLOYMENT_GROUP_NAME="${APP_NAME}-deployment-group-${ENVIRONMENT}"
fi

# Full application name with environment
FULL_APP_NAME="${APP_NAME}-${ENVIRONMENT}"

echo "Starting blue/green deployment for $FULL_APP_NAME..."

# Create a deployment
DEPLOYMENT_ID=$(aws deploy create-deployment \
  --application-name "$FULL_APP_NAME" \
  --deployment-group-name "$DEPLOYMENT_GROUP_NAME" \
  --revision "revisionType=S3,s3Location={bucket=$S3_BUCKET,key=$S3_KEY,bundleType=zip}" \
  --description "$DESCRIPTION" \
  --output text \
  --query 'deploymentId')

echo "Deployment created with ID: $DEPLOYMENT_ID"

# Wait for the deployment to complete
echo "Waiting for deployment to complete..."
aws deploy wait deployment-successful --deployment-id "$DEPLOYMENT_ID"

# Get the deployment status
DEPLOYMENT_STATUS=$(aws deploy get-deployment \
  --deployment-id "$DEPLOYMENT_ID" \
  --query 'deploymentInfo.status' \
  --output text)

echo "Deployment status: $DEPLOYMENT_STATUS"

if [ "$DEPLOYMENT_STATUS" == "Succeeded" ]; then
  echo "Deployment completed successfully!"
  exit 0
else
  echo "Deployment failed with status: $DEPLOYMENT_STATUS"
  exit 1
fi