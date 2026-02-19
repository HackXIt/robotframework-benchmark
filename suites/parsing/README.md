# Parsing Benchmark Suites

Place `.robot` and `.resource` files here to measure how quickly Robot
Framework parses them.

## Suggested file naming

| File                  | Description                                       |
|-----------------------|---------------------------------------------------|
| `small.robot`         | ~5 test cases, minimal keywords                   |
| `medium.robot`        | ~50 test cases, moderate keyword depth            |
| `large.robot`         | ~500 test cases, deep keyword nesting             |
| `resource.resource`   | Resource file with variables and keyword definitions |

## Running

```bash
rfbenchmark run --suite parsing --suite-dir suites/parsing --iterations 10
```
