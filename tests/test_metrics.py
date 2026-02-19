"""
Tests for the metrics collection utilities.
"""

from __future__ import annotations

import time

import pytest

from robotframework_benchmark.utils.metrics import BenchmarkResult, MetricsCollector


class TestMetricsCollector:
    def test_stop_without_start_raises(self) -> None:
        collector = MetricsCollector()
        with pytest.raises(RuntimeError, match="start"):
            collector.stop("test")

    def test_basic_timing(self) -> None:
        collector = MetricsCollector()
        collector.start()
        time.sleep(0.01)
        result = collector.stop("sleep benchmark")
        assert result.elapsed_seconds >= 0.01
        assert result.name == "sleep benchmark"
        assert result.peak_memory_bytes is None

    def test_memory_tracking(self) -> None:
        collector = MetricsCollector(track_memory=True)
        collector.start()
        _data = [0] * 100_000  # allocate some memory
        result = collector.stop("alloc benchmark")
        assert result.peak_memory_bytes is not None
        assert result.peak_memory_bytes > 0


class TestBenchmarkResult:
    def test_str_single_run(self) -> None:
        result = BenchmarkResult(name="my bench", elapsed_seconds=0.5)
        text = str(result)
        assert "my bench" in text
        assert "500.000ms" in text

    def test_aggregate_mean(self) -> None:
        results = [
            BenchmarkResult(name="x", elapsed_seconds=0.1),
            BenchmarkResult(name="x", elapsed_seconds=0.3),
        ]
        agg = BenchmarkResult.aggregate(results)
        assert agg.mean_seconds == pytest.approx(0.2)
        assert agg.min_seconds == pytest.approx(0.1)
        assert agg.max_seconds == pytest.approx(0.3)
        assert agg.stdev_seconds is not None

    def test_aggregate_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            BenchmarkResult.aggregate([])
