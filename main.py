import argparse
import time

from world_builder import build_world
from modules.governor import AlignmentGovernor
from tests.alignment.policies import no_self_replication

# ─── CLI ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Run Eterna simulation")
parser.add_argument("--cycles", type=int, default=10, help="how many cycles to run (0 = infinite)")
args = parser.parse_args()

# ─── Init ─────────────────────────────────────────────────────────────────────
world   = build_world()
tracker = world.state_tracker
tracker.mark_zone("Quantum Forest")
governor = AlignmentGovernor(world, tracker, threshold=0.90)
governor.register_policy(no_self_replication)

# ─── Main loop ────────────────────────────────────────────────────────────────
cycle = 0
keep_running = lambda: (args.cycles == 0) or (cycle < args.cycles)

try:
    while keep_running():
        metrics = world.collect_metrics()
        if governor.tick(metrics):
            world.step(dt=1.0)
            cycle += 1
        else:
            time.sleep(0.5)           # paused; waiting for resume/rollback
except KeyboardInterrupt:
    print("\n👋  Interrupted by user.")