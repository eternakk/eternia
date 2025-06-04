# Environment Setup Guide

This document provides instructions for setting up and using the different environments in the Eternia project.

## Overview

Eternia supports three environments:

1. **Development**: For local development and testing
2. **Staging**: For pre-production testing and validation
3. **Production**: For the live, user-facing application

Each environment has its own configuration settings that are optimized for its specific purpose.

## Configuration Management

Eternia uses a configuration management system that loads settings from YAML files in the `config/settings` directory. The system loads configuration in the following order:

1. Default settings from `config/settings/default.yaml`
2. Environment-specific settings from `config/settings/{environment}.yaml`
3. Environment variables with the prefix `ETERNIA_`

This allows for a flexible configuration system where default settings can be overridden by environment-specific settings, which can in turn be overridden by environment variables.

## Setting Up the Development Environment

The development environment is designed for local development and testing. It includes features like debug mode, detailed logging, and disabled authentication to make development easier.

### Prerequisites

- Python 3.10 or higher
- Node.js and npm (for frontend development)
- SQLite (included with Python)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/eternia.git
   cd eternia
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set the environment:
   ```bash
   export ETERNIA_ENV=development  # On Windows: set ETERNIA_ENV=development
   ```

5. Start the API server:
   ```bash
   ./run_api.py
   ```

6. In a separate terminal, start the frontend development server:
   ```bash
   cd ui
   npm install
   npm run dev
   ```

7. Access the application at http://localhost:5173

## Setting Up the Staging Environment

The staging environment is designed to be as close as possible to the production environment, but with some additional debugging and testing capabilities. It's used for pre-production testing and validation.

### Prerequisites

- PostgreSQL database
- Node.js and npm (for frontend build)
- Access to the staging server

### Setup Steps

1. Clone the repository on the staging server:
   ```bash
   git clone https://github.com/your-organization/eternia.git
   cd eternia
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   ```bash
   createdb eternia_staging
   ```

5. Set the environment variables:
   ```bash
   export ETERNIA_ENV=staging
   export DB_PASSWORD=your_database_password
   export JWT_SECRET=your_jwt_secret
   ```

6. Build the frontend:
   ```bash
   cd ui
   npm install
   npm run build
   ```

7. Start the API server:
   ```bash
   ./run_api.py
   ```

8. Set up a reverse proxy (like Nginx) to serve the frontend and proxy API requests.

## Setting Up the Production Environment

The production environment is optimized for performance, security, and reliability. It's used for the live, user-facing application.

### Prerequisites

- PostgreSQL database
- Node.js and npm (for frontend build)
- Access to the production server
- AWS account (for cloud backups)

### Setup Steps

1. Clone the repository on the production server:
   ```bash
   git clone https://github.com/your-organization/eternia.git
   cd eternia
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   ```bash
   createdb eternia_production
   ```

5. Set the environment variables:
   ```bash
   export ETERNIA_ENV=production
   export DB_PASSWORD=your_database_password
   export JWT_SECRET=your_jwt_secret
   export AWS_ACCESS_KEY_ID=your_aws_access_key
   export AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   ```

6. Build the frontend:
   ```bash
   cd ui
   npm install
   npm run build
   ```

7. Apply database migrations manually:
   ```bash
   ./scripts/apply_migrations.py
   ```

8. Start the API server using a process manager like Supervisor:
   ```bash
   supervisord -c supervisor.conf
   ```

9. Set up a reverse proxy (like Nginx) with SSL to serve the frontend and proxy API requests.

10. Set up monitoring and alerting using the configured endpoints.

11. Set up automated backups using the configured settings.

## Switching Between Environments

To switch between environments, set the `ETERNIA_ENV` environment variable to the desired environment name:

```bash
export ETERNIA_ENV=development  # For development
export ETERNIA_ENV=staging      # For staging
export ETERNIA_ENV=production   # For production
```

## Environment-Specific Configuration

Each environment has its own configuration file in the `config/settings` directory:

- `development.yaml`: Settings for the development environment
- `staging.yaml`: Settings for the staging environment
- `production.yaml`: Settings for the production environment

These files contain environment-specific settings that override the default settings in `default.yaml`. You can modify these files to customize the behavior of each environment.

## Using Environment Variables

You can override any configuration setting using environment variables with the prefix `ETERNIA_`. For example, to override the `api.port` setting, you would set the environment variable `ETERNIA_API_PORT`:

```bash
export ETERNIA_API_PORT=9000
```

This is particularly useful for sensitive information like database passwords and API keys, which should not be stored in configuration files.

## Conclusion

By setting up proper development, staging, and production environments, you can ensure a smooth development process and reliable deployment of the Eternia application. Each environment is optimized for its specific purpose, with appropriate settings for debugging, security, and performance.