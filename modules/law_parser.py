import pathlib, re
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pydantic import BaseModel, Field, field_validator

class LawEffect(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)

    @field_validator("type")
    def validate_type(cls, v):
        """Validate that the effect type is a known type."""
        valid_types = ["modify_zone", "apply_modifier", "remove_modifier", "trigger_event", 
                      "change_emotion", "add_memory", "adjust_score", "spawn_entity", "grant_energy"]
        if v not in valid_types:
            raise ValueError(f"Effect type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("params")
    def validate_params(cls, v, info):
        """Validate that the parameters are appropriate for the effect type."""
        effect_type = info.data.get("type")

        # Skip validation if type is not set yet
        if not effect_type:
            return v

        # Validate params based on effect type
        if effect_type == "modify_zone" and "zone_name" not in v:
            raise ValueError("modify_zone effect requires 'zone_name' parameter")
        elif effect_type == "apply_modifier" and "modifier_name" not in v:
            raise ValueError("apply_modifier effect requires 'modifier_name' parameter")
        elif effect_type == "remove_modifier" and "modifier_name" not in v:
            raise ValueError("remove_modifier effect requires 'modifier_name' parameter")
        elif effect_type == "trigger_event" and "event_name" not in v:
            raise ValueError("trigger_event effect requires 'event_name' parameter")
        elif effect_type == "change_emotion" and "emotion" not in v:
            raise ValueError("change_emotion effect requires 'emotion' parameter")
        elif effect_type == "add_memory" and "content" not in v:
            raise ValueError("add_memory effect requires 'content' parameter")
        elif effect_type == "adjust_score" and "value" not in v:
            raise ValueError("adjust_score effect requires 'value' parameter")
        elif effect_type == "spawn_entity" and "entity_type" not in v:
            raise ValueError("spawn_entity effect requires 'entity_type' parameter")
        elif effect_type == "grant_energy" and "amount" not in v:
            raise ValueError("grant_energy effect requires 'amount' parameter")

        return v

class Law(BaseModel):
    name: str
    version: int = 1
    enabled: bool = True
    description: str = ""
    on_event: list[str]
    conditions: list[str] = []
    effects: dict[str, LawEffect] = Field(default_factory=dict)

    @field_validator("name")
    def slug_safe(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9 _-]+", v):
            raise ValueError("name must be slug‑safe")
        return v

    @field_validator("version")
    def validate_version(cls, v):
        """Validate that the version is a positive integer."""
        if v <= 0:
            raise ValueError("version must be a positive integer")
        return v

    @field_validator("on_event")
    def validate_on_event(cls, v):
        """Validate that the on_event list is not empty and contains valid event names."""
        if not v:
            raise ValueError("on_event list cannot be empty")

        # Check for valid event names (basic format validation)
        for event in v:
            if not isinstance(event, str) or not event:
                raise ValueError("Event names must be non-empty strings")
            if not re.fullmatch(r"[A-Za-z0-9_]+", event):
                raise ValueError(f"Event name '{event}' contains invalid characters")

        return v

    @field_validator("conditions")
    def validate_conditions(cls, v):
        """Validate that the conditions are valid condition expressions."""
        for condition in v:
            if not isinstance(condition, str):
                raise ValueError("Conditions must be strings")
            # Basic syntax validation for conditions
            if condition and not re.search(r"[A-Za-z0-9_]+\s*[=<>!]+", condition):
                raise ValueError(f"Condition '{condition}' does not appear to be a valid expression")

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
