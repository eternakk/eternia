import asyncio
from world_builder import build_world
from modules.governor import AlignmentGovernor
import os
DEV_TOKEN = os.getenv("ETERNA_TOKEN", "7eba339e71568d9957617382fdb1df65")
event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

world = build_world()
governor = AlignmentGovernor(world, world.state_tracker, event_queue=event_queue)


# ---------------- simulation task ----------------
async def run_world():
    while True:
        if governor.is_shutdown():
            break                    # clean exit
        metrics = world.collect_metrics()
        if governor.tick(metrics):
            world.step()
        await asyncio.sleep(0)       # yield