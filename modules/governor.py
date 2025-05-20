# modules/governor.py
import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, Callable

from modules.law_parser import load_laws

CHECKPOINT_DIR = Path("artifacts/checkpoints")


class AlignmentGovernor:
    """
    Hard‑safety layer that can pause, rollback, or kill the simulation.
    """

    def __init__(
        self,
        world,
        state_tracker,
        threshold: float = 0.90,
        save_interval: int = 10000,
        event_queue: "asyncio.Queue | None" = None,
    ):
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

        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    MAX_CKPTS = 10  # keep last 10

    # -------- public control API -------- #
    def pause(self):
        self._paused = True
        self._log_event("pause")

    def resume(self):
        self._paused = False
        self._log_event("resume")

    def shutdown(self, reason: str):
        self._log_event("shutdown", reason)
        self._shutdown = True

    def rollback(self, target: Path | None = None):
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
    def tick(self, metrics: Dict) -> bool:
        """
        Returns True if the world may continue this step.
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
        for cb in self.policy_callbacks:
            if cb(metrics) is False:
                self.rollback()
                return False

        # 3) record a safe checkpoint every N ticks or on request
        self._tick_counter += 1
        if self._tick_counter >= self.save_interval:
            self._save_checkpoint()
            self._tick_counter = 0

        return True

    # -------- helper methods -------- #
    def register_policy(self, callback: Callable[[Dict], bool]):
        """Callback receives metrics dict; return False to trigger rollback."""
        self.policy_callbacks.append(callback)

    def _save_checkpoint(self):
        self._broadcast({"event": "checkpoint_scheduled"})
        ts = int(time.time() * 1000)
        path = CHECKPOINT_DIR / f"ckpt_{ts}.bin"
        self.world.save_checkpoint(path)
        self.state_tracker.register_checkpoint(path)  # already exists
        self._log_event("checkpoint_saved", str(path))

        # prune old files
        cks = sorted(CHECKPOINT_DIR.glob("ckpt_*.bin"))
        for old in cks[: -self.MAX_CKPTS]:
            old.unlink(missing_ok=True)

    def _latest_checkpoint(self):
        cks = sorted(CHECKPOINT_DIR.glob("ckpt_*.bin"))
        return cks[-1] if cks else None

    def _broadcast(self, payload: dict):
        """Push log entries to an asyncio.Queue for the API WebSocket."""
        if self.event_queue is not None:
            try:
                self.event_queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass  # drop on overflow

    def _log_event(self, event: str, payload=None):
        entry = {"t": time.time(), "event": event, "payload": payload}
        (CHECKPOINT_DIR / "governor_log.jsonl").open("a").write(
            json.dumps(entry) + "\n"
        )
        self._broadcast(entry)

    # external API can swap in a fresh queue at runtime
    def set_event_queue(self, q: "asyncio.Queue"):
        self.event_queue = q

    def is_shutdown(self) -> bool:
        return self._shutdown

    def _enforce_laws(self, event: str, payload: dict):
        for law in self.laws.values():
            if not law.enabled or event not in law.on_event:
                continue
            if not self._conditions_met(law.conditions, payload):
                continue
            for eff_name, eff in law.effects.items():
                self._apply_effect(eff_name, eff.params, payload)

    def _conditions_met(self, conds, payload):
        # naïve evaluation – you can swap with tinyexpr or jmespath later
        for c in conds:
            key, op, val = re.split(r"\s*==\s*", c)
            if str(payload.get(key.strip())) != val.strip("'\""):
                return False
        return True

    def _apply_effect(self, name, params, payload):
        if name == "apply_emotion":
            self.world.eterna.apply_emotion(params["type"], params.get("delta", "+"))
        elif name == "grant_energy":
            target = params.get("target", "agent")
            amt = params["amount"]
            self.world.grant_energy(target, amt)
        # add more handlers as needed
