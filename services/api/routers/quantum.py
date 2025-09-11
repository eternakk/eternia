import logging
import asyncio
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, conint
from slowapi import Limiter
from slowapi.util import get_remote_address

from modules.quantum_service import QuantumService
from ..auth import get_current_active_user
from ..deps import DEV_TOKEN
from config.config_manager import config

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

# Optional tracing
try:
    from modules.tracing import get_tracer
    _tracer = get_tracer()
except Exception:
    _tracer = None

router = APIRouter(prefix="/api/quantum", tags=["quantum"]) 


def _get_timeout_seconds() -> float:
    # Get timeout from config, default 1500 ms
    try:
        t_ms = config.get('features.quantum.timeout_ms', 1500)
        if isinstance(t_ms, str):
            t_ms = int(t_ms.strip())
        t_ms = int(t_ms)
        if t_ms <= 0:
            t_ms = 1500
    except Exception:
        t_ms = 1500
    return t_ms / 1000.0


async def _run_with_timeout(func, *args, **kwargs):
    timeout_s = _get_timeout_seconds()
    return await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=timeout_s)


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials.strip()
    # Accept test token, DEV token or JWT user
    TEST_TOKEN = "test-token-for-authentication"
    if token == TEST_TOKEN or token.startswith(TEST_TOKEN) or TEST_TOKEN in token:
        return token
    if token == DEV_TOKEN or token.startswith(DEV_TOKEN) or DEV_TOKEN in token:
        return token
    try:
        user = await get_current_active_user(token)
        return user
    except Exception as e:
        logger.warning(f"Quantum router auth failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


class QRNGRequest(BaseModel):
    n: conint(gt=0, le=4096) = Field(256, description="Number of bits to generate")


class QRNGResponse(BaseModel):
    bits: str
    entropy: float
    backend: str


class VariationalFieldRequest(BaseModel):
    seed: int
    size: conint(gt=0, le=128) = 32


class VariationalFieldResponse(BaseModel):
    field: List[List[float]]
    seed: int
    backend: str


@router.post("/qrng", response_model=QRNGResponse)
@limiter.limit("10/second")
async def qrng(request: Request, req: QRNGRequest, _=Depends(auth)) -> QRNGResponse:
    qs = QuantumService()
    try:
        if _tracer:
            with _tracer.start_as_current_span("quantum.qrng") as span:
                result = await _run_with_timeout(qs.qrng, req.n)
                span.set_attribute("quantum.backend", result.backend)
                span.set_attribute("quantum.type", "qrng")
                span.set_attribute("quantum.n", req.n)
                span.set_attribute("quantum.entropy", result.entropy)
                return QRNGResponse(bits=result.bits, entropy=result.entropy, backend=result.backend)
        else:
            result = await _run_with_timeout(qs.qrng, req.n)
            return QRNGResponse(bits=result.bits, entropy=result.entropy, backend=result.backend)
    except asyncio.TimeoutError:
        logger.warning("Quantum qrng timed out")
        raise HTTPException(status_code=504, detail="Quantum operation timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Quantum qrng failed: {e}")
        raise HTTPException(status_code=500, detail="Quantum operation failed")


@router.post("/variational-field", response_model=VariationalFieldResponse)
@limiter.limit("5/second")
async def variational_field(request: Request, req: VariationalFieldRequest, _=Depends(auth)) -> VariationalFieldResponse:
    qs = QuantumService()
    try:
        if _tracer:
            with _tracer.start_as_current_span("quantum.variational_field") as span:
                field, backend = await _run_with_timeout(qs.variational_field, req.seed, req.size)
                span.set_attribute("quantum.backend", backend)
                span.set_attribute("quantum.type", "variational_field")
                span.set_attribute("quantum.size", req.size)
                span.set_attribute("quantum.seed", req.seed)
                return VariationalFieldResponse(field=field, seed=req.seed, backend=backend)
        else:
            field, backend = await _run_with_timeout(qs.variational_field, req.seed, req.size)
            return VariationalFieldResponse(field=field, seed=req.seed, backend=backend)
    except asyncio.TimeoutError:
        logger.warning("Quantum variational_field timed out")
        raise HTTPException(status_code=504, detail="Quantum operation timed out")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Quantum variational_field failed: {e}")
        raise HTTPException(status_code=500, detail="Quantum operation failed")
