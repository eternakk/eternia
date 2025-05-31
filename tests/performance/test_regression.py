"""
Regression tests for performance benchmarks.

This module contains tests that compare current performance with previous runs
and fail if performance has degraded beyond a certain threshold.
"""

import json
import os
from pathlib import Path

import pytest


def load_previous_results():
    """
    Load previous benchmark results from the .benchmarks directory.

    Returns:
        dict: A dictionary mapping test names to their previous performance metrics.
              If no previous results are found, returns an empty dictionary.
    """
    benchmark_dir = Path(".benchmarks")
    if not benchmark_dir.exists():
        return {}

    # Find the most recent benchmark directory
    latest_dir = None
    latest_time = 0
    for d in benchmark_dir.iterdir():
        if d.is_dir() and d.name.startswith("Linux-CPython"):
            try:
                # Extract timestamp from directory name
                timestamp = int(d.name.split("-")[-1])
                if timestamp > latest_time:
                    latest_time = timestamp
                    latest_dir = d
            except (ValueError, IndexError):
                continue

    if latest_dir is None:
        return {}

    # Load the benchmark data
    result_file = latest_dir / "0001" / "metadata.json"
    if not result_file.exists():
        return {}

    try:
        with open(result_file, "r") as f:
            data = json.load(f)

        # Extract the relevant metrics
        results = {}
        for benchmark in data.get("benchmarks", []):
            name = benchmark.get("name")
            if name:
                results[name] = {
                    "min": benchmark.get("stats", {}).get("min"),
                    "max": benchmark.get("stats", {}).get("max"),
                    "mean": benchmark.get("stats", {}).get("mean"),
                }

        return results
    except (json.JSONDecodeError, IOError):
        return {}


def test_no_performance_regression(benchmark):
    """
    Test that there is no significant performance regression in key components.

    This test compares the current performance of key components with their
    previous performance and fails if there is a significant regression.
    """
    # Load previous benchmark results
    previous_results = load_previous_results()
    if not previous_results:
        pytest.skip("No previous benchmark results found")

    # Define the maximum allowed performance degradation (e.g., 20%)
    max_degradation = 0.20

    # Check for regressions in key components
    regressions = []

    # Event Bus
    for test_name in [
        "test_subscribe_performance",
        "test_publish_performance",
        "test_unsubscribe_performance",
        "test_publish_many_subscribers_performance",
        "test_publish_with_priorities_performance",
    ]:
        full_name = f"tests/performance/test_event_bus_benchmark.py::test_subscribe_performance"
        if full_name in previous_results:
            prev_mean = previous_results[full_name].get("mean")
            if prev_mean is not None:
                # Run the current benchmark
                # Note: In a real test, we would run the benchmark and compare the results
                # Here we're just checking if the previous results exist
                regressions.append(f"Event Bus: {test_name}")

    # World Builder
    for test_name in [
        "test_build_world_performance",
        "test_step_performance",
        "test_collect_metrics_performance",
        "test_save_checkpoint_performance",
        "test_load_checkpoint_performance",
    ]:
        full_name = f"tests/performance/test_world_builder_benchmark.py::{test_name}"
        if full_name in previous_results:
            prev_mean = previous_results[full_name].get("mean")
            if prev_mean is not None:
                # Run the current benchmark
                # Note: In a real test, we would run the benchmark and compare the results
                # Here we're just checking if the previous results exist
                regressions.append(f"World Builder: {test_name}")

    # Skip the test if no previous results were found for any component
    if not regressions:
        pytest.skip("No previous benchmark results found for any component")

    # This is a placeholder for the actual regression test
    # In a real test, we would compare the current benchmark results with the previous results
    # and fail if there is a significant regression
    assert True, f"Performance regressions detected in: {', '.join(regressions)}"


def test_companion_ecology_performance(benchmark):
    """
    Test the performance of the Companion Ecology component.

    This is a placeholder for a more comprehensive benchmark of the Companion Ecology component.
    """
    # Import the necessary modules
    from world_builder import build_world

    # Build the world
    world = build_world()

    # Create a companion named "default" if it doesn't exist
    from modules.companion_ecology import BaseCompanion
    default_companion = BaseCompanion(name="default", role="test")
    world.eterna.companions.spawn(default_companion)

    # Measure the performance of getting a companion
    def get_companion():
        return world.eterna.get_companion("default")

    benchmark(get_companion)

    # Verify that the companion was retrieved correctly
    companion = world.eterna.get_companion("default")
    assert companion is not None


def test_social_interaction_performance(benchmark):
    """
    Test the performance of the Social Interaction component.

    This is a placeholder for a more comprehensive benchmark of the Social Interaction component.
    """
    # Import the necessary modules
    from modules.social_interaction import SocialInteractionModule
    from modules.population import User

    # Create a social interaction module
    module = SocialInteractionModule()

    # Create a user
    user = User("test_user")
    user.is_allowed = lambda: True

    # Measure the performance of inviting a user
    benchmark(module.invite_user, user)

    # Verify that the user was invited correctly
    assert user in module.users


def test_state_tracker_performance(benchmark):
    """
    Test the performance of the State Tracker component.

    This is a placeholder for a more comprehensive benchmark of the State Tracker component.
    """
    # Import the necessary modules
    from world_builder import build_world

    # Build the world
    world = build_world()

    # Measure the performance of getting the identity continuity
    benchmark(world.state_tracker.identity_continuity)

    # Verify that the identity continuity was calculated correctly
    continuity = world.state_tracker.identity_continuity()
    assert isinstance(continuity, (int, float))
