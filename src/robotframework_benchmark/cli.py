"""
Command-line interface for running Robot Framework benchmarks.

Usage::

    # Run all benchmarks with default settings
    rfbenchmark run

    # Run only parsing benchmarks, 10 iterations, JSON output
    rfbenchmark run --suite parsing --iterations 10 --format json

    # Show available benchmark suites
    rfbenchmark list
"""

import argparse
import sys
from typing import List, Optional

_SUITES = {
    "parsing": "robotframework_benchmark.benchmarks.parsing.ParsingBenchmark",
    "execution": "robotframework_benchmark.benchmarks.execution.ExecutionBenchmark",
    "model": "robotframework_benchmark.benchmarks.model.ModelBenchmark",
    "memory": "robotframework_benchmark.benchmarks.memory.MemoryBenchmark",
}


def _import_class(dotted_path: str):
    module_path, _, class_name = dotted_path.rpartition(".")
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rfbenchmark",
        description="Robot Framework benchmark runner",
    )
    sub = parser.add_subparsers(dest="command")

    # --- list ---
    sub.add_parser("list", help="List available benchmark suites.")

    # --- run ---
    run_parser = sub.add_parser("run", help="Execute benchmark suites.")
    run_parser.add_argument(
        "--suite",
        metavar="NAME",
        choices=list(_SUITES),
        action="append",
        dest="suites",
        help=(
            "Benchmark suite to run.  May be repeated.  "
            "Choices: {}.  ".format(", ".join(_SUITES)) +
            "Defaults to all suites."
        ),
    )
    run_parser.add_argument(
        "--iterations",
        metavar="N",
        type=int,
        default=1,
        help="Number of iterations per benchmark method (default: 1).",
    )
    run_parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
        help="Output format (default: console).",
    )
    run_parser.add_argument(
        "--suite-dir",
        metavar="PATH",
        default=None,
        help="Path to a directory containing .robot suite fixtures.",
    )

    return parser


def _cmd_list() -> None:
    print("Available benchmark suites:")
    for name, dotted_path in _SUITES.items():
        print("  {:<12}  ({})".format(name, dotted_path))


def _cmd_run(args: argparse.Namespace) -> None:
    import pathlib

    from robotframework_benchmark.utils.reporting import ConsoleReporter, JsonReporter

    selected_suites = args.suites or list(_SUITES)
    suite_dir = pathlib.Path(args.suite_dir) if args.suite_dir else None
    reporter = JsonReporter() if args.format == "json" else ConsoleReporter()

    all_results = {}
    for suite_name in selected_suites:
        klass = _import_class(_SUITES[suite_name])
        kwargs = {"iterations": args.iterations}
        if suite_dir is not None:
            kwargs["suite_dir"] = suite_dir
        instance = klass(**kwargs)
        results = instance.run()
        all_results.update(results)

    reporter.report(all_results)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the ``rfbenchmark`` CLI command.

    Returns:
        Exit code (0 on success, non-zero on error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        _cmd_list()
    elif args.command == "run":
        _cmd_run(args)
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
