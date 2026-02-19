"""
Base benchmark class providing common infrastructure for all benchmark types.

All concrete benchmarks should subclass :class:`BaseBenchmark` and implement
:meth:`BaseBenchmark.setup`, :meth:`BaseBenchmark.teardown`, and one or more
benchmark methods decorated with :func:`~robotframework_benchmark.benchmarks.base.benchmark`.
"""

import abc
import functools
import time
from collections.abc import Callable
from typing import Any, Dict, List, Optional

from robotframework_benchmark.utils.metrics import BenchmarkResult, MetricsCollector


def benchmark(name: Optional[str] = None, track_memory: bool = False) -> Callable:
    """Decorator that marks a method as a benchmark target.

    The decorated method is timed automatically and a :class:`BenchmarkResult`
    is stored on the instance under ``self.results[name]``.

    Args:
        name: Human-readable name for this benchmark.  Defaults to the
            method's ``__name__``.
        track_memory: When ``True``, enable :mod:`tracemalloc` memory tracking
            so that :attr:`~BenchmarkResult.peak_memory_bytes` is populated.

    Example::

        class MyBenchmark(BaseBenchmark):
            @benchmark("parse small suite", track_memory=True)
            def bench_parse_small(self):
                ...  # code under measurement
    """

    def decorator(func: Callable) -> Callable:
        label = name or func.__name__

        @functools.wraps(func)
        def wrapper(self: "BaseBenchmark", *args: Any, **kwargs: Any) -> BenchmarkResult:
            # Pre-create a placeholder so that function bodies can enrich
            # self.results[label].extra before timing completes.
            placeholder = BenchmarkResult(name=label, elapsed_seconds=0.0)
            self.results[label] = placeholder

            collector = MetricsCollector(track_memory=track_memory)
            collector.start()
            try:
                func(self, *args, **kwargs)
            finally:
                result = collector.stop(label)

            # Merge any extras the function body attached to the placeholder.
            result.extra.update(placeholder.extra)
            if placeholder.peak_memory_bytes is not None and result.peak_memory_bytes is None:
                result.peak_memory_bytes = placeholder.peak_memory_bytes
            self.results[label] = result
            return result

        wrapper._is_benchmark = True  # type: ignore[attr-defined]
        wrapper._benchmark_name = label  # type: ignore[attr-defined]
        return wrapper

    return decorator


class BaseBenchmark(abc.ABC):
    """Abstract base class for all benchmark implementations.

    Subclasses must implement :meth:`setup` and :meth:`teardown`.  Benchmark
    methods should be decorated with :func:`benchmark`.

    Attributes:
        results: Mapping of benchmark name to :class:`BenchmarkResult` populated
            after :meth:`run` is called.
        iterations: Number of times each benchmark method is executed during
            :meth:`run`.

    Example::

        class MySuite(BaseBenchmark):
            def setup(self) -> None:
                self.resource = load_something()

            def teardown(self) -> None:
                self.resource = None

            @benchmark("my operation")
            def bench_operation(self) -> None:
                do_work(self.resource)

        suite = MySuite(iterations=5)
        suite.run()
        for name, result in suite.results.items():
            print(name, result.mean_seconds)
    """

    def __init__(self, iterations: int = 1) -> None:
        self.iterations = iterations
        self.results: Dict[str, BenchmarkResult] = {}

    @abc.abstractmethod
    def setup(self) -> None:
        """Prepare any state or resources needed by the benchmark."""

    @abc.abstractmethod
    def teardown(self) -> None:
        """Release any resources acquired in :meth:`setup`."""

    def run(self) -> Dict[str, BenchmarkResult]:
        """Execute all benchmark methods and return accumulated results.

        Each method decorated with :func:`benchmark` is called
        :attr:`iterations` times.  Results from repeated runs are averaged into
        a single :class:`BenchmarkResult` stored in :attr:`results`.

        Returns:
            The :attr:`results` dict mapping benchmark name to result.
        """
        try:
            self.setup()
            bench_methods = [
                getattr(self, m)
                for m in dir(self)
                if callable(getattr(self, m)) and getattr(getattr(self, m), "_is_benchmark", False)
            ]

            accumulated: Dict[str, List[BenchmarkResult]] = {}
            for _ in range(self.iterations):
                for method in bench_methods:
                    result = method()
                    accumulated.setdefault(result.name, []).append(result)

            for bench_name, run_results in accumulated.items():
                self.results[bench_name] = BenchmarkResult.aggregate(run_results)
        finally:
            self.teardown()

        return self.results

    def _wall_time(self) -> float:  # noqa: PLR6301
        """Return the current wall-clock time in seconds."""
        return time.perf_counter()
