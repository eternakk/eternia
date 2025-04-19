from pydantic import BaseModel
from typing import Any, Dict

class StateOut(BaseModel):
    cycle:         int
    identity_score: float
    emotion:       str | None
    modifiers:     Dict[str, list[str]]

class CommandOut(BaseModel):
    status: str
    detail: str | None = None