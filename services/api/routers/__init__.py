# Import all routers
from .agent import router as agent_router
from .zone import router as zone_router
from .ritual import router as ritual_router
from .command import router as command_router
from .state import router as state_router
from .log import router as log_router
from .law import router as law_router
from .monitoring import router as monitoring_router

# Export all routers
__all__ = [
    "agent_router",
    "zone_router",
    "ritual_router",
    "command_router",
    "state_router",
    "log_router",
    "law_router",
    "monitoring_router",
]