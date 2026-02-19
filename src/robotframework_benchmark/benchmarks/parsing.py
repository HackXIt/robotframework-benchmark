"""
Syntax parsing benchmarks.

Measures how quickly Robot Framework's parser can process ``.robot`` and
``.resource`` source files of varying sizes and complexity.

Benchmark targets
-----------------
- :func:`robot.api.get_model` – high-level file-to-model parsing
- :class:`robot.running.builder.builders.SuiteStructureParser` – internal
  structure parser used when building a full :class:`~robot.running.TestSuite`
- :func:`robot.api.get_resource_model` – resource file parsing

Implementing benchmarks
-----------------------
Subclass or extend :class:`ParsingBenchmark` and add methods decorated with
:func:`~robotframework_benchmark.benchmarks.base.benchmark`::

    from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
    from robotframework_benchmark.benchmarks.base import benchmark

    class MyParsingBenchmark(ParsingBenchmark):
        @benchmark("parse custom file")
        def bench_custom(self) -> None:
            robot.api.get_model(self.suite_path / "custom.robot")
"""

from __future__ import annotations

import pathlib
import tempfile

import robot.api

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark

# ---------------------------------------------------------------------------
# Minimal embedded Robot Framework source used as fixture data.
# Replace these with real suite files in ``suites/parsing/`` for meaningful
# results.
# ---------------------------------------------------------------------------

_SMALL_SUITE = """\
*** Settings ***
Documentation    A small suite for parsing benchmarks.

*** Test Cases ***
First Test
    Log    Hello, world!

Second Test
    Log    Goodbye, world!
"""

_MEDIUM_SUITE = _SMALL_SUITE + "\n".join(
    f"Test {i}\n    Log    iteration {i}\n" for i in range(50)
)

_LARGE_SUITE = _SMALL_SUITE + "\n".join(
    f"Test {i}\n    Log    iteration {i}\n" for i in range(500)
)

_RESOURCE_FILE = """\
*** Settings ***
Documentation    A resource file for parsing benchmarks.

*** Variables ***
${GREETING}    Hello

*** Keywords ***
Greet
    [Arguments]    ${name}
    Log    ${GREETING}, ${name}!
"""


class ParsingBenchmark(BaseBenchmark):
    """Benchmarks for Robot Framework syntax parsing.

    Attributes:
        suite_dir: :class:`~pathlib.Path` to the directory holding benchmark
            ``.robot`` and ``.resource`` fixtures.  Defaults to a temporary
            directory populated with the built-in small/medium/large fixtures
            when :meth:`setup` is called.

    To use your own suites, set ``suite_dir`` before calling :meth:`run`::

        bench = ParsingBenchmark()
        bench.suite_dir = pathlib.Path("suites/parsing")
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
        """Create temporary fixture files if no ``suite_dir`` was provided."""
        if self.suite_dir is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.suite_dir = pathlib.Path(self._tmpdir.name)
            (self.suite_dir / "small.robot").write_text(_SMALL_SUITE)
            (self.suite_dir / "medium.robot").write_text(_MEDIUM_SUITE)
            (self.suite_dir / "large.robot").write_text(_LARGE_SUITE)
            (self.suite_dir / "resource.resource").write_text(_RESOURCE_FILE)

    def teardown(self) -> None:
        """Remove temporary fixture files (if created during :meth:`setup`)."""
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None

    # ------------------------------------------------------------------
    # Benchmark methods
    # ------------------------------------------------------------------

    @benchmark("parse small suite")
    def bench_parse_small(self) -> None:
        """Parse a small ``.robot`` file (~4 test cases)."""
        robot.api.get_model(str(self.suite_dir / "small.robot"))

    @benchmark("parse medium suite")
    def bench_parse_medium(self) -> None:
        """Parse a medium ``.robot`` file (~52 test cases)."""
        robot.api.get_model(str(self.suite_dir / "medium.robot"))

    @benchmark("parse large suite")
    def bench_parse_large(self) -> None:
        """Parse a large ``.robot`` file (~502 test cases)."""
        robot.api.get_model(str(self.suite_dir / "large.robot"))

    @benchmark("parse resource file")
    def bench_parse_resource(self) -> None:
        """Parse a ``.resource`` file."""
        robot.api.get_resource_model(str(self.suite_dir / "resource.resource"))
