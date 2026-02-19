"""
Utilities for collecting and representing benchmark metrics.

This module provides :class:`MetricsCollector` for timing code sections and
:class:`BenchmarkResult` for storing, aggregating, and displaying results.
"""

from __future__ import annotations

import statistics
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkResult:
    """Holds timing and (optionally) memory measurements for a single benchmark.

    Attributes:
        name: Human-readable benchmark identifier.
        elapsed_seconds: Wall-clock seconds measured for the run.
        peak_memory_bytes: Peak RSS increase in bytes, or ``None`` when memory
            tracking was disabled.
        extra: Arbitrary additional metadata (e.g. number of parsed tokens).
    """

    name: str
    elapsed_seconds: float
    peak_memory_bytes: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    # Populated by :meth:`aggregate`
    _all_elapsed: list[float] = field(default_factory=list, repr=False)

    @property
    def mean_seconds(self) -> float:
        """Mean wall-clock duration across aggregated runs."""
        if self._all_elapsed:
            return statistics.mean(self._all_elapsed)
        return self.elapsed_seconds

    @property
    def stdev_seconds(self) -> float | None:
        """Standard deviation of wall-clock durations, or ``None`` for a single run."""
        if len(self._all_elapsed) > 1:
            return statistics.stdev(self._all_elapsed)
        return None

    @property
    def min_seconds(self) -> float:
        """Minimum wall-clock duration across aggregated runs."""
        if self._all_elapsed:
            return min(self._all_elapsed)
        return self.elapsed_seconds

    @property
    def max_seconds(self) -> float:
        """Maximum wall-clock duration across aggregated runs."""
        if self._all_elapsed:
            return max(self._all_elapsed)
        return self.elapsed_seconds

    @classmethod
    def aggregate(cls, results: list["BenchmarkResult"]) -> "BenchmarkResult":
        """Combine multiple single-run results into one aggregated result.

        Args:
            results: Non-empty list of :class:`BenchmarkResult` from repeated runs.

        Returns:
            A new :class:`BenchmarkResult` whose :attr:`elapsed_seconds` is the
            mean and :attr:`_all_elapsed` contains all individual samples.

        Raises:
            ValueError: If *results* is empty.
        """
        if not results:
            raise ValueError("Cannot aggregate an empty list of results.")
        all_elapsed = [r.elapsed_seconds for r in results]
        peak_mem = max((r.peak_memory_bytes for r in results if r.peak_memory_bytes is not None), default=None)
        return cls(
            name=results[0].name,
            elapsed_seconds=statistics.mean(all_elapsed),
            peak_memory_bytes=peak_mem,
            extra=results[0].extra,
            _all_elapsed=all_elapsed,
        )

    def __str__(self) -> str:
        runs = len(self._all_elapsed) or 1
        parts = [
            f"[{self.name}]",
            f"mean={self.mean_seconds * 1000:.3f}ms",
        ]
        if runs > 1:
            parts.append(f"runs={runs}")
            if self.stdev_seconds is not None:
                parts.append(f"stdev={self.stdev_seconds * 1000:.3f}ms")
            parts.append(f"min={self.min_seconds * 1000:.3f}ms")
            parts.append(f"max={self.max_seconds * 1000:.3f}ms")
        if self.peak_memory_bytes is not None:
            parts.append(f"peak_mem={self.peak_memory_bytes / 1024:.1f}KB")
        return " ".join(parts)


class MetricsCollector:
    """Collects wall-clock timing and optionally tracemalloc memory statistics.

    Usage::

        collector = MetricsCollector(track_memory=True)
        collector.start()
        do_work()
        result = collector.stop("my benchmark")
        print(result)
    """

    def __init__(self, track_memory: bool = False) -> None:
        self._track_memory = track_memory
        self._start_time: float | None = None

    def start(self) -> None:
        """Begin timing (and optionally memory tracking)."""
        if self._track_memory:
            tracemalloc.start()
        self._start_time = time.perf_counter()

    def stop(self, name: str) -> BenchmarkResult:
        """Stop timing and return a :class:`BenchmarkResult`.

        Args:
            name: Benchmark identifier to embed in the result.

        Raises:
            RuntimeError: If :meth:`start` was not called before :meth:`stop`.
        """
        if self._start_time is None:
            raise RuntimeError("MetricsCollector.stop() called before start().")
        elapsed = time.perf_counter() - self._start_time
        self._start_time = None

        peak_memory: int | None = None
        if self._track_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_memory = peak

        return BenchmarkResult(
            name=name,
            elapsed_seconds=elapsed,
            peak_memory_bytes=peak_memory,
        )
