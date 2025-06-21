import logging
from typing import List, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from ..auth import get_current_active_user, Permission, User
from ..deps import world
from ..limiter import limiter  # Import the shared limiter instance

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api",
    tags=["agents"],
)

# Router for agent operations
"""Operations with agents/companions in the Eternia simulation."""


async def auth(token: str = Depends(get_current_active_user)):
    """
    Authenticate requests using JWT-based authentication.
    """
    return token


@router.get(
    "/agents",
    summary="List all agents",
    description="Returns a list of all agents/companions in the system with their details.",
    response_description="List of agents with their details",
    responses={
        200: {"description": "List of agents successfully retrieved"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def list_agents(request: Request, current_user: Union[str, User] = Depends(auth)):
    """
    List all agents in the system.

    Args:
        request: The request object (for rate limiting)
        current_user: The authenticated user or legacy token

    Returns:
        List of agents with their details
    """
    try:
        # Check if world.eterna and companions are properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            return []

        if not hasattr(world.eterna, 'companions') or not world.eterna.companions:
            logger.error("Companions module not initialized")
            return []

        # Access companions through the companions attribute
        if not hasattr(world.eterna.companions, 'companions'):
            logger.error("Companions list not found in companions module")
            return []

        agents = world.eterna.companions.companions
        if agents is None:
            logger.error("Companions list is None")
            return []

        # Helper function to make any object JSON serializable
        def make_serializable(obj, max_depth=3, current_depth=0):
            if current_depth > max_depth:
                return str(obj)

            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item, max_depth, current_depth + 1) for item in obj]
            elif isinstance(obj, dict):
                return {k: make_serializable(v, max_depth, current_depth + 1) for k, v in obj.items() 
                        if not k.startswith("_")}
            else:
                # Complex object
                if hasattr(obj, "to_dict") and callable(obj.to_dict):
                    try:
                        return make_serializable(obj.to_dict(), max_depth, current_depth + 1)
                    except:
                        pass

                if hasattr(obj, "__dict__"):
                    try:
                        return make_serializable({k: v for k, v in obj.__dict__.items() if not k.startswith("_")}, 
                                               max_depth, current_depth + 1)
                    except:
                        pass

                # Last resort: convert to string
                return str(obj)

        result = []
        for agent in agents:
            try:
                agent_data = {}

                # Add each attribute with individual try-except blocks
                try:
                    agent_data["name"] = agent.name
                except Exception as e:
                    logger.error(f"Error getting agent name: {e}")
                    agent_data["name"] = "Unknown"

                try:
                    agent_data["role"] = agent.role
                except Exception as e:
                    logger.error(f"Error getting agent role: {e}")
                    agent_data["role"] = "Unknown"

                try:
                    emotion = getattr(agent, "emotion", None)
                    agent_data["emotion"] = make_serializable(emotion)
                except Exception as e:
                    logger.error(f"Error getting agent emotion: {e}")
                    agent_data["emotion"] = None

                try:
                    zone = getattr(agent, "zone", None)
                    agent_data["zone"] = make_serializable(zone)
                except Exception as e:
                    logger.error(f"Error getting agent zone: {e}")
                    agent_data["zone"] = None

                try:
                    memory = getattr(agent, "memory_seed", None)
                    if memory is None:
                        memory = getattr(agent, "memory", None)
                    agent_data["memory"] = make_serializable(memory)
                except Exception as e:
                    logger.error(f"Error getting agent memory: {e}")
                    agent_data["memory"] = None

                result.append(agent_data)
            except Exception as e:
                logger.error(f"Error processing agent: {e}")
                # Continue to the next agent

        return result
    except Exception as e:
        logger.error(f"Error retrieving agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agents: {str(e)}")


@router.get(
    "/agent/{name}",
    summary="Get agent details",
    description="Returns detailed information about a specific agent/companion.",
    response_description="Detailed information about the specified agent",
    responses={
        200: {"description": "Agent details successfully retrieved"},
        400: {"description": "Invalid agent name"},
        404: {"description": "Agent not found"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("60/minute")
async def get_agent(
    request: Request, 
    name: str, 
    current_user: Union[str, User] = Depends(auth)
):
    """
    Get details of a specific agent.

    Args:
        request: The request object (for rate limiting)
        name: The name of the agent
        current_user: The authenticated user or legacy token

    Returns:
        Details of the specified agent
    """
    try:
        # Validate agent name
        if not name or not isinstance(name, str):
            raise HTTPException(status_code=400, detail="Invalid agent name")

        # Prevent injection attacks
        if any(char in name for char in "\"'\\;:,.<>/{}[]()"):
            logger.warning(f"Possible injection attempt with agent name: {name}")
            raise HTTPException(status_code=400, detail="Invalid agent name")

        # Check if world.eterna is properly initialized
        if not hasattr(world, 'eterna') or not world.eterna:
            logger.error("World or Eterna not initialized")
            raise HTTPException(status_code=500, detail="World not initialized")

        # Check if get_companion method exists
        if not hasattr(world.eterna, 'get_companion'):
            logger.error("get_companion method not found in Eterna")
            raise HTTPException(status_code=500, detail="Method not found")

        agent = world.eterna.get_companion(name)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Expand details as needed
        return {
            "name": agent.name,
            "role": agent.role,
            "emotion": getattr(agent, "emotion", None),
            "zone": getattr(agent, "zone", None),
            "memory": getattr(agent, "memory", None),
            "history": getattr(agent, "history", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent: {str(e)}")
