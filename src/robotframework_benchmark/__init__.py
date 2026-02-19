"""
robotframework-benchmark
========================

A benchmark library for performance testing Robot Framework core implementations.

Main benchmark areas:
- Syntax parsing (``robotframework_benchmark.benchmarks.parsing``)
- Keyword and test execution (``robotframework_benchmark.benchmarks.execution``)
- Model loading (``robotframework_benchmark.benchmarks.model``)
- Memory and storage profiling (``robotframework_benchmark.benchmarks.memory``)

Quick start::

    from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
    from robotframework_benchmark.utils.metrics import BenchmarkResult

    bench = ParsingBenchmark()
    result = bench.run()
    print(result)
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
