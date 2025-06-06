"""
Adapter for bridging the legacy event queue mechanism with the new event bus.

This module provides an adapter that subscribes to events from the event bus
and forwards them to the legacy event queue. This allows components that are
still using the legacy mechanism to receive events from the event bus.
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional

from modules.utilities.event_bus import event_bus, Event, EventListener, event_handler, EventPriority
from modules.governor_events import GovernorEvent
from modules.zone_events import ZoneEvent


class LegacyEventAdapter(EventListener):
    """
    Adapter that forwards events from the event bus to the legacy event queue.

    This adapter subscribes to all GovernorEvent and ZoneEvent events and forwards them to
    the legacy event queue in the format expected by the legacy components.
    """

    def __init__(self, event_queue: asyncio.Queue):
        """
        Initialize the adapter with the legacy event queue.

        Args:
            event_queue: The legacy event queue to forward events to.
        """
        self.event_queue = event_queue
        super().__init__()  # Register event handlers

    @event_handler(GovernorEvent, priority=EventPriority.MONITOR)
    def handle_governor_event(self, event: GovernorEvent) -> None:
        """
        Handle a governor event by forwarding it to the legacy event queue.

        Args:
            event: The governor event to forward.
        """
        # Convert the event to the legacy format
        legacy_event = self._convert_to_legacy_format(event)

        # Forward the event to the legacy queue
        try:
            self.event_queue.put_nowait(legacy_event)
        except asyncio.QueueFull:
            # Drop the event if the queue is full (same behavior as in governor._broadcast)
            pass

    @event_handler(ZoneEvent, priority=EventPriority.MONITOR)
    def handle_zone_event(self, event: ZoneEvent) -> None:
        """
        Handle a zone event by forwarding it to the legacy event queue.

        Args:
            event: The zone event to forward.
        """
        # Convert the event to the legacy format
        legacy_event = self._convert_to_legacy_format(event)

        # Forward the event to the legacy queue
        try:
            self.event_queue.put_nowait(legacy_event)
        except asyncio.QueueFull:
            # Drop the event if the queue is full
            pass

    def _convert_to_legacy_format(self, event: Event) -> Dict[str, Any]:
        """
        Convert an Event to the legacy format.

        The legacy format is a dictionary with 't', 'event', and 'payload' keys.

        Args:
            event: The event to convert.

        Returns:
            Dict[str, Any]: The event in legacy format.
        """
        # Common fields for all events
        legacy_event = {
            "t": getattr(event, "timestamp", time.time()),
        }

        # Event-specific fields
        event_type = type(event).__name__

        match event_type:
            # Governor events
            case "PauseEvent":
                legacy_event["event"] = "pause"
                legacy_event["payload"] = None
            case "ResumeEvent":
                legacy_event["event"] = "resume"
                legacy_event["payload"] = None
            case "ShutdownEvent":
                legacy_event["event"] = "shutdown"
                legacy_event["payload"] = event.reason
            case "RollbackEvent":
                legacy_event["event"] = "rollback_complete"
                legacy_event["payload"] = str(event.checkpoint)
            case "ContinuityBreachEvent":
                legacy_event["event"] = "continuity_breach"
                legacy_event["payload"] = event.metrics
            case "CheckpointScheduledEvent":
                legacy_event["event"] = "checkpoint_scheduled"
                legacy_event["payload"] = None
            case "CheckpointSavedEvent":
                legacy_event["event"] = "checkpoint_saved"
                legacy_event["payload"] = str(event.path)
            case "PolicyViolationEvent":
                legacy_event["event"] = "policy_violation"
                legacy_event["payload"] = {
                    "policy_name": event.policy_name,
                    "metrics": event.metrics
                }
            case "LawEnforcedEvent":
                legacy_event["event"] = "law_enforced"
                legacy_event["payload"] = {
                    "law_name": event.law_name,
                    "event_name": event.event_name,
                    "payload": event.payload
                }
            # Zone events
            case "ZoneChangedEvent":
                legacy_event["event"] = "zone_changed"
                legacy_event["payload"] = {
                    "zone_name": event.zone_name,
                    "is_new": event.is_new
                }
            case "ZoneExploredEvent":
                legacy_event["event"] = "zone_explored"
                legacy_event["payload"] = {
                    "zone_name": event.zone_name
                }
            case "ZoneModifierAddedEvent":
                legacy_event["event"] = "zone_modifier_added"
                legacy_event["payload"] = {
                    "zone_name": event.zone_name,
                    "modifier": event.modifier
                }
            case _:
                # For any other events, use the class name as the event name
                legacy_event["event"] = event_type.lower().replace("event", "")
                legacy_event["payload"] = vars(event)

        return legacy_event


def setup_legacy_adapter(event_queue: asyncio.Queue) -> LegacyEventAdapter:
    """
    Set up the legacy event adapter.

    This function creates a LegacyEventAdapter that forwards events from the
    event bus to the legacy event queue.

    Args:
        event_queue: The legacy event queue to forward events to.

    Returns:
        LegacyEventAdapter: The adapter instance.
    """
    return LegacyEventAdapter(event_queue)
