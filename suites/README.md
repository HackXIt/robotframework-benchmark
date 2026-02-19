# Benchmark Test Suites

This directory holds Robot Framework test suites (`.robot` files) used as
input fixtures for the benchmark library.

## Structure

| Directory   | Purpose                                               |
|-------------|-------------------------------------------------------|
| `parsing/`  | Suites measuring Robot Framework **syntax parsing**   |
| `execution/`| Suites measuring **keyword and test execution**       |
| `model/`    | Suites for **model loading and traversal** benchmarks |
| `memory/`   | Suites for **memory and storage** benchmarks          |

## Writing Fixture Suites

Place `.robot` files in the relevant sub-directory and pass the directory path
to the corresponding benchmark class via `--suite-dir`:

```bash
rfbenchmark run --suite parsing --suite-dir suites/parsing
```

Or in Python:

```python
import pathlib
from robotframework_benchmark.benchmarks.parsing import ParsingBenchmark

bench = ParsingBenchmark(suite_dir=pathlib.Path("suites/parsing"), iterations=5)
bench.run()
```

## Tips

- Start with **small** suites to verify the benchmark plumbing works end-to-end.
- Add **medium** (50–200 tests) and **large** (500+ tests) suites to expose
  scaling characteristics.
- Use descriptive suite and test-case names; they appear in benchmark reports.
