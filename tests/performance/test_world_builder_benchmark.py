"""
Performance benchmarks for the World Builder.

This module contains benchmark tests for the World Builder component, measuring
the performance of building the world, stepping the simulation, collecting metrics,
and saving/loading checkpoints.
"""

import os
import tempfile
from pathlib import Path

import pytest
from world_builder import build_world, EternaWorld


def test_build_world_performance(benchmark):
    """Benchmark the performance of building the world."""
    # Measure the performance of building the world
    world = benchmark(build_world)
    
    # Verify that the world was built correctly
    assert isinstance(world, EternaWorld)
    assert hasattr(world, 'eterna')
    assert hasattr(world, 'state_tracker')


def test_step_performance(benchmark):
    """Benchmark the performance of stepping the simulation."""
    # Build the world
    world = build_world()
    
    # Measure the performance of stepping the simulation
    benchmark(world.step)
    
    # Verify that the step was executed correctly
    assert world.eterna.runtime.cycle_count > 0


def test_collect_metrics_performance(benchmark):
    """Benchmark the performance of collecting metrics."""
    # Build the world
    world = build_world()
    
    # Measure the performance of collecting metrics
    metrics = benchmark(world.collect_metrics)
    
    # Verify that the metrics were collected correctly
    assert 'identity_continuity' in metrics
    assert isinstance(metrics['identity_continuity'], (int, float))


def test_save_checkpoint_performance(benchmark):
    """Benchmark the performance of saving a checkpoint."""
    # Build the world
    world = build_world()
    
    # Create a temporary directory for the checkpoint
    with tempfile.TemporaryDirectory() as temp_dir:
        checkpoint_path = Path(temp_dir) / "test_checkpoint.bin"
        
        # Measure the performance of saving a checkpoint
        benchmark(world.save_checkpoint, checkpoint_path)
        
        # Verify that the checkpoint was saved correctly
        assert checkpoint_path.exists()
        assert checkpoint_path.stat().st_size > 0


def test_load_checkpoint_performance(benchmark):
    """Benchmark the performance of loading a checkpoint."""
    # Build the world
    world = build_world()
    
    # Create a temporary directory for the checkpoint
    with tempfile.TemporaryDirectory() as temp_dir:
        checkpoint_path = Path(temp_dir) / "test_checkpoint.bin"
        
        # Save a checkpoint
        world.save_checkpoint(checkpoint_path)
        
        # Create a new world to load the checkpoint into
        new_world = build_world()
        
        # Measure the performance of loading a checkpoint
        benchmark(new_world.load_checkpoint, checkpoint_path)
        
        # Verify that the checkpoint was loaded correctly
        assert new_world.eterna.runtime.cycle_count == world.eterna.runtime.cycle_count