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
        self._rollback_active = False
        self.policy_callbacks: list[Callable[[Dict], bool]] = []

        # Adaptive checkpoint interval based on simulation size
        self.base_save_interval = save_interval
        self.save_interval = self._determine_save_interval()
        self._last_interval_update = 0
        self._interval_update_frequency = 1000  # Check if we need to adjust interval every 1000 ticks

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
        self._rollback_active = True
        try:
            ckpt = target or self._latest_checkpoint()
            if not ckpt:
                self.shutdown("No safe checkpoint available")
                return
            self.world.load_checkpoint(ckpt)
            self.state_tracker.mark_rollback(ckpt)
            # reset counters visible in UI
            self.world.eterna.runtime.cycle_count = 0
            self._log_event("rollback_complete", str(ckpt))
        finally:
            self._rollback_active = False

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
           save interval has been reached and significant changes have occurred.
        5. It adaptively adjusts the checkpoint interval based on simulation size.

        Args:
            metrics: A dictionary of metrics from the world, including
                'identity_continuity' and any other metrics used by policy callbacks.

        Returns:
            bool: True if the world may continue this step, False otherwise.
        """
        # First, check if the simulation is paused or shut down
        # These are the most basic conditions that prevent the simulation from continuing
        if self._paused:
            return False  # Simulation is paused, don't proceed
        if self._shutdown:
            return False  # Simulation is shut down, don't proceed

        # ---- SAFETY CHECK 1: Identity Continuity ----
        # Identity continuity measures how much the world's identity has changed
        # If it drops below the threshold, the world has changed too much and we need to roll back
        identity_continuity = metrics.get("identity_continuity", 1.0)

        # If continuity is below threshold, log the breach, roll back, and halt the simulation
        if identity_continuity < self.continuity_threshold:
            # Log the continuity breach event with the current metrics
            self._log_event("continuity_breach", metrics)
            # Roll back to the last safe checkpoint
            self.rollback()
            # Prevent the simulation from continuing
            return False

        # ---- SAFETY CHECK 2: Policy Callbacks ----
        # Determine if we need to check policies on this tick
        # We check policies either when there's a significant change in continuity
        # or periodically (every 5 ticks) to balance safety and performance
        significant_change = abs(identity_continuity - getattr(self, '_last_continuity', 1.0)) > 0.05
        check_policies = significant_change or (self._tick_counter % 5 == 0)

        if check_policies:
            # Cache the current continuity value for future comparisons
            # This allows us to detect significant changes in the next tick
            self._last_continuity = identity_continuity

            # Run all registered policy callbacks
            # These are custom safety checks that can trigger a rollback
            for i, cb in enumerate(self.policy_callbacks):
                # If any policy callback returns False, the simulation should roll back
                if cb(metrics) is False:
                    # Publish a PolicyViolationEvent to notify other components
                    event_bus.publish(PolicyViolationEvent(
                        timestamp=time.time(),
                        policy_name=f"policy_{i}",  # Use index as name if no better name is available
                        metrics=metrics
                    ))
                    # Roll back to the last safe checkpoint
                    self.rollback()
                    # Prevent the simulation from continuing
                    return False

        # ---- CHECKPOINT MANAGEMENT ----
        # Increment the tick counter for checkpoint scheduling
        self._tick_counter += 1

        # Adaptive checkpoint interval: adjust based on simulation size
        # This ensures efficient resource usage for different simulation scales
        if hasattr(self, '_interval_update_frequency') and self._tick_counter % self._interval_update_frequency == 0:
            # Calculate new interval based on current simulation metrics
            new_interval = self._determine_save_interval()

            # Only update if the change is significant (more than 10% of base interval)
            # This prevents frequent small adjustments that wouldn't meaningfully impact performance
            if abs(new_interval - self.save_interval) > self.base_save_interval * 0.1:
                self.logger.info(f"Adjusting checkpoint interval from {self.save_interval} to {new_interval} ticks based on simulation size")
                self.save_interval = new_interval

        # Determine if we need to create a checkpoint
        # We create checkpoints either:
        # 1. When we reach the regular save interval, OR
        # 2. When there's a significant change and at least 1/10th of the interval has passed
        #    (this ensures we capture important state changes without creating too many checkpoints)
        checkpoint_needed = (self._tick_counter >= self.save_interval) or (
            significant_change and self._tick_counter >= self.save_interval // 10
        )

        if checkpoint_needed:
            # Use a background thread for checkpoint creation if available
            # This prevents the checkpoint creation from blocking the main simulation loop
            if hasattr(self, '_checkpoint_thread') and getattr(self, '_checkpoint_thread', None) is not None:
                # Only create a new checkpoint if the previous thread has finished
                if not self._checkpoint_thread.is_alive():
                    self._checkpoint_thread = None
                    self._save_checkpoint()
                    self._tick_counter = 0  # Reset the counter after creating a checkpoint
            else:
                # If no background thread is available, create the checkpoint directly
                self._save_checkpoint()
                self._tick_counter = 0  # Reset the counter after creating a checkpoint

        # If we've reached this point, all safety checks have passed
        # and the simulation can continue
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

    def _determine_save_interval(self) -> int:
        """
        Determine the appropriate save interval based on simulation size.

        This method implements an adaptive checkpoint interval algorithm that considers:
        1. Memory usage of the process (if psutil is available)
        2. Size of the state tracker's memory collections
        3. Number of zones in the simulation

        The algorithm increases the checkpoint interval for larger simulations to:
        - Reduce disk I/O overhead
        - Prevent performance degradation from frequent checkpointing
        - Balance safety (frequent checkpoints) with performance

        Returns:
            int: The determined save interval in ticks.
        """
        # Start with the base save interval as our foundation
        # This is the default interval specified during initialization
        interval = self.base_save_interval

        # Try to adjust based on system metrics
        try:
            # --- MEMORY-BASED ADJUSTMENT ---
            # Use psutil to get accurate memory usage of the current process
            import psutil
            process = psutil.Process()
            # Calculate memory usage in megabytes for easier threshold comparison
            memory_usage_mb = process.memory_info().rss / (1024 * 1024)

            # Scaling factor: Increase checkpoint interval for larger memory footprints
            # This is because larger memory states take longer to serialize/deserialize
            # and consume more disk space per checkpoint
            if memory_usage_mb > 1000:  # More than 1GB: large simulation
                interval *= 2            # Double the interval
                # Rationale: Very large simulations need much less frequent checkpoints
                # to maintain performance
            elif memory_usage_mb > 500:  # More than 500MB: medium-large simulation
                interval *= 1.5          # Increase by 50%
                # Rationale: Medium-large simulations need moderately less frequent checkpoints

            # --- STATE COMPLEXITY ADJUSTMENT ---
            # Check the size of the memories collection as an indicator of state complexity
            if hasattr(self.state_tracker, "memories"):
                memories_count = len(self.state_tracker.memories)
                # More memories means more complex state to checkpoint
                if memories_count > 1000:  # Very complex state
                    interval *= 1.5        # Increase by 50%
                elif memories_count > 500:  # Moderately complex state
                    interval *= 1.2        # Increase by 20%
                # Rationale: More memories mean larger checkpoint files and longer
                # serialization/deserialization times

            # --- WORLD SIZE ADJUSTMENT ---
            # Check the number of zones as an indicator of world size
            if hasattr(self.world.eterna, "exploration") and hasattr(self.world.eterna.exploration, "registry"):
                # Get the number of zones in the world
                zones_count = len(getattr(self.world.eterna.exploration.registry, "zones", []))
                # More zones means larger world state to checkpoint
                if zones_count > 100:    # Very large world
                    interval *= 1.3      # Increase by 30%
                elif zones_count > 50:   # Medium-large world
                    interval *= 1.1      # Increase by 10%
                # Rationale: More zones mean more objects to serialize and more
                # complex relationships to maintain in checkpoints

        except (ImportError, AttributeError):
            # If psutil is not available or attributes can't be accessed,
            # we fall back to the base interval without adjustments
            # This ensures the system still works even without these optimizations
            pass

        # Ensure we never go below the base interval, even if calculation errors occur
        # This provides a safety guarantee for minimum checkpoint frequency
        return max(int(interval), self.base_save_interval)

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

    def is_rollback_active(self) -> bool:
        """Return True while a rollback operation is underway."""
        return self._rollback_active

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
