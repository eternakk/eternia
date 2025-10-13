import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.config_manager import config
from ..auth import User, get_current_active_user
from ..deps import DEV_TOKEN
from ..limiter import limiter
from ..schemas import ModelGenerationRequest, ModelGenerationResponse

logger = logging.getLogger(__name__)

security = HTTPBearer()
router = APIRouter(
    prefix="/api",
    tags=["generation"],
)

TEST_TOKEN = "test-token-for-authentication"


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Union[str, User]:
    """
    Minimal bearer-token authentication aligned with other routers.

    Accepts the shared DEV token, the test token, or falls back to JWT validation.
    """
    token = (credentials.credentials or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token == TEST_TOKEN or token.startswith(TEST_TOKEN):
        return token

    if token == DEV_TOKEN or token.startswith(DEV_TOKEN):
        return token

    try:
        return await get_current_active_user(token)
    except Exception:
        logger.warning("Generation router authentication failed for token prefix %s", token[:4])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/generate_model",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ModelGenerationResponse,
    summary="Generate a 3D model from a natural-language prompt (stub)",
    responses={
        202: {"description": "Request accepted; integration pending implementation."},
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
    },
)
@limiter.limit("15/minute")
async def generate_model(
    request: Request,
    payload: ModelGenerationRequest,
    current_user: Union[str, User] = Depends(auth),
) -> ModelGenerationResponse:
    """
    EP1-S1 stub endpoint.

    Establishes the POST `/api/generate_model` surface so downstream work can plug in the
    Sloyd integration once credentials and pipelines are ready.
    """
    prompt_preview = payload.prompt.strip().replace("\n", " ")[:120]
    logger.info(
        "EP1-S1 stub invoked (prompt='%s', style='%s', category='%s')",
        prompt_preview,
        payload.style or "",
        payload.category or "",
    )

    api_key = (config.get("integrations.sloyd.api_key", default="") or "").strip()
    if not api_key:
        message = (
            "Sloyd integration is not yet configured. "
            "Set `integrations.sloyd.api_key` to enable downstream development."
        )
        return ModelGenerationResponse(status="unavailable", message=message)

    message = (
        "Sloyd credentials detected, but the generation pipeline is not implemented yet. "
        "Track progress via Story EP1-S1."
    )
    return ModelGenerationResponse(status="pending", message=message)
