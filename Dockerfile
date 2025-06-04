# Dockerfile for Eternia Backend
# This Dockerfile builds a Docker image for the Eternia backend.

# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create necessary directories
RUN mkdir -p logs artifacts data

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run_api.py"]