"""
Model loading benchmarks.

Measures the cost of constructing and traversing the Robot Framework in-memory
model objects (:mod:`robot.model`, :mod:`robot.running`, :mod:`robot.result`).

Benchmark targets
-----------------
- :class:`robot.model.TestSuite` construction and visitor traversal
- :class:`robot.running.TestSuite` building via
  :func:`robot.api.TestSuite.from_file_system`
- :class:`robot.result.ExecutionResult` loading from an existing ``output.xml``

Implementing benchmarks
-----------------------
Subclass :class:`ModelBenchmark` and add methods decorated with
:func:`~robotframework_benchmark.benchmarks.base.benchmark`::

    from robotframework_benchmark.benchmarks.model import ModelBenchmark
    from robotframework_benchmark.benchmarks.base import benchmark

    class MyModelBenchmark(ModelBenchmark):
        @benchmark("load large output.xml")
        def bench_load_output(self) -> None:
            robot.result.ExecutionResult(str(self.output_xml_path))
"""

from __future__ import annotations

import io
import pathlib
import tempfile

import robot.api
import robot.model
import robot.result

from robotframework_benchmark.benchmarks.base import BaseBenchmark, benchmark

# ---------------------------------------------------------------------------
# Minimal suite fixture used to generate an output.xml for result-loading
# benchmarks.
# ---------------------------------------------------------------------------

_FIXTURE_SUITE = """\
*** Test Cases ***
Model Fixture
    Log    model benchmark fixture
"""


class ModelBenchmark(BaseBenchmark):
    """Benchmarks for Robot Framework model loading and traversal.

    Attributes:
        suite_dir: :class:`~pathlib.Path` to the directory holding ``.robot``
            fixture files.
        output_xml_path: :class:`~pathlib.Path` to a pre-generated
            ``output.xml`` used for result-loading benchmarks.  When ``None``
            a small one is generated automatically during :meth:`setup`.

    To use your own artefacts::

        bench = ModelBenchmark()
        bench.suite_dir = pathlib.Path("suites/model")
        bench.output_xml_path = pathlib.Path("results/output.xml")
        bench.run()
    """

    def __init__(
        self,
        iterations: int = 1,
        suite_dir: pathlib.Path | None = None,
        output_xml_path: pathlib.Path | None = None,
    ) -> None:
        super().__init__(iterations=iterations)
        self.suite_dir = suite_dir
        self.output_xml_path = output_xml_path
        self._tmpdir: tempfile.TemporaryDirectory | None = None  # type: ignore[type-arg]

    # ------------------------------------------------------------------
    # BaseBenchmark interface
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Prepare fixture files and generate ``output.xml`` if needed."""
        if self.suite_dir is None:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.suite_dir = pathlib.Path(self._tmpdir.name)
            (self.suite_dir / "fixture.robot").write_text(_FIXTURE_SUITE)

        if self.output_xml_path is None:
            output_xml = self.suite_dir / "output.xml"
            suite = robot.api.TestSuite.from_file_system(
                str(self.suite_dir / "fixture.robot")
            )
            suite.run(
                output=str(output_xml),
                log=None,
                report=None,
                stdout=io.StringIO(),
            )
            self.output_xml_path = output_xml

    def teardown(self) -> None:
        """Remove temporary directory (if created during :meth:`setup`)."""
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None

    # ------------------------------------------------------------------
    # Benchmark methods
    # ------------------------------------------------------------------

    @benchmark("build running model from filesystem")
    def bench_build_running_model(self) -> None:
        """Measure the time to build :class:`robot.running.TestSuite` from disk."""
        robot.api.TestSuite.from_file_system(str(self.suite_dir))

    @benchmark("get AST model (get_model)")
    def bench_get_ast_model(self) -> None:
        """Measure the time to obtain the AST model via :func:`robot.api.get_model`."""
        robot.api.get_model(str(self.suite_dir / "fixture.robot"))

    @benchmark("load execution result (output.xml)")
    def bench_load_result(self) -> None:
        """Load an ``output.xml`` file into :class:`robot.result.ExecutionResult`."""
        robot.result.ExecutionResult(str(self.output_xml_path))

    @benchmark("traverse model with SuiteVisitor")
    def bench_traverse_model(self) -> None:
        """Build the running model and traverse it with a no-op :class:`robot.model.SuiteVisitor`."""

        class _Counter(robot.model.SuiteVisitor):
            count = 0

            def visit_test(self, test: robot.model.TestCase) -> None:  # type: ignore[override]
                self.count += 1

        suite = robot.api.TestSuite.from_file_system(str(self.suite_dir))
        visitor = _Counter()
        suite.visit(visitor)
