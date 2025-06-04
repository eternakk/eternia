# CI/CD Pipeline Documentation for Eternia

This document explains the Continuous Integration and Continuous Deployment (CI/CD) pipeline set up for the Eternia project.

## Overview

The Eternia project uses GitHub Actions for CI/CD, with the following workflow:

1. **Testing**: Run tests for both backend and frontend on every push and pull request
2. **Building**: Build Docker images for both backend and frontend
3. **Deployment**: Deploy the application to staging or production environments

## Workflow Files

The CI/CD pipeline is defined in the following GitHub Actions workflow files:

- `.github/workflows/test.yml`: Runs tests for both backend and frontend
- `.github/workflows/build-deploy.yml`: Builds Docker images and deploys to staging or production
- `.github/workflows/security-scanning.yml`: Runs security scans on the codebase
- `.github/workflows/gql-scanning.yml`: Runs GraphQL-specific security scans

## Testing Workflow

The testing workflow (`test.yml`) runs on every push to the main branch and on every pull request. It performs the following steps:

1. **Backend Tests**:
   - Runs on multiple Python versions (3.10 and 3.12)
   - Installs dependencies
   - Runs linting with flake8
   - Runs type checking with mypy
   - Runs unit tests with pytest
   - Runs integration tests
   - Uploads coverage reports

2. **Frontend Tests**:
   - Installs dependencies
   - Runs linting
   - Runs type checking
   - Runs unit tests
   - Builds the frontend to ensure it compiles correctly

## Build and Deploy Workflow

The build and deploy workflow (`build-deploy.yml`) runs on:
- Pushes to the main branch (deploys to staging)
- Tag pushes with a version number (deploys to production)
- Manual triggers via workflow dispatch

It performs the following steps:

1. **Build**:
   - Builds Docker images for both backend and frontend
   - Tags images with appropriate version tags
   - Pushes images to GitHub Container Registry

2. **Deploy to Staging**:
   - Runs when changes are pushed to the main branch
   - Updates Kubernetes manifests with the new image tags
   - Applies the manifests to the staging environment
   - Verifies the deployment

3. **Deploy to Production**:
   - Runs when a version tag is pushed or manually triggered
   - Updates Kubernetes manifests with the new image tags
   - Applies the manifests to the production environment
   - Verifies the deployment

## Kubernetes Deployment

The application is deployed to Kubernetes clusters with the following components:

1. **Namespaces**:
   - `eternia-staging`: For the staging environment
   - `eternia-production`: For the production environment

2. **Deployments**:
   - Backend API server
   - Frontend web server

3. **Services**:
   - Backend service
   - Frontend service

4. **Ingress**:
   - Routes traffic to the appropriate services
   - Handles TLS termination
   - Configures domain names

## Environment Configuration

The CI/CD pipeline uses environment-specific configuration:

1. **Staging**:
   - Domain: `staging.eternia.example.com`
   - Environment variable: `ETERNIA_ENV=staging`
   - Kubernetes namespace: `eternia-staging`

2. **Production**:
   - Domain: `eternia.example.com`
   - Environment variable: `ETERNIA_ENV=production`
   - Kubernetes namespace: `eternia-production`

## Secrets Management

The following secrets are required in GitHub repository settings:

- `AWS_ACCESS_KEY_ID`: AWS access key for EKS access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for EKS access
- `AWS_REGION`: AWS region where the EKS clusters are located

## Manual Deployment

To manually trigger a deployment:

1. Go to the Actions tab in the GitHub repository
2. Select the "Build and Deploy" workflow
3. Click "Run workflow"
4. Select the branch to deploy from
5. Select the environment to deploy to (staging or production)
6. Click "Run workflow"

## Rollback Procedure

To roll back to a previous version:

1. Find the tag or commit hash of the version to roll back to
2. Manually trigger the "Build and Deploy" workflow
3. Select the appropriate branch or tag
4. Deploy to the desired environment

Alternatively, you can roll back directly in Kubernetes:

```bash
# Roll back the backend deployment
kubectl rollout undo deployment/eternia-backend -n eternia-production

# Roll back the frontend deployment
kubectl rollout undo deployment/eternia-frontend -n eternia-production
```

## Monitoring Deployments

You can monitor the status of deployments in several ways:

1. **GitHub Actions**: Check the workflow runs in the Actions tab
2. **Kubernetes Dashboard**: View the status of deployments, pods, and services
3. **Kubectl**: Use the following commands:

```bash
# Check deployment status
kubectl get deployments -n eternia-production

# Check pod status
kubectl get pods -n eternia-production

# View logs
kubectl logs deployment/eternia-backend -n eternia-production
```

## Troubleshooting

Common issues and their solutions:

1. **Failed Tests**: Check the test logs in GitHub Actions for details on which tests failed
2. **Failed Builds**: Check the build logs for compilation errors or dependency issues
3. **Failed Deployments**: Check the Kubernetes events and logs:

```bash
# Check events
kubectl get events -n eternia-production

# Check deployment status
kubectl describe deployment eternia-backend -n eternia-production
```

4. **Image Pull Errors**: Ensure the GitHub Container Registry credentials are correctly configured