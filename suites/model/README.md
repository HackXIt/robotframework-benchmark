# Model Benchmark Suites

Place `.robot` files here and provide pre-generated `output.xml` artefacts to
measure Robot Framework model loading and traversal costs.

## Suggested contents

| Path                    | Description                                      |
|-------------------------|--------------------------------------------------|
| `fixture.robot`         | Suite used to generate `output.xml`             |
| `output.xml`            | Pre-generated execution result for loading tests |

## Generating output.xml

```bash
python -m robot --output suites/model/output.xml suites/model/fixture.robot
```

## Running

```bash
rfbenchmark run --suite model --suite-dir suites/model --iterations 3
```
