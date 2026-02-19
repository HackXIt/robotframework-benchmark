*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.benchmarks.memory.MemoryBenchmark`.
...
...    Tests use the CLI subprocess to avoid calling ``robot.api.TestSuite.run()``
...    from within a running Robot Framework execution context.

Library    Collections
Library    Process


*** Variables ***
${RFBENCHMARK}    rfbenchmark


*** Test Cases ***
Memory Benchmark Exits Successfully
    [Documentation]
    ...    ``rfbenchmark run --suite memory`` must exit with code 0, confirming
    ...    all memory benchmarks complete without error.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    memory
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Memory benchmark failed:\n${result.stderr}

Memory Benchmark Produces JSON With Expected Names
    [Documentation]
    ...    JSON output must contain entries for all three built-in memory
    ...    benchmarks.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    memory    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Memory benchmark JSON run failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${names}=    Evaluate    [e['name'] for e in $data]
    Should Contain    ${names}    heap usage during parsing
    Should Contain    ${names}    rss growth during suite run
    Should Contain    ${names}    tracemalloc top allocations during build

All Memory Benchmark Times Are Positive
    [Documentation]
    ...    Every ``mean_ms`` value in the JSON output must be strictly greater
    ...    than zero.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    memory    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be True    ${entry}[mean_ms] > 0
        ...    msg=Expected positive mean_ms for '${entry}[name]', got ${entry}[mean_ms].
    END

Heap Usage Benchmark Reports Peak Memory Bytes
    [Documentation]
    ...    The ``heap usage during parsing`` benchmark uses ``track_memory=True``
    ...    so its JSON entry must include a positive ``peak_memory_bytes`` field.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    memory    --format    json
    ...    stdout=PIPE    stderr=PIPE
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${heap_entry}=    Evaluate
    ...    next(e for e in $data if e['name']=='heap usage during parsing')
    Dictionary Should Contain Key    ${heap_entry}    peak_memory_bytes
    ...    msg=Expected 'peak_memory_bytes' in heap benchmark JSON entry.
    Should Be True    ${heap_entry}[peak_memory_bytes] > 0
    ...    msg=peak_memory_bytes must be positive.

Memory Benchmark Respects Iterations Flag
    [Documentation]
    ...    ``--iterations 2`` must produce JSON entries with ``runs=2``.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run
    ...    --suite    memory    --iterations    2    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Memory benchmark with --iterations 2 failed:\n${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be Equal As Integers    ${entry}[runs]    2
        ...    msg=Expected runs=2 for '${entry}[name]', got ${entry}[runs].
    END
