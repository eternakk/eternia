import asyncio
from world_builder import build_world
from modules.governor import AlignmentGovernor

event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

world = build_world()
governor = AlignmentGovernor(world, world.state_tracker, event_queue=event_queue)

# ---------------- simulation task ----------------
async def run_world():
    while True:
        metrics = world.collect_metrics()
        if governor.tick(metrics):
            world.step()          # advances cycle_count
        await asyncio.sleep(0)    # yield to event loop