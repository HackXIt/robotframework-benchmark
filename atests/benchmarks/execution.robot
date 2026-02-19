*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.benchmarks.execution.ExecutionBenchmark`.
...
...    Tests use the CLI subprocess to avoid calling ``robot.api.TestSuite.run()``
...    from within a running Robot Framework execution context, which would
...    corrupt the outer execution's XML output state.

Library    Collections
Library    Process


*** Variables ***
${RFBENCHMARK}    rfbenchmark


*** Test Cases ***
Execution Benchmark Exits Successfully
    [Documentation]
    ...    ``rfbenchmark run --suite execution`` must exit with code 0,
    ...    confirming all execution benchmarks complete without error.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    execution
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Execution benchmark failed:\n${result.stderr}

Execution Benchmark Produces JSON With Expected Names
    [Documentation]
    ...    JSON output must contain entries for all three built-in execution
    ...    benchmarks.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    execution    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Execution benchmark JSON run failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${names}=    Evaluate    [e['name'] for e in $data]
    Should Contain    ${names}    build suite from filesystem
    Should Contain    ${names}    run simple suite (no output)
    Should Contain    ${names}    run keyword suite (no output)

All Execution Benchmark Times Are Positive
    [Documentation]
    ...    Every ``mean_ms`` value in the JSON output must be strictly greater
    ...    than zero.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    execution    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be True    ${entry}[mean_ms] > 0
        ...    msg=Expected positive mean_ms for '${entry}[name]', got ${entry}[mean_ms].
    END

Running A Suite Reports Longer Time Than Building It
    [Documentation]
    ...    ``run simple suite (no output)`` should take at least as long as
    ...    ``build suite from filesystem``, since running includes building.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    execution    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${build_ms}=    Evaluate    next(e['mean_ms'] for e in $data if e['name']=='build suite from filesystem')
    ${run_ms}=    Evaluate    next(e['mean_ms'] for e in $data if e['name']=='run simple suite (no output)')
    Should Be True    ${run_ms} >= ${build_ms}
    ...    msg=Expected run (${run_ms}ms) >= build (${build_ms}ms).

Execution Benchmark Respects Iterations Flag
    [Documentation]
    ...    ``--iterations 2`` must produce JSON entries with ``runs=2``.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run
    ...    --suite    execution    --iterations    2    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Execution benchmark with --iterations 2 failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be Equal As Integers    ${entry}[runs]    2
        ...    msg=Expected runs=2 for '${entry}[name]', got ${entry}[runs].
    END

Suite Run Time Is Within Reasonable Bounds
    [Documentation]
    ...    A sanity check that the simple suite runs in under 30 seconds,
    ...    to detect hangs or runaway execution.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    execution    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${run_ms}=    Evaluate    next(e['mean_ms'] for e in $data if e['name']=='run simple suite (no output)')
    Should Be True    ${run_ms} < 30000
    ...    msg=Simple suite run exceeded 30s threshold: ${run_ms}ms.
