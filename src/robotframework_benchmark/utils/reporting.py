"""
Utilities for reporting and exporting benchmark results.

Provides :class:`ConsoleReporter` for human-readable terminal output and
:class:`JsonReporter` for machine-readable JSON export.  Both implement the
:class:`BaseReporter` interface.
"""

from __future__ import annotations

import abc
import json
import sys
from typing import IO, Any

from robotframework_benchmark.utils.metrics import BenchmarkResult


class BaseReporter(abc.ABC):
    """Abstract reporter interface."""

    @abc.abstractmethod
    def report(self, results: dict[str, BenchmarkResult]) -> None:
        """Emit *results* through this reporter's output channel."""


class ConsoleReporter(BaseReporter):
    """Write a formatted summary table to *stream* (default: ``sys.stdout``).

    Example output::

        ┌─────────────────────────────────────────────────────────────────────┐
        │                     Benchmark Results                               │
        ├──────────────────────┬──────────┬──────────┬──────────┬─────────────┤
        │ Benchmark            │ Mean(ms) │ Min(ms)  │ Max(ms)  │ Peak Mem    │
        ├──────────────────────┼──────────┼──────────┼──────────┼─────────────┤
        │ parse small suite    │    1.234 │    1.100 │    1.400 │  256.0 KB   │
        └──────────────────────┴──────────┴──────────┴──────────┴─────────────┘
    """

    _COL_WIDTHS = (28, 10, 10, 10, 12)
    _HEADERS = ("Benchmark", "Mean(ms)", "Min(ms)", "Max(ms)", "Peak Mem")

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream = stream or sys.stdout

    def report(self, results: dict[str, BenchmarkResult]) -> None:
        if not results:
            self._stream.write("No benchmark results to report.\n")
            return

        w = self._COL_WIDTHS
        sep_top = "┌" + "┬".join("─" * (cw + 2) for cw in w) + "┐"
        sep_mid = "├" + "┼".join("─" * (cw + 2) for cw in w) + "┤"
        sep_bot = "└" + "┴".join("─" * (cw + 2) for cw in w) + "┘"

        def row(cells: tuple[str, ...]) -> str:
            padded = [f" {str(c):<{w[i]}} " for i, c in enumerate(cells)]
            return "│" + "│".join(padded) + "│"

        title = " Benchmark Results "
        total_width = sum(w) + 2 * len(w) + len(w) - 1
        self._stream.write("┌" + title.center(total_width, "─") + "┐\n")
        self._stream.write(sep_mid + "\n")
        self._stream.write(row(self._HEADERS) + "\n")
        self._stream.write(sep_mid + "\n")

        for result in results.values():
            mem_str = f"{result.peak_memory_bytes / 1024:.1f} KB" if result.peak_memory_bytes else "N/A"
            self._stream.write(
                row((
                    result.name[:w[0]],
                    f"{result.mean_seconds * 1000:.3f}",
                    f"{result.min_seconds * 1000:.3f}",
                    f"{result.max_seconds * 1000:.3f}",
                    mem_str,
                ))
                + "\n"
            )

        self._stream.write(sep_bot + "\n")


class JsonReporter(BaseReporter):
    """Serialise benchmark results to JSON.

    Args:
        stream: Output stream (default: ``sys.stdout``).
        indent: JSON indentation level (default: ``2``).
    """

    def __init__(self, stream: IO[str] | None = None, indent: int = 2) -> None:
        self._stream = stream or sys.stdout
        self._indent = indent

    def report(self, results: dict[str, BenchmarkResult]) -> None:
        payload: list[dict[str, Any]] = []
        for result in results.values():
            entry: dict[str, Any] = {
                "name": result.name,
                "mean_ms": round(result.mean_seconds * 1000, 6),
                "min_ms": round(result.min_seconds * 1000, 6),
                "max_ms": round(result.max_seconds * 1000, 6),
                "runs": len(result._all_elapsed) or 1,
            }
            if result.stdev_seconds is not None:
                entry["stdev_ms"] = round(result.stdev_seconds * 1000, 6)
            if result.peak_memory_bytes is not None:
                entry["peak_memory_bytes"] = result.peak_memory_bytes
            if result.extra:
                entry["extra"] = result.extra
            payload.append(entry)
        json.dump(payload, self._stream, indent=self._indent)
        self._stream.write("\n")
