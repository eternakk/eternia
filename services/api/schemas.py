from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class StateOut(BaseModel):
    cycle: int = Field(ge=0, description="Current cycle number of the simulation")
    identity_score: float = Field(
        ge=0.0, le=1.0, description="Identity continuity score between 0 and 1"
    )
    emotion: Optional[str] = Field(default=None, description="Current emotion state")
    modifiers: Dict[str, List[str]] = Field(
        default_factory=dict, description="Active modifiers by category"
    )
    current_zone: Optional[str] = Field(default=None, description="Current active zone")

    @field_validator("emotion")
    def validate_emotion(cls, v):
        """Validate that the emotion is a recognized emotion if not None."""
        if v is not None:
            valid_emotions = [
                "joy",
                "sadness",
                "anger",
                "fear",
                "surprise",
                "disgust",
                "trust",
                "anticipation",
                "serenity",
                "acceptance",
                "apprehension",
                "distraction",
                "pensiveness",
                "boredom",
                "annoyance",
                "interest",
                "neutral",
                "calm",
                "excited",
                "curious",
            ]
            if v.lower() not in [e.lower() for e in valid_emotions]:
                raise ValueError(f"'{v}' is not a recognized emotion")
        return v

    @field_validator("modifiers")
    def validate_modifiers(cls, v):
        """Validate that the modifiers dictionary has valid categories and values."""
        valid_categories = [
            "environmental",
            "emotional",
            "cognitive",
            "social",
            "physical",
            "temporal",
        ]

        for category, modifiers in v.items():
            if category not in valid_categories:
                raise ValueError(f"'{category}' is not a valid modifier category")

            if not isinstance(modifiers, list):
                raise ValueError(f"Modifiers for category '{category}' must be a list")

            for modifier in modifiers:
                if not isinstance(modifier, str) or not modifier:
                    raise ValueError(
                        f"Modifier '{modifier}' in category '{category}' must be a non-empty string"
                    )

        return v


class CommandOut(BaseModel):
    status: str = Field(..., description="Status of the command execution")
    detail: Optional[str] = Field(
        default=None, description="Additional details about the command execution"
    )

    @field_validator("status")
    def validate_status(cls, v):
        """Validate that the status is one of the recognized statuses."""
        valid_statuses = [
            "success",
            "error",
            "paused",
            "running",
            "shutdown",
            "rolled_back",
        ]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


Hey


class ModelGenerationRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language description of the asset to generate.",
    )
    style: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Optional aesthetic/style hint to pass through to the generator.",
    )
    category: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Optional asset category (e.g., props, structures) to guide template selection.",
    )


class ModelGenerationResponse(BaseModel):
    status: str = Field(
        ...,
        description="Current status of the generation request (e.g., pending, unavailable).",
    )
    message: Optional[str] = Field(
        default=None, description="Human-readable note describing the status."
    )
    model_id: Optional[str] = Field(
        default=None, description="Identifier for the generated model when available."
    )
    model_url: Optional[str] = Field(
        default=None,
        description="URL where the generated model can be retrieved once ready.",
    )

    @field_validator("status")
    def validate_status(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Status must be a non-empty string.")
        return value
