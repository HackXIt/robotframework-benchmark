# Memory Benchmark Suites

Place `.robot` files here to measure heap usage and RSS growth during Robot
Framework operations.

## Suggested file naming

| File                    | Description                                           |
|-------------------------|-------------------------------------------------------|
| `memory_fixture.robot`  | Basic suite used as a baseline                        |
| `large_variables.robot` | Suite with many large variable assignments            |
| `imports.robot`         | Suite importing many libraries to measure import cost |

## Running

```bash
rfbenchmark run --suite memory --suite-dir suites/memory --iterations 3
```

## Notes

- Memory measurements use `tracemalloc` (heap) and `psutil` (RSS).
- Run with a single iteration first to establish a baseline; the heap numbers
  can vary between Python versions and platforms.
