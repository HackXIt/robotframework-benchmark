"""
Tests for benchmark suite classes (parsing, execution, model, memory).

These are lightweight smoke tests that verify each benchmark can be
instantiated, run, and return results – they do NOT assert exact timings.
"""

from __future__ import annotations

import pytest

from robotframework_benchmark.benchmarks.execution import ExecutionBenchmark
from robotframework_benchmark.benchmarks.memory import MemoryBenchmark
from robotframework_benchmark.benchmarks.model import ModelBenchmark
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
from robotframework_benchmark.utils.metrics import BenchmarkResult


class TestParsingBenchmark:
    def test_run_returns_results(self) -> None:
        bench = ParsingBenchmark(iterations=1)
        results = bench.run()
        assert results
        for result in results.values():
            assert isinstance(result, BenchmarkResult)
            assert result.elapsed_seconds >= 0

    def test_expected_benchmark_names(self) -> None:
        bench = ParsingBenchmark()
        results = bench.run()
        expected = {
            "parse small suite",
            "parse medium suite",
            "parse large suite",
            "parse resource file",
        }
        assert expected.issubset(results.keys())


class TestExecutionBenchmark:
    def test_run_returns_results(self) -> None:
        bench = ExecutionBenchmark(iterations=1)
        results = bench.run()
        assert results
        for result in results.values():
            assert isinstance(result, BenchmarkResult)

    def test_expected_benchmark_names(self) -> None:
        bench = ExecutionBenchmark()
        results = bench.run()
        expected = {
            "build suite from filesystem",
            "run simple suite (no output)",
            "run keyword suite (no output)",
        }
        assert expected.issubset(results.keys())


class TestModelBenchmark:
    def test_run_returns_results(self) -> None:
        bench = ModelBenchmark(iterations=1)
        results = bench.run()
        assert results
        for result in results.values():
            assert isinstance(result, BenchmarkResult)

    def test_expected_benchmark_names(self) -> None:
        bench = ModelBenchmark()
        results = bench.run()
        expected = {
            "build running model from filesystem",
            "get AST model (get_model)",
            "load execution result (output.xml)",
            "traverse model with SuiteVisitor",
        }
        assert expected.issubset(results.keys())


class TestMemoryBenchmark:
    def test_run_returns_results(self) -> None:
        bench = MemoryBenchmark(iterations=1)
        results = bench.run()
        assert results

    def test_heap_usage_benchmark_has_memory_info(self) -> None:
        bench = MemoryBenchmark()
        results = bench.run()
        heap_result = results.get("heap usage during parsing")
        assert heap_result is not None
        assert heap_result.peak_memory_bytes is not None
        assert heap_result.peak_memory_bytes > 0
