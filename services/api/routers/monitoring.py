import logging
import time
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette_exporter import handle_metrics

from modules.monitoring import metrics
from ..deps import world, governor

# Configure logging
logger = logging.getLogger(__name__)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(tags=["monitoring"])


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Exposes metrics in the Prometheus format for monitoring and alerting.",
    response_description="Metrics in Prometheus format",
    responses={
        200: {"description": "Metrics successfully retrieved", "content": {"text/plain": {}}},
        500: {"description": "Internal server error"},
    },
)
async def metrics_endpoint():
    """
    Expose Prometheus metrics.

    This endpoint exposes metrics in the Prometheus format for scraping.
    It doesn't require authentication to allow Prometheus to scrape it.

    Returns:
        Metrics in Prometheus format
    """
    return Response(
        content=metrics.generate_latest_metrics(),
        media_type="text/plain"
    )


@router.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the system and its components.",
    response_description="Health status information",
    responses={
        200: {"description": "Health check successful"},
        500: {"description": "Health check failed", "content": {"text/plain": {}}},
    },
)
async def health_check():
    """
    Health check endpoint.

    This endpoint returns a simple health check response.
    It doesn't require authentication to allow monitoring systems to check it.

    Returns:
        Health check status
    """
    try:
        # Check if the world is running
        is_running = not governor.is_paused() and not governor.is_shutdown()

        # Check if the database is accessible (if applicable)
        # db_status = check_database_connection()

        return {
            "status": "healthy" if is_running else "degraded",
            "version": "0.1.0",
            "timestamp": time.time(),
            "components": {
                "world": "running" if is_running else "paused" if governor.is_paused() else "shutdown",
                # "database": "connected" if db_status else "disconnected",
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response(
            content=f"Health check failed: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )
