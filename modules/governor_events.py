"""
Governor-specific events for the Eternia system.

This module defines events that are specific to the AlignmentGovernor component.
These events are published by the governor and can be subscribed to by other components.
"""

from pathlib import Path
from typing import Any, Dict

from modules.utilities.event_bus import Event


class GovernorEvent(Event):
    """Base class for all governor events."""

    def __init__(self, timestamp: float):
        """
        Initialize the governor event.

        Args:
            timestamp: The time when the event occurred.
        """
        self.timestamp = timestamp


class PauseEvent(GovernorEvent):
    """Event fired when the simulation is paused."""

    pass


class ResumeEvent(GovernorEvent):
    """Event fired when the simulation is resumed."""

    pass


class ShutdownEvent(GovernorEvent):
    """Event fired when the simulation is shut down."""

    def __init__(self, timestamp: float, reason: str):
        """
        Initialize the shutdown event.

        Args:
            timestamp: The time when the event occurred.
            reason: The reason for shutting down the simulation.
        """
        super().__init__(timestamp)
        self.reason = reason


class RollbackEvent(GovernorEvent):
    """Event fired when the simulation is rolled back to a previous checkpoint."""

    def __init__(self, timestamp: float, checkpoint: Path):
        """
        Initialize the rollback event.

        Args:
            timestamp: The time when the event occurred.
            checkpoint: The checkpoint that was rolled back to.
        """
        super().__init__(timestamp)
        self.checkpoint = checkpoint


class ContinuityBreachEvent(GovernorEvent):
    """Event fired when the identity continuity is below the threshold."""

    def __init__(self, timestamp: float, metrics: Dict[str, Any]):
        """
        Initialize the continuity breach event.

        Args:
            timestamp: The time when the event occurred.
            metrics: The metrics that triggered the breach.
        """
        super().__init__(timestamp)
        self.metrics = metrics


class CheckpointScheduledEvent(GovernorEvent):
    """Event fired when a checkpoint is scheduled."""

    pass


class CheckpointSavedEvent(GovernorEvent):
    """Event fired when a checkpoint is saved."""

    def __init__(self, timestamp: float, path: Path):
        """
        Initialize the checkpoint saved event.

        Args:
            timestamp: The time when the event occurred.
            path: The path where the checkpoint was saved.
        """
        super().__init__(timestamp)
        self.path = path


class PolicyViolationEvent(GovernorEvent):
    """Event fired when a policy is violated."""

    def __init__(self, timestamp: float, policy_name: str, metrics: Dict[str, Any]):
        """
        Initialize the policy violation event.

        Args:
            timestamp: The time when the event occurred.
            policy_name: The name of the policy that was violated.
            metrics: The metrics that triggered the violation.
        """
        super().__init__(timestamp)
        self.policy_name = policy_name
        self.metrics = metrics


class LawEnforcedEvent(GovernorEvent):
    """Event fired when a law is enforced."""

    def __init__(
            self, timestamp: float, law_name: str, event_name: str, payload: Dict[str, Any]
    ):
        """
        Initialize the law enforced event.

        Args:
            timestamp: The time when the event occurred.
            law_name: The name of the law that was enforced.
            event_name: The name of the event that triggered the law.
            payload: The payload of the event that triggered the law.
        """
        super().__init__(timestamp)
        self.law_name = law_name
        self.event_name = event_name
        self.payload = payload
