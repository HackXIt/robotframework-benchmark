# Execution Benchmark Suites

Place `.robot` files here to measure the overhead of Robot Framework keyword
and test execution.

## Suggested file naming

| File                  | Description                                   |
|-----------------------|-----------------------------------------------|
| `simple.robot`        | Basic `Log` calls, no external libraries      |
| `keyword_heavy.robot` | Deep keyword call stacks                      |
| `loop.robot`          | `FOR` loops and `WHILE` loops                 |
| `library.robot`       | Standard Library keyword usage patterns       |

## Running

```bash
rfbenchmark run --suite execution --suite-dir suites/execution --iterations 5
```
