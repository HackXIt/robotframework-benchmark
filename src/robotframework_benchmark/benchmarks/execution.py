"""
Keyword and test execution benchmarks.

Measures the overhead Robot Framework imposes when executing keywords and
running test cases through its normal execution pipeline.

Benchmark targets
-----------------
- :class:`robot.running.TestSuite` – top-level in-memory execution entry point
- :func:`robot.api.TestSuite.from_file_system` – building + running a suite
- Individual keyword invocation latency via the ``robot.running`` internals

Implementing benchmarks
-----------------------
Subclass :class:`ExecutionBenchmark` and add methods decorated with
:func:`~robotframework_benchmark.benchmarks.base.benchmark`::

    from robotframework_benchmark.benchmarks.execution import ExecutionBenchmark
    from robotframework_benchmark.benchmarks.base import benchmark

    class MyExecutionBenchmark(ExecutionBenchmark):
        @benchmark("execute custom suite")
        def bench_custom(self) -> None:
            suite = robot.api.TestSuite.from_file_system(self.suite_path)
            suite.run(output="NONE")
"""

from __future__ import annotations

import io
import pathlib
import tempfile

import robot.api
import robot.api.interfaces

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark

# ---------------------------------------------------------------------------
# Minimal embedded suites used as execution fixtures.
# ---------------------------------------------------------------------------

_SIMPLE_SUITE = """\
*** Settings ***
Library    Collections

*** Test Cases ***
Log Message
    Log    Hello from benchmark

Create List
    ${items}=    Create List    a    b    c
    Should Contain    ${items}    b
"""

_KEYWORD_SUITE = """\
*** Settings ***
Library    String

*** Keywords ***
Repeat Uppercase
    [Arguments]    ${text}    ${count}
    FOR    ${_}    IN RANGE    ${count}
        ${upper}=    Convert To Uppercase    ${text}
    END
    RETURN    ${upper}

*** Test Cases ***
Keyword Invocation
    Repeat Uppercase    benchmark    10
"""


class ExecutionBenchmark(BaseBenchmark):
    """Benchmarks for Robot Framework keyword and test execution.

    Attributes:
        suite_dir: :class:`~pathlib.Path` to the directory holding ``.robot``
            suites used during execution benchmarks.  Defaults to a temporary
            directory populated with built-in fixtures.

    To use your own suites::

        bench = ExecutionBenchmark()
        bench.suite_dir = pathlib.Path("suites/execution")
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
            (self.suite_dir / "simple.robot").write_text(_SIMPLE_SUITE)
            (self.suite_dir / "keyword.robot").write_text(_KEYWORD_SUITE)

    def teardown(self) -> None:
        """Remove temporary fixture files."""
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None

    # ------------------------------------------------------------------
    # Benchmark methods
    # ------------------------------------------------------------------

    @benchmark("build suite from filesystem")
    def bench_build_suite(self) -> None:
        """Measure the time to build a :class:`robot.api.TestSuite` from disk."""
        robot.api.TestSuite.from_file_system(str(self.suite_dir))

    @benchmark("run simple suite (no output)")
    def bench_run_simple(self) -> None:
        """Build and execute the simple suite, discarding all output."""
        suite = robot.api.TestSuite.from_file_system(
            str(self.suite_dir / "simple.robot")
        )
        # Suppress output artefacts during benchmarking.
        suite.run(output="NONE", log="NONE", report="NONE", stdout=io.StringIO())

    @benchmark("run keyword suite (no output)")
    def bench_run_keywords(self) -> None:
        """Build and execute the keyword-heavy suite, discarding all output."""
        suite = robot.api.TestSuite.from_file_system(
            str(self.suite_dir / "keyword.robot")
        )
        suite.run(output="NONE", log="NONE", report="NONE", stdout=io.StringIO())
