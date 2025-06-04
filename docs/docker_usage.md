# Docker Usage Guide for Eternia

This document explains how to use Docker for development, testing, and deployment of the Eternia project.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0.0 or higher)

## Project Structure

The Eternia project is containerized with Docker and consists of the following components:

- **Backend**: Python FastAPI application
- **Frontend**: React application with TypeScript
- **Simulation**: Python simulation engine

## Docker Files

The project includes the following Docker-related files:

- `Dockerfile`: Backend Dockerfile for the API and simulation
- `docker-entrypoint.sh`: Entrypoint script for the backend container
- `ui/Dockerfile`: Frontend Dockerfile for production
- `ui/Dockerfile.dev`: Frontend Dockerfile for development with hot reloading
- `ui/nginx.conf`: Nginx configuration for the frontend
- `docker-compose.yml`: Docker Compose configuration for local development

## Basic Usage

### Starting the Application

To start the entire application (backend API and frontend):

```bash
docker-compose up
```

This will start the backend API on port 8000 and the frontend on port 80.

### Development Mode

For development with hot reloading for the frontend:

```bash
docker-compose --profile dev up
```

This will start the backend API on port 8000 and the development frontend on port 3000.

### Running the Simulation

To run the simulation:

```bash
docker-compose --profile simulation up simulation
```

You can customize the simulation by modifying the `command` in the `docker-compose.yml` file.

### Building the Images

To build the Docker images without starting the containers:

```bash
docker-compose build
```

### Stopping the Application

To stop all running containers:

```bash
docker-compose down
```

## Environment Configuration

The Docker setup respects the environment configuration described in `docs/environment_setup.md`. By default, the containers run in the `development` environment.

To run in a different environment:

```bash
ETERNIA_ENV=production docker-compose up
```

## Accessing the Services

- **Backend API**: http://localhost:8000
- **Frontend (Production)**: http://localhost
- **Frontend (Development)**: http://localhost:3000

## Container Management

### Viewing Logs

To view logs from all containers:

```bash
docker-compose logs
```

To view logs from a specific container:

```bash
docker-compose logs backend
```

To follow the logs:

```bash
docker-compose logs -f
```

### Executing Commands

To execute a command in a running container:

```bash
docker-compose exec backend bash
```

### Restarting Services

To restart a specific service:

```bash
docker-compose restart backend
```

## Production Deployment

For production deployment, it's recommended to:

1. Build the images with production settings:
   ```bash
   ETERNIA_ENV=production docker-compose build
   ```

2. Push the images to a container registry:
   ```bash
   docker tag eternia-backend your-registry/eternia-backend:latest
   docker tag eternia-frontend your-registry/eternia-frontend:latest
   docker push your-registry/eternia-backend:latest
   docker push your-registry/eternia-frontend:latest
   ```

3. Deploy using Docker Compose or Kubernetes in your production environment.

## Troubleshooting

### Common Issues

1. **Port conflicts**: If you already have services running on ports 8000 or 80, you'll need to modify the port mappings in `docker-compose.yml`.

2. **Permission issues**: If you encounter permission issues with volumes, ensure your user has appropriate permissions or run Docker with elevated privileges.

3. **Build failures**: If the build fails, check the Docker logs for details. You might need to install additional system dependencies.

### Resetting the Environment

To completely reset your Docker environment:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Best Practices

1. **Use volumes for development**: The Docker Compose configuration mounts the project directories as volumes for development, allowing you to make changes without rebuilding the containers.

2. **Use environment variables**: Use environment variables to configure the application for different environments.

3. **Keep images small**: The multi-stage build for the frontend keeps the production image small by only including the built assets.

4. **Use health checks**: Health checks ensure that the services are running correctly.

5. **Use profiles**: Docker Compose profiles allow you to start only the services you need.