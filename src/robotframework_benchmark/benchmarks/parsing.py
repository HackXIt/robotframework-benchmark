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

Fixture files
-------------
Built-in fixture ``.robot`` and ``.resource`` files live in:
``fixtures/parsing/`` (alongside this module).

Implementing benchmarks
-----------------------
Subclass or extend :class:`ParsingBenchmark` and add methods decorated with
:func:`~robotframework_benchmark.benchmarks.base.benchmark`::

    from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
    from robotframework_benchmark.benchmarks.base import benchmark

    class MyParsingBenchmark(ParsingBenchmark):
        @benchmark("parse custom file")
        def bench_custom(self) -> None:
            robot.api.get_model(str(self.suite_dir / "custom.robot"))
"""

import pathlib
import shutil
import tempfile
from typing import Optional

import robot.api

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark

# Directory containing the built-in fixture files shipped with the package.
_FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "parsing"


class ParsingBenchmark(BaseBenchmark):
    """Benchmarks for Robot Framework syntax parsing.

    Attributes:
        suite_dir: :class:`~pathlib.Path` to the directory holding benchmark
            ``.robot`` and ``.resource`` fixtures.  Defaults to a temporary
            directory populated with the built-in fixtures when
            :meth:`setup` is called.

    To use your own suites, set ``suite_dir`` before calling :meth:`run`::

        bench = ParsingBenchmark()
        bench.suite_dir = pathlib.Path("suites/parsing")
        bench.run()
    """

    def __init__(self, iterations: int = 1, suite_dir: Optional[pathlib.Path] = None) -> None:
        super().__init__(iterations=iterations)
        self.suite_dir = suite_dir
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None  # type: ignore[type-arg]

    # ------------------------------------------------------------------
    # BaseBenchmark interface
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Copy built-in fixture files to a temporary directory if no ``suite_dir`` was provided."""
        if self.suite_dir is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.suite_dir = pathlib.Path(self._tmpdir.name)
            for src in _FIXTURES_DIR.iterdir():
                shutil.copy2(src, self.suite_dir / src.name)

    def teardown(self) -> None:
        """Remove temporary fixture directory (if created during :meth:`setup`)."""
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
