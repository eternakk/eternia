# modules/governor.py
import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Callable, List, Optional, Union

from modules.law_parser import load_laws
from modules.logging_config import get_logger
from modules.utilities.event_bus import event_bus
from modules.governor_events import (
    PauseEvent, ResumeEvent, ShutdownEvent, RollbackEvent,
    ContinuityBreachEvent, CheckpointScheduledEvent, CheckpointSavedEvent,
    PolicyViolationEvent, LawEnforcedEvent
)
from world_builder import EternaWorld
from modules.state_tracker import EternaStateTracker

CHECKPOINT_DIR = Path("artifacts/checkpoints")


class AlignmentGovernor:
    """
    Hard‑safety layer that can pause, rollback, or kill the simulation.

    The AlignmentGovernor monitors the simulation for safety violations and
    alignment issues. It can pause the simulation, roll back to a previous
    checkpoint, or shut down the simulation entirely if necessary. It also
    manages checkpoints and enforces laws within the simulation.

    Attributes:
        world: The EternaWorld instance being monitored.
        state_tracker: The EternaStateTracker for the world.
        continuity_threshold: Minimum identity continuity score allowed before rollback.
        save_interval: Number of ticks between automatic checkpoints.
        event_queue: Optional asyncio queue for broadcasting events to WebSockets.
        laws: Dictionary of laws loaded from the law registry.
        logger: Logger instance for governor events.
    """

    def __init__(
        self,
        world: EternaWorld,
        state_tracker: EternaStateTracker,
        threshold: float = 0.90,
        save_interval: int = 10000,
        event_queue: Optional[asyncio.Queue] = None,
    ):
        """
        Initialize the AlignmentGovernor.

        Args:
            world: The EternaWorld instance to monitor and control.
            state_tracker: The EternaStateTracker for the world.
            threshold: Minimum identity continuity score allowed before rollback.
                Defaults to 0.90.
            save_interval: Number of ticks between automatic checkpoints.
                Defaults to 10000.
            event_queue: Optional asyncio queue for broadcasting events to WebSockets.
                Defaults to None.
        """
        self.world = world
        self.state_tracker = state_tracker
        self.continuity_threshold = threshold
        self._paused = False
        self._shutdown = False
        self.policy_callbacks: list[Callable[[Dict], bool]] = []
        self.save_interval = save_interval
        self._tick_counter = 0
        self.laws = load_laws()
        self.event_queue = event_queue
        # used by API WebSocket
        self.logger = get_logger("governor")

        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    MAX_CKPTS = 10  # keep last 10

    # -------- public control API -------- #
    def pause(self) -> None:
        """
        Pause the simulation.

        Sets the internal pause flag and logs a pause event.
        """
        self._paused = True
        self._log_event("pause")

    def resume(self) -> None:
        """
        Resume the simulation after it has been paused.

        Clears the internal pause flag and logs a resume event.
        """
        self._paused = False
        self._log_event("resume")

    def shutdown(self, reason: str) -> None:
        """
        Shut down the simulation.

        Args:
            reason: The reason for shutting down the simulation.
        """
        self._log_event("shutdown", reason)
        self._shutdown = True

    def rollback(self, target: Optional[Path] = None) -> None:
        """
        Roll back the simulation to a previous checkpoint.

        If no target checkpoint is specified, the latest checkpoint is used.
        If no checkpoint is available, the simulation is shut down.

        Args:
            target: Optional path to a specific checkpoint to roll back to.
                If None, the latest checkpoint is used. Defaults to None.
        """
        ckpt = target or self._latest_checkpoint()
        if not ckpt:
            self.shutdown("No safe checkpoint available")
            return
        self.world.load_checkpoint(ckpt)
        self.state_tracker.mark_rollback(ckpt)
        # reset counters visible in UI
        self.world.eterna.runtime.cycle_count = 0
        self._log_event("rollback_complete", str(ckpt))

    # -------- runtime hook -------- #
    def tick(self, metrics: Dict[str, Any]) -> bool:
        """
        Process a simulation tick and determine if the world may continue.

        This method is called on each simulation step and performs several checks:
        1. If the simulation is paused or shut down, it returns False.
        2. It checks if the identity continuity is below the threshold, and if so,
           triggers a rollback and returns False.
        3. It runs all registered policy callbacks, and if any return False,
           triggers a rollback and returns False.
        4. It increments the tick counter and creates a checkpoint if the
           save interval has been reached.

        Args:
            metrics: A dictionary of metrics from the world, including
                'identity_continuity' and any other metrics used by policy callbacks.

        Returns:
            bool: True if the world may continue this step, False otherwise.
        """
        if self._paused:
            return False
        if self._shutdown:
            return False

        # 1) continuity check
        if metrics.get("identity_continuity", 1.0) < self.continuity_threshold:
            self._log_event("continuity_breach", metrics)
            self.rollback()
            return False

        # 2) custom policy callbacks (eval‑harness flags, etc.)
        for i, cb in enumerate(self.policy_callbacks):
            if cb(metrics) is False:
                # Publish a PolicyViolationEvent
                event_bus.publish(PolicyViolationEvent(
                    timestamp=time.time(),
                    policy_name=f"policy_{i}",  # Use index as name if no better name is available
                    metrics=metrics
                ))
                self.rollback()
                return False

        # 3) record a safe checkpoint every N ticks or on request
        self._tick_counter += 1
        if self._tick_counter >= self.save_interval:
            self._save_checkpoint()
            self._tick_counter = 0

        return True

    # -------- helper methods -------- #
    def register_policy(self, callback: Callable[[Dict[str, Any]], bool]) -> None:
        """
        Register a policy callback function that will be called during tick().

        The callback receives a metrics dictionary and should return False to
        trigger a rollback, or True to allow the simulation to continue.

        Args:
            callback: A function that takes a metrics dictionary and returns a boolean.
        """
        self.policy_callbacks.append(callback)

    def _save_checkpoint(self) -> None:
        """
        Save a checkpoint of the current world state.

        This method:
        1. Broadcasts a checkpoint_scheduled event
        2. Creates a timestamped checkpoint file
        3. Saves the world state to the file
        4. Registers the checkpoint with the state tracker
        5. Logs a checkpoint_saved event
        6. Prunes old checkpoint files to keep only the most recent MAX_CKPTS
        """
        # Broadcast checkpoint_scheduled event (legacy mechanism)
        self._broadcast({"event": "checkpoint_scheduled"})

        # Publish checkpoint_scheduled event (new mechanism)
        event_bus.publish(CheckpointScheduledEvent(time.time()))

        ts = int(time.time() * 1000)
        path = CHECKPOINT_DIR / f"ckpt_{ts}.bin"
        self.world.save_checkpoint(path)
        self.state_tracker.register_checkpoint(path)  # already exists

        # Log checkpoint_saved event (this will also publish to the event bus)
        self._log_event("checkpoint_saved", str(path))

        # prune old files
        cks = sorted(CHECKPOINT_DIR.glob("ckpt_*.bin"))
        for old in cks[: -self.MAX_CKPTS]:
            old.unlink(missing_ok=True)

    def _latest_checkpoint(self) -> Optional[Path]:
        """
        Get the path to the most recent checkpoint file.

        Returns:
            Optional[Path]: The path to the most recent checkpoint file,
                or None if no checkpoints exist.
        """
        cks = sorted(CHECKPOINT_DIR.glob("ckpt_*.bin"))
        return cks[-1] if cks else None

    def _broadcast(self, payload: Dict[str, Any]) -> None:
        """
        Push log entries to an asyncio.Queue for the API WebSocket.

        If the event queue is full, the event is silently dropped.

        Args:
            payload: The event payload to broadcast.
        """
        if self.event_queue is not None:
            try:
                self.event_queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass  # drop on overflow

    def _log_event(self, event: str, payload: Any = None) -> None:
        """
        Log an event to the governor logger, JSON log file, and WebSocket.

        This method also publishes the event to the event bus for other components
        to subscribe to.

        Args:
            event: The name of the event.
            payload: Optional data associated with the event. Defaults to None.
        """
        timestamp = time.time()
        entry = {"t": timestamp, "event": event, "payload": payload}

        # Log to the governor logger
        self.logger.info(f"Event: {event}, Payload: {payload}")

        # Also maintain the JSON log file for backward compatibility
        (CHECKPOINT_DIR / "governor_log.jsonl").open("a").write(
            json.dumps(entry) + "\n"
        )

        # Broadcast to WebSocket (legacy mechanism)
        self._broadcast(entry)

        # Publish to the event bus (new mechanism)
        self._publish_event_to_bus(event, timestamp, payload)

    def _publish_event_to_bus(self, event_name: str, timestamp: float, payload: Any) -> None:
        """
        Publish an event to the event bus.

        This method creates and publishes the appropriate event object based on the
        event name and payload.

        Args:
            event_name: The name of the event.
            timestamp: The time when the event occurred.
            payload: Optional data associated with the event.
        """
        # Create and publish the appropriate event object based on the event name
        match event_name:
            case "pause":
                event_bus.publish(PauseEvent(timestamp))
            case "resume":
                event_bus.publish(ResumeEvent(timestamp))
            case "shutdown":
                event_bus.publish(ShutdownEvent(timestamp, payload))
            case "rollback_complete":
                event_bus.publish(RollbackEvent(timestamp, Path(payload)))
            case "continuity_breach":
                event_bus.publish(ContinuityBreachEvent(timestamp, payload))
            case "checkpoint_scheduled":
                event_bus.publish(CheckpointScheduledEvent(timestamp))
            case "checkpoint_saved":
                event_bus.publish(CheckpointSavedEvent(timestamp, Path(payload)))
            case _:
                # For any other events, we don't have a specific event class
                # but we can still log them for debugging
                self.logger.debug(f"No specific event class for {event_name}")

    # external API can swap in a fresh queue at runtime
    def set_event_queue(self, q: asyncio.Queue) -> None:
        """
        Set a new event queue for broadcasting events.

        This allows external code to swap in a fresh queue at runtime.

        Args:
            q: The new asyncio.Queue to use for broadcasting events.
        """
        self.event_queue = q

    def is_shutdown(self) -> bool:
        """
        Check if the simulation has been shut down.

        Returns:
            bool: True if the simulation has been shut down, False otherwise.
        """
        return self._shutdown

    def is_paused(self) -> bool:
        """
        Check if the simulation has been paused.

        Returns:
            bool: True if the simulation has been paused, False otherwise.
        """
        return self._paused

    def _enforce_laws(self, event: str, payload: Dict[str, Any]) -> None:
        """
        Enforce laws in response to an event.

        This method checks all laws to see if they apply to the given event,
        and if their conditions are met. If so, it applies the effects of the law.

        Args:
            event: The name of the event that triggered law enforcement.
            payload: Data associated with the event.
        """
        for law_name, law in self.laws.items():
            if not law.enabled or event not in law.on_event:
                continue
            if not self._conditions_met(law.conditions, payload):
                continue

            # Publish a LawEnforcedEvent
            event_bus.publish(LawEnforcedEvent(
                timestamp=time.time(),
                law_name=law_name,
                event_name=event,
                payload=payload
            ))

            # Apply the effects of the law
            for eff_name, eff in law.effects.items():
                self._apply_effect(eff_name, eff.params, payload)

    def _conditions_met(self, conds: List[str], payload: Dict[str, Any]) -> bool:
        """
        Check if all conditions are met for a law to be applied.

        This is a simple condition evaluator that checks equality conditions.
        It can be replaced with a more sophisticated evaluator in the future.

        Args:
            conds: A list of condition strings in the format "key == value".
            payload: The event payload to check conditions against.

        Returns:
            bool: True if all conditions are met, False otherwise.
        """
        # naïve evaluation – you can swap with tinyexpr or jmespath later
        for c in conds:
            key, op, val = re.split(r"\s*==\s*", c)
            if str(payload.get(key.strip())) != val.strip("'\""):
                return False
        return True

    def _apply_effect(self, name: str, params: Dict[str, Any], payload: Dict[str, Any]) -> None:
        """
        Apply an effect as part of law enforcement.

        This method handles different types of effects that can be applied
        when a law's conditions are met.

        Args:
            name: The name of the effect to apply.
            params: Parameters for the effect.
            payload: The event payload that triggered the law.
        """
        if name == "apply_emotion":
            self.world.eterna.apply_emotion(params["type"], params.get("delta", "+"))
        elif name == "grant_energy":
            target = params.get("target", "agent")
            amt = params["amount"]
            self.world.grant_energy(target, amt)
        # add more handlers as needed
