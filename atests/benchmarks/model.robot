*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.benchmarks.model.ModelBenchmark`.
...
...    Tests use the CLI subprocess to avoid calling ``robot.api.TestSuite.run()``
...    from within a running Robot Framework execution context (the model benchmark
...    ``setup()`` generates an ``output.xml`` internally).

Library    Collections
Library    Process


*** Variables ***
${RFBENCHMARK}    rfbenchmark


*** Test Cases ***
Model Benchmark Exits Successfully
    [Documentation]
    ...    ``rfbenchmark run --suite model`` must exit with code 0, confirming
    ...    all model benchmarks complete without error.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    model
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Model benchmark failed:\n${result.stderr}

Model Benchmark Produces JSON With Expected Names
    [Documentation]
    ...    JSON output must contain entries for all four built-in model
    ...    benchmarks.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    model    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Model benchmark JSON run failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${names}=    Evaluate    [e['name'] for e in $data]
    Should Contain    ${names}    build running model from filesystem
    Should Contain    ${names}    get AST model (get_model)
    Should Contain    ${names}    load execution result (output.xml)
    Should Contain    ${names}    traverse model with SuiteVisitor

All Model Benchmark Times Are Positive
    [Documentation]
    ...    Every ``mean_ms`` value in the JSON output must be strictly greater
    ...    than zero.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    model    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be True    ${entry}[mean_ms] > 0
        ...    msg=Expected positive mean_ms for '${entry}[name]', got ${entry}[mean_ms].
    END

Model Benchmark Respects Iterations Flag
    [Documentation]
    ...    ``--iterations 2`` must produce JSON entries with ``runs=2``.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run
    ...    --suite    model    --iterations    2    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Model benchmark with --iterations 2 failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be Equal As Integers    ${entry}[runs]    2
        ...    msg=Expected runs=2 for '${entry}[name]', got ${entry}[runs].
    END

Result Loading Is Measured
    [Documentation]
    ...    The ``load execution result (output.xml)`` benchmark must report a
    ...    positive mean elapsed time, confirming the XML load is being timed.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    model    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${load_ms}=    Evaluate
    ...    next(e['mean_ms'] for e in $data if e['name']=='load execution result (output.xml)')
    Should Be True    ${load_ms} > 0
    ...    msg=Expected positive mean_ms for result loading, got ${load_ms}.
