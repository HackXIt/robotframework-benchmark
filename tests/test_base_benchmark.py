"""
Tests for the benchmark base class.
"""

from __future__ import annotations

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark
from robotframework_benchmark.utils.metrics import BenchmarkResult


class _SimpleBenchmark(BaseBenchmark):
    """Minimal concrete benchmark for testing the base class."""

    setup_called = False
    teardown_called = False
    bench_called = 0

    def setup(self) -> None:
        self.setup_called = True

    def teardown(self) -> None:
        self.teardown_called = True

    @benchmark("simple operation")
    def bench_simple(self) -> None:
        self.bench_called += 1


class TestBaseBenchmark:
    def test_run_calls_setup_and_teardown(self) -> None:
        b = _SimpleBenchmark()
        b.run()
        assert b.setup_called
        assert b.teardown_called

    def test_run_returns_results(self) -> None:
        b = _SimpleBenchmark()
        results = b.run()
        assert "simple operation" in results
        assert isinstance(results["simple operation"], BenchmarkResult)

    def test_run_iterations(self) -> None:
        b = _SimpleBenchmark(iterations=3)
        b.run()
        assert b.bench_called == 3

    def test_teardown_called_on_exception(self) -> None:
        class _FailingBenchmark(BaseBenchmark):
            teardown_called = False

            def setup(self) -> None:
                raise RuntimeError("setup failed")

            def teardown(self) -> None:
                self.teardown_called = True

            @benchmark("noop")
            def bench_noop(self) -> None:
                pass

        b = _FailingBenchmark()
        try:
            b.run()
        except RuntimeError:
            pass
        assert b.teardown_called
