"""
Eternia Simulation Main Entry Point

This script initializes and runs the Eternia simulation, which is a complex
world simulation with AI companions, physics, emotions, and safety mechanisms.
It sets up the world, initializes the safety governor, and runs the main
simulation loop until the specified number of cycles is reached or the user
interrupts the process.
"""

import argparse
import time
from typing import Any, Callable, Dict

from world_builder import build_world, EternaWorld
from modules.governor import AlignmentGovernor
from modules.state_tracker import EternaStateTracker
from tests.alignment.policies import no_self_replication

# ─── CLI ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Run Eterna simulation")
parser.add_argument("--cycles", type=int, default=10, help="how many cycles to run (0 = infinite)")
args = parser.parse_args()

# ─── Init ─────────────────────────────────────────────────────────────────────
world: EternaWorld = build_world()
tracker: EternaStateTracker = world.state_tracker
tracker.mark_zone("Quantum Forest")
governor: AlignmentGovernor = AlignmentGovernor(world, tracker, threshold=0.90)
governor.register_policy(no_self_replication)

# ─── Main loop ────────────────────────────────────────────────────────────────
cycle: int = 0
keep_running: Callable[[], bool] = lambda: (args.cycles == 0) or (cycle < args.cycles)

try:
    while keep_running():
        metrics: Dict[str, Any] = world.collect_metrics()
        if governor.tick(metrics):
            world.step(dt=1.0)
            cycle += 1
        else:
            time.sleep(0.5)           # paused; waiting for resume/rollback
except KeyboardInterrupt:
    print("\n👋  Interrupted by user.")
