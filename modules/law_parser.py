import pathlib, re
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pydantic import BaseModel, Field, validator

class LawEffect(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)

class Law(BaseModel):
    name: str
    version: int = 1
    enabled: bool = True
    description: str = ""
    on_event: list[str]
    conditions: list[str] = []
    effects: dict[str, LawEffect] = Field(default_factory=dict)

    @validator("name")
    def slug_safe(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9 _-]+", v):
            raise ValueError("name must be slug‑safe")
        return v

def load_laws(path="laws") -> dict[str, Law]:
    laws = {}
    for file_path in pathlib.Path(path).glob("*.law.toml"):
        with open(file_path, "rb") as fp:  # Open in binary mode
            data = tomllib.load(fp)
            meta     = data.get("meta", {})
            trigger  = data.get("trigger", {})
            effects  = data.get("effects", {})
            law = Law(
                name        = meta["name"],
                version     = meta.get("version", 1),
                enabled     = meta.get("enabled", True),
                description = meta.get("description", ""),
                on_event    = trigger["on_event"],
                conditions  = trigger.get("conditions", []),
                effects     = {k: LawEffect(type=k, params=v) for k, v in effects.items()},
            )
            laws[law.name] = law
    return laws
