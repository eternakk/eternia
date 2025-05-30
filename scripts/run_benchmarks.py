#!/usr/bin/env python3
"""
Script to run performance benchmarks and track results over time.

This script runs the performance benchmarks and saves the results to a file
that can be used to track performance over time.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def run_benchmarks(args):
    """
    Run the performance benchmarks.
    
    Args:
        args: Command-line arguments.
    
    Returns:
        int: The return code from the pytest command.
    """
    # Create the command to run the benchmarks
    cmd = ["pytest", "tests/performance/"]
    
    # Add verbose flag if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add benchmark flags
    cmd.extend([
        "--benchmark-json", str(args.output),
        "--benchmark-columns", "min,max,mean,stddev",
    ])
    
    # Run the benchmarks
    print(f"Running benchmarks: {' '.join(cmd)}")
    return subprocess.call(cmd)


def compare_with_previous(args):
    """
    Compare current benchmark results with previous runs.
    
    Args:
        args: Command-line arguments.
    
    Returns:
        int: 0 if successful, 1 if there was an error.
    """
    # Create the command to compare benchmarks
    cmd = ["pytest-benchmark", "compare"]
    
    # Add verbose flag if requested
    if args.verbose:
        cmd.append("--verbose")
    
    # Run the comparison
    print(f"Comparing benchmarks: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run performance benchmarks and track results over time.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", "-o", type=Path, default=Path("benchmark_results.json"),
                        help="Output file for benchmark results")
    parser.add_argument("--compare", "-c", action="store_true", help="Compare with previous runs")
    
    args = parser.parse_args()
    
    # Create the output directory if it doesn't exist
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Run the benchmarks
    ret_code = run_benchmarks(args)
    
    # Compare with previous runs if requested
    if args.compare and ret_code == 0:
        ret_code = compare_with_previous(args)
    
    return ret_code


if __name__ == "__main__":
    sys.exit(main())