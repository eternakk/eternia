# Performance Benchmarks

This directory contains performance benchmark tests for the Eternia project. These tests measure the performance of key system components and track changes over time to detect performance regressions.

## Running Benchmarks

To run all benchmarks:

```bash
pytest tests/performance/ -v
```

To run a specific benchmark:

```bash
pytest tests/performance/test_event_bus_benchmark.py -v
```

## Benchmark Results

Benchmark results are stored in the `.benchmarks` directory at the root of the project. This directory is created automatically by pytest-benchmark when you run the benchmarks.

To compare current results with previous runs:

```bash
pytest-benchmark compare
```

## Creating New Benchmarks

To create a new benchmark test, follow these steps:

1. Create a new file in this directory with a name like `test_<component>_benchmark.py`.
2. Import the component you want to benchmark.
3. Create a test function that takes a `benchmark` fixture as an argument.
4. Use the `benchmark` fixture to measure the performance of the component.

Example:

```python
def test_component_performance(benchmark):
    # Setup code here
    
    # Measure performance
    result = benchmark(
        component.function_to_benchmark,
        arg1, arg2, ...
    )
    
    # Assertions to verify the result is correct
    assert result == expected_result
```

## Regression Tests

Regression tests compare current performance with previous runs and fail if performance has degraded beyond a certain threshold. These tests are defined in the `test_regression.py` file.

To run only regression tests:

```bash
pytest tests/performance/test_regression.py -v
```