"""
Benchmark modules for Robot Framework core implementations.

Available benchmarks:
- :mod:`~robotframework_benchmark.benchmarks.parsing` – syntax parsing
- :mod:`~robotframework_benchmark.benchmarks.execution` – keyword and test execution
- :mod:`~robotframework_benchmark.benchmarks.model` – model loading
- :mod:`~robotframework_benchmark.benchmarks.memory` – memory and storage profiling
"""

from robotframework_benchmark.benchmarks.execution import ExecutionBenchmark
from robotframework_benchmark.benchmarks.memory import MemoryBenchmark
from robotframework_benchmark.benchmarks.model import ModelBenchmark
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark

__all__ = [
    "ParsingBenchmark",
    "ExecutionBenchmark",
    "ModelBenchmark",
    "MemoryBenchmark",
]
