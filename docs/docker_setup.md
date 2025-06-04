# Docker Setup Guide

This document provides instructions for using Docker with the Eternia project.

## Overview

Eternia has been containerized using Docker to ensure consistent deployment across different environments. The containerization includes:

1. A Dockerfile for the backend (Python/FastAPI)
2. A Dockerfile for the frontend (React/TypeScript)
3. A docker-compose.yml file for orchestrating the services
4. .dockerignore files to optimize the build process

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Running the Application with Docker Compose

The easiest way to run the entire Eternia application stack is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/eternia.git
   cd eternia
   ```

2. Create a `.env` file with your environment variables (optional):
   ```bash
   ETERNIA_ENV=development
   DB_PASSWORD=your_secure_password
   JWT_SECRET=your_jwt_secret
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs (in development mode)
   - Database Admin: http://localhost:8080 (in development mode)

5. To stop the services:
   ```bash
   docker-compose down
   ```

### Environment-Specific Configurations

You can run the application in different environments by setting the `ETERNIA_ENV` environment variable:

```bash
# Development environment
ETERNIA_ENV=development docker-compose up -d

# Staging environment
ETERNIA_ENV=staging docker-compose up -d

# Production environment
ETERNIA_ENV=production docker-compose up -d
```

Each environment uses its corresponding configuration file from `config/settings/{environment}.yaml`.

## Building and Running Individual Containers

### Backend Container

To build and run only the backend container:

```bash
# Build the backend image
docker build -t eternia-backend .

# Run the backend container
docker run -p 8000:8000 -e ETERNIA_ENV=development eternia-backend
```

### Frontend Container

To build and run only the frontend container:

```bash
# Build the frontend image
docker build -t eternia-frontend -f ui/Dockerfile ui/

# Run the frontend container
docker run -p 80:80 eternia-frontend
```

## Development Workflow with Docker

### Using Docker for Development

For development, you can use Docker Compose with volume mounts to enable hot reloading:

```bash
# Start the services with development profile
docker-compose --profile dev up -d
```

This will:
- Mount your local code into the containers
- Enable hot reloading for the frontend
- Provide database admin tools

### Running Tests in Docker

To run tests inside Docker:

```bash
# Run backend tests
docker-compose run --rm backend pytest

# Run frontend tests
docker-compose run --rm frontend npm test
```

## Production Deployment

For production deployment:

1. Set secure passwords and secrets in environment variables:
   ```bash
   export ETERNIA_ENV=production
   export DB_PASSWORD=your_secure_production_password
   export JWT_SECRET=your_secure_production_jwt_secret
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. For production, consider using a reverse proxy like Nginx or Traefik with SSL termination in front of the services.

## Docker Image Management

### Tagging Images

For version control of Docker images:

```bash
# Tag the backend image
docker tag eternia-backend your-registry/eternia-backend:v1.0.0

# Tag the frontend image
docker tag eternia-frontend your-registry/eternia-frontend:v1.0.0
```

### Pushing Images to a Registry

To push the images to a Docker registry:

```bash
# Push the backend image
docker push your-registry/eternia-backend:v1.0.0

# Push the frontend image
docker push your-registry/eternia-frontend:v1.0.0
```

## Troubleshooting

### Common Issues

1. **Database connection issues**:
   - Ensure the database container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`

2. **Frontend not connecting to backend**:
   - Ensure the backend container is running: `docker-compose ps`
   - Check backend logs: `docker-compose logs backend`
   - Verify the API URL in the frontend configuration

3. **Container not starting**:
   - Check container logs: `docker-compose logs [service_name]`
   - Verify environment variables are set correctly

### Viewing Logs

To view logs from the containers:

```bash
# View logs from all services
docker-compose logs

# View logs from a specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f
```

## Conclusion

Using Docker with Eternia ensures consistent deployment across different environments and simplifies the development workflow. The containerization approach allows for easy scaling, deployment, and management of the application.