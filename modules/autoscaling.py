"""
Simple autoscaling decision module for Eternia.

This module provides a lightweight AutoScaler that makes scale up/down decisions
based on a single load factor (0.0–1.0). It emits events on the EventBus so that
other parts of the system (or deployment adapters) can react appropriately.

It is intentionally implementation-agnostic (doesn't talk to k8s or Docker directly)
so it can be used in unit tests and wired to real infra by listeners elsewhere.
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Optional

from modules.utilities.event_bus import event_bus, Event, SystemEvent

logger = logging.getLogger(__name__)


@dataclass
class ScaleDecisionEvent(Event):
    load: float
    current_replicas: int
    desired_replicas: int
    reason: str = ""
    timestamp: float = time.time()


class ScaleUpEvent(ScaleDecisionEvent):
    pass


class ScaleDownEvent(ScaleDecisionEvent):
    pass


class AutoScaler:
    """
    Threshold-based autoscaler.

    - If load >= scale_up_threshold -> scale up by 1 (respecting max_replicas)
    - If load <= scale_down_threshold -> scale down by 1 (respecting min_replicas)
    - Otherwise, keep current replicas.

    Cooldown prevents consecutive scale actions from happening too frequently.
    """

    def __init__(
        self,
        *,
        min_replicas: int = 1,
        max_replicas: int = 10,
        scale_up_threshold: float = 0.75,
        scale_down_threshold: float = 0.25,
        cooldown_seconds: float = 30.0,
        initial_replicas: Optional[int] = None,
    ) -> None:
        if min_replicas < 1:
            raise ValueError("min_replicas must be >= 1")
        if max_replicas < min_replicas:
            raise ValueError("max_replicas must be >= min_replicas")
        if not (0.0 <= scale_down_threshold <= 1.0):
            raise ValueError("scale_down_threshold must be within [0,1]")
        if not (0.0 <= scale_up_threshold <= 1.0):
            raise ValueError("scale_up_threshold must be within [0,1]")
        if scale_down_threshold > scale_up_threshold:
            raise ValueError("scale_down_threshold cannot exceed scale_up_threshold")

        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_seconds = cooldown_seconds

        self.current_replicas = (
            initial_replicas if initial_replicas is not None else min_replicas
        )
        self.last_scale_ts: float = 0.0

    def _in_cooldown(self) -> bool:
        return (time.time() - self.last_scale_ts) < self.cooldown_seconds

    def evaluate(self, load: float) -> Optional[str]:
        """
        Evaluate the current load and emit a scale decision if needed.

        Returns: "up", "down", or None if no action taken.
        """
        load = max(0.0, min(1.0, float(load)))  # clamp

        if self._in_cooldown():
            logger.debug("Autoscaler cooldown active, skipping decision")
            return None

        # Decide scale up/down
        if load >= self.scale_up_threshold and self.current_replicas < self.max_replicas:
            desired = min(self.current_replicas + 1, self.max_replicas)
            self._emit_up(load, desired, reason="threshold_crossed")
            return "up"

        if load <= self.scale_down_threshold and self.current_replicas > self.min_replicas:
            desired = max(self.current_replicas - 1, self.min_replicas)
            self._emit_down(load, desired, reason="threshold_crossed")
            return "down"

        logger.debug("Autoscaler: no change required (load=%.2f, replicas=%d)", load, self.current_replicas)
        return None

    # --- internals ---
    def _emit_up(self, load: float, desired: int, *, reason: str) -> None:
        evt = ScaleUpEvent(load=load, current_replicas=self.current_replicas, desired_replicas=desired, reason=reason)
        self.current_replicas = desired
        self.last_scale_ts = time.time()
        logger.info("Autoscaling UP: %s", evt)
        event_bus.publish(evt)

    def _emit_down(self, load: float, desired: int, *, reason: str) -> None:
        evt = ScaleDownEvent(load=load, current_replicas=self.current_replicas, desired_replicas=desired, reason=reason)
        self.current_replicas = desired
        self.last_scale_ts = time.time()
        logger.info("Autoscaling DOWN: %s", evt)
        event_bus.publish(evt)
