"""
Memory and storage benchmarks.

Tracks peak heap usage and object counts while Robot Framework performs
common operations.  Uses Python's built-in :mod:`tracemalloc` for allocation
tracking and :mod:`psutil` for process-level RSS metrics.

Benchmark targets
-----------------
- Heap allocation during file parsing (``robot.api.get_model``)
- Object retention after building a :class:`robot.running.TestSuite`
- RSS growth during a full suite run

Implementing benchmarks
-----------------------
Subclass :class:`MemoryBenchmark` and add methods decorated with
:func:`~robotframework_benchmark.benchmarks.base.benchmark`::

    from robotframework_benchmark.benchmarks.memory import MemoryBenchmark
    from robotframework_benchmark.benchmarks.base import benchmark

    class MyMemoryBenchmark(MemoryBenchmark):
        @benchmark("heap usage for my suite")
        def bench_my_suite_memory(self) -> None:
            robot.api.get_model(str(self.suite_dir / "my.robot"))

.. note::
    Memory benchmarks use :class:`~robotframework_benchmark.utils.metrics.MetricsCollector`
    with ``track_memory=True``.  Results will include
    :attr:`~robotframework_benchmark.utils.metrics.BenchmarkResult.peak_memory_bytes`.
"""

from __future__ import annotations

import io
import pathlib
import tempfile
import tracemalloc

import psutil
import robot.api

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark

_FIXTURE_SUITE = """\
*** Settings ***
Library    Collections

*** Test Cases ***
Memory Fixture 1
    ${lst}=    Create List    a    b    c    d    e
    Log    ${lst}

Memory Fixture 2
    ${dct}=    Create Dictionary    key=value    foo=bar
    Log    ${dct}
"""


class MemoryBenchmark(BaseBenchmark):
    """Benchmarks focused on memory usage of Robot Framework operations.

    Attributes:
        suite_dir: :class:`~pathlib.Path` to the directory holding ``.robot``
            fixture files.

    To use your own suites::

        bench = MemoryBenchmark()
        bench.suite_dir = pathlib.Path("suites/memory")
        bench.run()
    """

    def __init__(self, iterations: int = 1, suite_dir: pathlib.Path | None = None) -> None:
        super().__init__(iterations=iterations)
        self.suite_dir = suite_dir
        self._tmpdir: tempfile.TemporaryDirectory | None = None  # type: ignore[type-arg]

    # ------------------------------------------------------------------
    # BaseBenchmark interface
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Write fixture suites to a temporary directory."""
        if self.suite_dir is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.suite_dir = pathlib.Path(self._tmpdir.name)
            (self.suite_dir / "memory_fixture.robot").write_text(_FIXTURE_SUITE)

    def teardown(self) -> None:
        """Remove temporary fixture files."""
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None

    # ------------------------------------------------------------------
    # Benchmark methods
    # ------------------------------------------------------------------

    @benchmark("heap usage during parsing", track_memory=True)
    def bench_parse_heap(self) -> None:
        """Measure peak tracemalloc heap during ``get_model``."""
        robot.api.get_model(str(self.suite_dir / "memory_fixture.robot"))

    @benchmark("rss growth during suite run")
    def bench_rss_growth(self) -> None:
        """Measure process RSS before and after executing the fixture suite."""
        proc = psutil.Process()
        rss_before = proc.memory_info().rss
        suite = robot.api.TestSuite.from_file_system(
            str(self.suite_dir / "memory_fixture.robot")
        )
        suite.run(output=None, log=None, report=None, stdout=io.StringIO())
        rss_after = proc.memory_info().rss
        growth = max(0, rss_after - rss_before)
        # Store RSS growth in the result's extra metadata.
        self.results["rss growth during suite run"].extra["rss_growth_bytes"] = growth

    @benchmark("tracemalloc top allocations during build")
    def bench_top_allocations(self) -> None:
        """Capture the top 10 allocation sites while building the running model."""
        tracemalloc.start()
        robot.api.TestSuite.from_file_system(str(self.suite_dir))
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        top_stats = snapshot.statistics("lineno")[:10]
        # Embed the top allocation sites in the result's ``extra`` dict.
        self.results["tracemalloc top allocations during build"].extra["top_allocations"] = [
            str(stat) for stat in top_stats
        ]
