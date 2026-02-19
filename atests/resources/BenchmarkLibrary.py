"""
Robot Framework keyword library providing access to the benchmark Python API.

This library is intended for use in the ``atests/`` acceptance test suites.
It wraps the benchmark classes and utilities so they can be exercised through
standard Robot Framework keyword calls.

Usage in a ``.robot`` file::

    *** Settings ***
    Library    ../resources/BenchmarkLibrary.py

    *** Test Cases ***
    Parsing benchmark returns results
        ${results}=    Run Parsing Benchmark
        Should Not Be Empty    ${results}
"""

from __future__ import annotations

import io
import json
from typing import Any

from robot.api.deco import keyword, library

from robotframework_benchmark.benchmarks.execution import ExecutionBenchmark
from robotframework_benchmark.benchmarks.memory import MemoryBenchmark
from robotframework_benchmark.benchmarks.model import ModelBenchmark
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
from robotframework_benchmark.utils.metrics import BenchmarkResult, MetricsCollector
from robotframework_benchmark.utils.reporting import ConsoleReporter, JsonReporter


@library(scope="SUITE", doc_format="reST")
class BenchmarkLibrary:
    """Keyword library for testing the robotframework-benchmark Python API.

    Scope is ``SUITE`` so that one library instance is shared across all tests
    in a suite, but a fresh instance is created for each suite file.
    """

    # ------------------------------------------------------------------
    # Parsing benchmark keywords
    # ------------------------------------------------------------------

    @keyword("Run Parsing Benchmark")
    def run_parsing_benchmark(self, iterations: int = 1) -> dict[str, BenchmarkResult]:
        """Run all :class:`~robotframework_benchmark.benchmarks.parsing.ParsingBenchmark`
        methods and return the results dict.

        Args:
            iterations: Number of times each benchmark method is executed.

        Returns:
            Dict mapping benchmark name → :class:`~robotframework_benchmark.utils.metrics.BenchmarkResult`.
        """
        bench = ParsingBenchmark(iterations=int(iterations))
        return bench.run()

    # ------------------------------------------------------------------
    # Execution benchmark keywords
    # ------------------------------------------------------------------

    @keyword("Run Execution Benchmark")
    def run_execution_benchmark(self, iterations: int = 1) -> dict[str, BenchmarkResult]:
        """Run all :class:`~robotframework_benchmark.benchmarks.execution.ExecutionBenchmark`
        methods and return the results dict.
        """
        bench = ExecutionBenchmark(iterations=int(iterations))
        return bench.run()

    # ------------------------------------------------------------------
    # Model benchmark keywords
    # ------------------------------------------------------------------

    @keyword("Run Model Benchmark")
    def run_model_benchmark(self, iterations: int = 1) -> dict[str, BenchmarkResult]:
        """Run all :class:`~robotframework_benchmark.benchmarks.model.ModelBenchmark`
        methods and return the results dict.
        """
        bench = ModelBenchmark(iterations=int(iterations))
        return bench.run()

    # ------------------------------------------------------------------
    # Memory benchmark keywords
    # ------------------------------------------------------------------

    @keyword("Run Memory Benchmark")
    def run_memory_benchmark(self, iterations: int = 1) -> dict[str, BenchmarkResult]:
        """Run all :class:`~robotframework_benchmark.benchmarks.memory.MemoryBenchmark`
        methods and return the results dict.
        """
        bench = MemoryBenchmark(iterations=int(iterations))
        return bench.run()

    # ------------------------------------------------------------------
    # BenchmarkResult inspection keywords
    # ------------------------------------------------------------------

    @keyword("Get Result Elapsed Seconds")
    def get_result_elapsed_seconds(
        self, results: dict[str, BenchmarkResult], name: str
    ) -> float:
        """Return the mean elapsed seconds for benchmark *name* from *results*.

        Fails if *name* is not present in *results*.
        """
        if name not in results:
            raise AssertionError(
                f"Benchmark '{name}' not found in results. "
                f"Available: {list(results.keys())}"
            )
        return results[name].mean_seconds

    @keyword("Get Result Peak Memory Bytes")
    def get_result_peak_memory_bytes(
        self, results: dict[str, BenchmarkResult], name: str
    ) -> int | None:
        """Return peak memory bytes for benchmark *name*, or ``None`` if not tracked."""
        if name not in results:
            raise AssertionError(f"Benchmark '{name}' not found in results.")
        return results[name].peak_memory_bytes

    @keyword("Result Should Have Memory Info")
    def result_should_have_memory_info(
        self, results: dict[str, BenchmarkResult], name: str
    ) -> None:
        """Fail unless *name* has a non-None :attr:`peak_memory_bytes`."""
        peak = self.get_result_peak_memory_bytes(results, name)
        if peak is None:
            raise AssertionError(
                f"Benchmark '{name}' has no memory info (peak_memory_bytes is None)."
            )
        if peak <= 0:
            raise AssertionError(
                f"Benchmark '{name}' has zero or negative peak_memory_bytes: {peak}."
            )

    @keyword("Result Elapsed Should Be Positive")
    def result_elapsed_should_be_positive(
        self, results: dict[str, BenchmarkResult], name: str
    ) -> None:
        """Fail unless *name* has a strictly positive elapsed time."""
        elapsed = self.get_result_elapsed_seconds(results, name)
        if elapsed <= 0:
            raise AssertionError(
                f"Benchmark '{name}' elapsed time is not positive: {elapsed}s."
            )

    @keyword("Results Should Contain Benchmarks")
    def results_should_contain_benchmarks(
        self, results: dict[str, BenchmarkResult], *names: str
    ) -> None:
        """Fail unless *results* contains all given benchmark *names*."""
        missing = [n for n in names if n not in results]
        if missing:
            raise AssertionError(
                f"Missing benchmarks in results: {missing}. "
                f"Available: {list(results.keys())}"
            )

    # ------------------------------------------------------------------
    # BenchmarkResult factory keywords
    # ------------------------------------------------------------------

    @keyword("Create Result With Memory Info")
    def create_result_with_memory_info(
        self, name: str, elapsed_ms: float = 1.0, peak_bytes: int = 1024
    ) -> BenchmarkResult:
        """Create a :class:`BenchmarkResult` with ``peak_memory_bytes`` set.

        Useful for testing reporters without having to run a full memory
        benchmark that internally calls ``robot.api.TestSuite.run()``.

        Args:
            name: Benchmark name to embed in the result.
            elapsed_ms: Elapsed time in milliseconds (default: 1.0).
            peak_bytes: Peak memory in bytes (default: 1024).
        """
        return BenchmarkResult(
            name=name,
            elapsed_seconds=float(elapsed_ms) / 1000.0,
            peak_memory_bytes=int(peak_bytes),
        )

    # ------------------------------------------------------------------
    # MetricsCollector keywords
    # ------------------------------------------------------------------

    @keyword("Create Metrics Collector")
    def create_metrics_collector(self, track_memory: bool = False) -> MetricsCollector:
        """Create and return a :class:`~robotframework_benchmark.utils.metrics.MetricsCollector`."""
        return MetricsCollector(track_memory=track_memory)

    @keyword("Start Metrics Collector")
    def start_metrics_collector(self, collector: MetricsCollector) -> None:
        """Start timing (and optional memory tracking) on *collector*.

        Call :keyword:`Stop Metrics Collector` to end the measurement and
        obtain a :class:`~robotframework_benchmark.utils.metrics.BenchmarkResult`.
        """
        collector.start()

    @keyword("Stop Metrics Collector")
    def stop_metrics_collector(
        self, collector: MetricsCollector, name: str
    ) -> BenchmarkResult:
        """Stop *collector* and return the :class:`BenchmarkResult` for *name*."""
        return collector.stop(name)

    # ------------------------------------------------------------------
    # Reporting keywords
    # ------------------------------------------------------------------

    @keyword("Console Report As String")
    def console_report_as_string(
        self, results: dict[str, BenchmarkResult]
    ) -> str:
        """Render *results* with :class:`~robotframework_benchmark.utils.reporting.ConsoleReporter`
        and return the output as a string.
        """
        buf = io.StringIO()
        ConsoleReporter(stream=buf).report(results)
        return buf.getvalue()

    @keyword("Json Report As String")
    def json_report_as_string(
        self, results: dict[str, BenchmarkResult]
    ) -> str:
        """Render *results* with :class:`~robotframework_benchmark.utils.reporting.JsonReporter`
        and return the JSON string.
        """
        buf = io.StringIO()
        JsonReporter(stream=buf).report(results)
        return buf.getvalue()

    @keyword("Json Report Should Be Valid")
    def json_report_should_be_valid(self, json_string: str) -> list[dict[str, Any]]:
        """Parse *json_string* as JSON; fail if it is not a non-empty list of objects.

        Returns the parsed list on success.
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"JSON output is not valid JSON: {exc}") from exc
        if not isinstance(data, list):
            raise AssertionError(f"Expected a JSON array, got {type(data).__name__}.")
        if not data:
            raise AssertionError("JSON array is empty.")
        for entry in data:
            for required in ("name", "mean_ms", "min_ms", "max_ms"):
                if required not in entry:
                    raise AssertionError(
                        f"JSON entry missing required key '{required}': {entry}"
                    )
        return data
