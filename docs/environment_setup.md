# Environment Setup Guide for Eternia

This document explains how to set up and use the different environments (development, staging, and production) in the Eternia project.

## Overview

Eternia supports three environments:

1. **Development**: For local development and testing
2. **Staging**: For pre-production testing in an environment similar to production
3. **Production**: For the live application

Each environment has its own configuration file in the `config/settings/` directory:
- `default.yaml`: Base configuration for all environments
- `development.yaml`: Development-specific overrides
- `staging.yaml`: Staging-specific overrides
- `production.yaml`: Production-specific overrides

## Setting the Environment

The environment is determined by the `ETERNIA_ENV` environment variable. If not set, it defaults to `development`.

```bash
# Set to development environment
export ETERNIA_ENV=development

# Set to staging environment
export ETERNIA_ENV=staging

# Set to production environment
export ETERNIA_ENV=production
```

## Environment-Specific Features

### Development Environment

- Debug mode enabled
- Detailed error messages
- Lower complexity for faster testing
- All zones are safe for testing
- Local database connection
- Relaxed security settings
- Higher API rate limits

To start the application in development mode:

```bash
export ETERNIA_ENV=development
python main.py
```

### Staging Environment

- Production-like settings
- Test accounts available
- Moderate API rate limits
- Staging database connection
- Near-production security settings

To start the application in staging mode:

```bash
export ETERNIA_ENV=staging
python main.py
```

### Production Environment

- No debug information
- Optimized for performance
- Strict security settings
- Environment variables for sensitive data
- Monitoring and alerting enabled
- Strict API rate limits

To start the application in production mode:

```bash
export ETERNIA_ENV=production
# Set required environment variables
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password
python main.py
```

## Configuration Override Hierarchy

The configuration system follows this hierarchy (from lowest to highest priority):

1. `default.yaml`: Base configuration
2. Environment-specific YAML file (e.g., `development.yaml`)
3. Environment variables (prefixed with `ETERNIA_`)

For example, to override the database host in development:

```bash
export ETERNIA_DATABASE_HOST=custom-db-host
```

## Adding New Configuration

When adding new configuration values:

1. Add the default value to `default.yaml`
2. Override environment-specific values in the appropriate environment files
3. For sensitive data in production, use environment variables

## Best Practices

- Never commit sensitive data (passwords, API keys) to the repository
- Use environment variables for sensitive data in production
- Test configuration changes in development and staging before deploying to production
- Keep environment-specific overrides minimal and focused on what actually needs to change
- Document any new configuration values added to the system