from world_builder import build_world
from modules.governor import AlignmentGovernor

# Singletons for now — you can swap with dependency‑injection later
world = build_world()
governor = AlignmentGovernor(world, world.state_tracker)