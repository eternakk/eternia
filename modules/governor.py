# modules/governor.py
import time
import json
from pathlib import Path
from typing import Dict, Callable

CHECKPOINT_DIR = Path("artifacts/checkpoints")

class AlignmentGovernor:
    """
    Hard‑safety layer that can pause, rollback, or kill the simulation.
    """

    def __init__(self, world, state_tracker, threshold: float = 0.90):
        self.world = world
        self.state_tracker = state_tracker
        self.continuity_threshold = threshold
        self._paused = False
        self.policy_callbacks: list[Callable[[Dict], bool]] = []

        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    # -------- public control API -------- #
    def pause(self):
        self._paused = True
        self._log_event("pause")

    def resume(self):
        self._paused = False
        self._log_event("resume")

    def shutdown(self, reason: str):
        self._log_event("shutdown", reason)
        raise SystemExit(f"[Alignment‑Governor] Shutdown: {reason}")

    def rollback(self):
        ckpt = self._latest_checkpoint()
        if not ckpt:
            self.shutdown("No safe checkpoint available")
        self.world.load_checkpoint(ckpt)
        self.state_tracker.mark_rollback(ckpt)
        self._log_event("rollback", f"to {ckpt}")

    # -------- runtime hook -------- #
    def tick(self, metrics: Dict) -> bool:
        """
        Returns True if the world may continue this step.
        """
        if self._paused:
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
        if metrics.get("checkpoint"):
            self._save_checkpoint()

        return True

    # -------- helper methods -------- #
    def register_policy(self, callback: Callable[[Dict], bool]):
        """Callback receives metrics dict; return False to trigger rollback."""
        self.policy_callbacks.append(callback)

    def _save_checkpoint(self):
        ts = int(time.time() * 1000)
        path = CHECKPOINT_DIR / f"ckpt_{ts}.bin"
        self.world.save_checkpoint(path)
        self.state_tracker.register_checkpoint(path)
        self._log_event("checkpoint_saved", str(path))

    def _latest_checkpoint(self):
        cks = sorted(CHECKPOINT_DIR.glob("ckpt_*.bin"))
        return cks[-1] if cks else None

    def _log_event(self, event: str, payload=None):
        entry = {"t": time.time(), "event": event, "payload": payload}
        (CHECKPOINT_DIR / "governor_log.jsonl").open("a").write(json.dumps(entry) + "\n")