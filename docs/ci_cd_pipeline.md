# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Eternia project.

## Overview

The Eternia project uses GitHub Actions for its CI/CD pipeline. The pipeline consists of several workflows that handle different aspects of the development lifecycle:

1. **Python Tests**: Runs tests for the Python backend code
2. **Docker Build and Test**: Builds and tests Docker images
3. **Frontend CI**: Tests and builds the frontend code
4. **Deploy**: Deploys the application to different environments
5. **Security Scanning**: Performs security scans on the codebase
6. **CodeQL Analysis**: Analyzes the code for security vulnerabilities

## Workflow Descriptions

### Python Tests (`python-tests.yml`)

This workflow runs whenever changes are pushed to the main branch or when a pull request is opened against the main branch. It:

1. Sets up Python 3.10
2. Installs dependencies from requirements.txt
3. Sets up the environment by creating necessary directories and log files
4. Runs all tests using pytest
5. Runs integration tests specifically

### Docker Build and Test (`docker-build.yml`)

This workflow runs whenever changes are pushed to the main branch or when a pull request is opened against the main branch, excluding changes to markdown files and the docs directory. It:

1. Sets up Docker Buildx for efficient Docker image building
2. Builds the backend Docker image
3. Builds the frontend Docker image
4. Sets up a test environment with a .env file
5. Starts the containers using docker-compose
6. Waits for the containers to be ready
7. Runs integration tests against the running containers
8. Checks container logs
9. Stops the containers

### Frontend CI (`frontend-ci.yml`)

This workflow runs whenever changes are pushed to the ui directory or the workflow file itself. It has two jobs:

1. **test-and-build**:
   - Sets up Node.js 18
   - Installs dependencies using npm ci
   - Runs linting
   - Runs type checking
   - Runs tests
   - Builds the frontend
   - Uploads the build artifacts

2. **analyze**:
   - Analyzes bundle size
   - Runs a security audit
   - Checks for outdated dependencies

### Deploy (`deploy.yml`)

This workflow runs when:
- Changes are pushed to the main branch
- Tags starting with 'v' are pushed
- The workflow is manually triggered

It has four jobs:

1. **determine-environment**:
   - Determines which environment to deploy to based on the trigger:
     - If manually triggered, uses the specified environment
     - If a tag starting with 'v' is pushed, deploys to production
     - If a push to the main branch, deploys to staging
     - Otherwise, deploys to development

2. **build-and-push**:
   - Builds and pushes Docker images to GitHub Container Registry
   - Tags the images with the environment name

3. **deploy**:
   - Sets up SSH access to the deployment server
   - Creates a deployment directory
   - Copies the docker-compose.yml file
   - Creates a .env file with environment-specific secrets
   - Deploys the application using docker-compose
   - Verifies the deployment

4. **notify**:
   - Notifies of deployment success or failure

### Security Scanning (`security-scanning.yml`)

This workflow runs security scans on the codebase to identify potential vulnerabilities.

### CodeQL Analysis (`codeql-analysis.yml`)

This workflow uses GitHub's CodeQL to analyze the code for security vulnerabilities.

## Environment Configuration

The CI/CD pipeline uses GitHub Environments for environment-specific configuration and protection rules. The following environments are defined:

1. **development**: For development and testing
2. **staging**: For pre-production testing
3. **production**: For the live, user-facing application

Each environment has its own set of secrets and protection rules. For example, the production environment may require approval before deployment.

## Secrets Management

The CI/CD pipeline uses GitHub Secrets for sensitive information such as:

- `SSH_PRIVATE_KEY`: SSH private key for deployment
- `DEPLOY_HOST`: Hostname of the deployment server
- `DEPLOY_USER`: Username for SSH access to the deployment server
- `DB_PASSWORD`: Database password
- `JWT_SECRET`: JWT secret for authentication

These secrets are environment-specific and are only accessible to workflows running in the appropriate environment.

## Deployment Strategy

The deployment strategy follows these rules:

1. **Development**: Automatic deployment on push to development branches
2. **Staging**: Automatic deployment on push to the main branch
3. **Production**: Manual deployment or automatic deployment on tag push

This strategy ensures that:
- Development environments are updated frequently for testing
- Staging environment is always up-to-date with the latest changes in the main branch
- Production environment is only updated after explicit approval or when a release tag is pushed

## Docker Image Management

Docker images are built and pushed to GitHub Container Registry (ghcr.io) with the following tags:

- Environment name (development, staging, production)
- Branch name (for branch pushes)
- Tag name (for tag pushes)
- Commit SHA (for all pushes)

This tagging strategy ensures that:
- Each environment has a stable image tag
- Each branch, tag, and commit has its own image tag for traceability
- Images can be easily rolled back to a previous version if needed

## Monitoring and Notifications

The CI/CD pipeline includes monitoring and notifications:

- Failed workflows trigger notifications
- Successful deployments trigger notifications
- Deployment verification checks the status of the deployed application

## Setting Up the CI/CD Pipeline

To set up the CI/CD pipeline for a new deployment:

1. Create GitHub Environments for development, staging, and production
2. Add the required secrets to each environment
3. Configure protection rules for sensitive environments (e.g., require approval for production)
4. Ensure the deployment server has Docker and Docker Compose installed
5. Set up SSH access to the deployment server

## Troubleshooting

Common issues and their solutions:

1. **Workflow failures**:
   - Check the workflow logs for error messages
   - Ensure all required secrets are set
   - Verify that the code passes all tests locally

2. **Deployment failures**:
   - Check the SSH connection to the deployment server
   - Ensure the deployment server has sufficient permissions
   - Verify that Docker and Docker Compose are installed on the server

3. **Container issues**:
   - Check the container logs: `docker-compose logs`
   - Verify that all required environment variables are set
   - Ensure the containers have the necessary resources

## Conclusion

The CI/CD pipeline for the Eternia project provides a comprehensive solution for testing, building, and deploying the application to different environments. It ensures that code changes are thoroughly tested before deployment and that deployments are consistent and reliable.