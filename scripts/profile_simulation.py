#!/usr/bin/env python3
"""
Profiling script for the Eternia simulation loop.

This script profiles the simulation loop to identify bottlenecks and
performance issues. It runs the simulation for a specified number of
cycles and generates a profile report.
"""

import cProfile
import pstats
import io
import time
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from world_builder import build_world
from modules.governor import AlignmentGovernor


def run_simulation(cycles=100):
    """
    Run the simulation for a specified number of cycles.
    
    Args:
        cycles: The number of cycles to run
    """
    # Build the world
    world = build_world()
    
    # Create a governor
    governor = AlignmentGovernor(world, world.state_tracker)
    
    # Run the simulation for the specified number of cycles
    for _ in range(cycles):
        metrics = world.collect_metrics()
        if governor.tick(metrics):
            world.step()
            world.eterna.runtime.cycle_count += 1
    
    return world, governor


def profile_simulation(cycles=100, output_file=None):
    """
    Profile the simulation loop.
    
    Args:
        cycles: The number of cycles to profile
        output_file: The file to write the profile results to
    """
    # Create a profiler
    profiler = cProfile.Profile()
    
    # Start the profiler
    profiler.enable()
    
    # Run the simulation
    start_time = time.time()
    world, governor = run_simulation(cycles)
    end_time = time.time()
    
    # Stop the profiler
    profiler.disable()
    
    # Print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Average time per cycle: {elapsed_time / cycles:.4f} seconds")
    
    # Create a StringIO object to capture the profile output
    s = io.StringIO()
    
    # Sort the profile stats by cumulative time
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    
    # Print the profile stats
    ps.print_stats(30)  # Print the top 30 functions by cumulative time
    
    # Print the profile output
    print(s.getvalue())
    
    # If an output file is specified, write the profile results to it
    if output_file:
        with open(output_file, 'w') as f:
            f.write(s.getvalue())
    
    return world, governor


def profile_specific_components(cycles=10):
    """
    Profile specific components of the simulation loop.
    
    Args:
        cycles: The number of cycles to profile
    """
    # Build the world
    world = build_world()
    
    # Create a governor
    governor = AlignmentGovernor(world, world.state_tracker)
    
    # Profile collect_metrics
    start_time = time.time()
    for _ in range(cycles):
        metrics = world.collect_metrics()
    end_time = time.time()
    collect_metrics_time = end_time - start_time
    print(f"collect_metrics: {collect_metrics_time:.4f} seconds ({collect_metrics_time / cycles:.4f} seconds per cycle)")
    
    # Profile governor.tick
    start_time = time.time()
    for _ in range(cycles):
        governor.tick(metrics)
    end_time = time.time()
    governor_tick_time = end_time - start_time
    print(f"governor.tick: {governor_tick_time:.4f} seconds ({governor_tick_time / cycles:.4f} seconds per cycle)")
    
    # Profile world.step
    start_time = time.time()
    for _ in range(cycles):
        world.step()
    end_time = time.time()
    world_step_time = end_time - start_time
    print(f"world.step: {world_step_time:.4f} seconds ({world_step_time / cycles:.4f} seconds per cycle)")
    
    return world, governor


def main():
    """Main function."""
    # Create the output directory if it doesn't exist
    output_dir = Path('artifacts/profiling')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Profile the simulation
    print("Profiling simulation...")
    output_file = output_dir / 'simulation_profile.txt'
    world, governor = profile_simulation(cycles=100, output_file=output_file)
    
    # Profile specific components
    print("\nProfiling specific components...")
    profile_specific_components(cycles=10)
    
    print(f"\nProfile results written to {output_file}")


if __name__ == '__main__':
    main()