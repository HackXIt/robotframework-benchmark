# robotframework-benchmark

A benchmark library for performance testing Robot Framework core implementations.

The goal of this project is to provide tooling to deeply examine speed, memory
usage, and storage characteristics of the
[Robot Framework](https://github.com/robotframework/robotframework) Python
implementation, covering key areas that matter to both framework maintainers and
third-party library developers.

## Features

- **Syntax parsing** – measure how quickly the RF parser processes `.robot` and
  `.resource` files of varying sizes
- **Keyword & test execution** – quantify the overhead the framework adds around
  keyword calls and test runs
- **Model loading** – benchmark `robot.model` / `robot.running` / `robot.result`
  construction and traversal
- **Memory & storage** – track heap allocations (`tracemalloc`) and process RSS
  (`psutil`) during common operations

## Requirements

- Python ≥ 3.13
- [uv](https://docs.astral.sh/uv/) for package management

## Installation

```bash
# Clone the repo
git clone https://github.com/HackXIt/robotframework-benchmark.git
cd robotframework-benchmark

# Install with dev extras (includes pytest + pytest-benchmark)
uv sync --extra dev
```

## Quick Start

### CLI

```bash
# List available benchmark suites
rfbenchmark list

# Run all benchmarks (1 iteration, console output)
rfbenchmark run

# Run only parsing benchmarks with 10 iterations
rfbenchmark run --suite parsing --iterations 10

# Run parsing + execution, output as JSON
rfbenchmark run --suite parsing --suite execution --format json

# Point at your own suite directory
rfbenchmark run --suite parsing --suite-dir suites/parsing --iterations 5
```

### Python API

```python
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
from robotframework_benchmark.utils.reporting import ConsoleReporter

bench = ParsingBenchmark(iterations=5)
results = bench.run()

reporter = ConsoleReporter()
reporter.report(results)
```

## Project Structure

```
robotframework-benchmark/
├── pyproject.toml                    # uv project config & dependencies
├── src/
│   └── robotframework_benchmark/
│       ├── __init__.py               # package version
│       ├── cli.py                    # `rfbenchmark` CLI entry point
│       ├── benchmarks/
│       │   ├── base.py               # BaseBenchmark + @benchmark decorator
│       │   ├── parsing.py            # syntax parsing benchmarks
│       │   ├── execution.py          # keyword/test execution benchmarks
│       │   ├── model.py              # model loading & traversal benchmarks
│       │   └── memory.py             # memory & storage benchmarks
│       └── utils/
│           ├── metrics.py            # MetricsCollector + BenchmarkResult
│           └── reporting.py          # ConsoleReporter + JsonReporter
├── suites/                           # Robot Framework .robot fixture files
│   ├── parsing/                      # fixtures for parsing benchmarks
│   ├── execution/                    # fixtures for execution benchmarks
│   ├── model/                        # fixtures for model benchmarks
│   └── memory/                       # fixtures for memory benchmarks
└── tests/                            # pytest unit/smoke tests
```

## Running Tests

```bash
uv run pytest
```

## Benchmark Suites (Robot Framework Syntax)

The `suites/` directory is where you add your own `.robot` files to use as
benchmark inputs.  Each sub-directory contains a `README.md` describing the
expected fixtures and how to point the CLI at them.

The benchmark classes ship with small built-in fixtures so you can verify
everything works before adding your own larger suites.

## Extending Benchmarks

Every benchmark class follows the same pattern – subclass `BaseBenchmark` and
decorate methods with `@benchmark`:

```python
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark
from robotframework_benchmark.benchmarks.base import benchmark

class MyParsingBenchmark(ParsingBenchmark):
    @benchmark("parse my custom suite")
    def bench_custom(self) -> None:
        import robot.api
        robot.api.get_model(str(self.suite_dir / "my_suite.robot"))
```

## License

MIT
