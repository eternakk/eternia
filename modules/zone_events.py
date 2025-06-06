"""
Zone-specific events for the Eternia system.

This module defines events that are specific to zone changes and modifications.
These events are published when zones are changed and can be subscribed to by other components.
"""

import time
from typing import Any, Dict, Optional

from modules.utilities.event_bus import Event


class ZoneEvent(Event):
    """Base class for all zone events."""

    def __init__(self, timestamp: float = None):
        """
        Initialize the zone event.

        Args:
            timestamp: The time when the event occurred. Defaults to current time.
        """
        self.timestamp = timestamp if timestamp is not None else time.time()


class ZoneChangedEvent(ZoneEvent):
    """Event fired when a zone is changed or marked as active."""

    def __init__(self, zone_name: str, is_new: bool = False, timestamp: float = None):
        """
        Initialize the zone changed event.

        Args:
            zone_name: The name of the zone that was changed.
            is_new: Whether this zone is newly added to explored zones.
            timestamp: The time when the event occurred.
        """
        super().__init__(timestamp)
        self.zone_name = zone_name
        self.is_new = is_new


class ZoneExploredEvent(ZoneEvent):
    """Event fired when a zone is marked as explored."""

    def __init__(self, zone_name: str, timestamp: float = None):
        """
        Initialize the zone explored event.

        Args:
            zone_name: The name of the zone that was explored.
            timestamp: The time when the event occurred.
        """
        super().__init__(timestamp)
        self.zone_name = zone_name


class ZoneModifierAddedEvent(ZoneEvent):
    """Event fired when a modifier is added to a zone."""

    def __init__(self, zone_name: str, modifier: Any, timestamp: float = None):
        """
        Initialize the zone modifier added event.

        Args:
            zone_name: The name of the zone the modifier was added to.
            modifier: The modifier that was added.
            timestamp: The time when the event occurred.
        """
        super().__init__(timestamp)
        self.zone_name = zone_name
        self.modifier = modifier