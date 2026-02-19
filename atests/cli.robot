*** Settings ***
Documentation
...    Acceptance tests for the ``rfbenchmark`` CLI entry-point.
...
...    Tests verify that the CLI commands ``list`` and ``run`` behave
...    correctly and produce the expected output for each benchmark suite
...    and output format.

Library    Collections
Library    OperatingSystem
Library    Process
Library    String


*** Variables ***
${RFBENCHMARK}    rfbenchmark


*** Test Cases ***
List Command Prints All Suite Names
    [Documentation]
    ...    ``rfbenchmark list`` should print the names of all four built-in
    ...    benchmark suites and exit with code 0.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    list
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark list exited with non-zero code: ${result.stderr}
    Should Contain    ${result.stdout}    parsing
    Should Contain    ${result.stdout}    execution
    Should Contain    ${result.stdout}    model
    Should Contain    ${result.stdout}    memory

No Subcommand Returns Non-Zero Exit Code
    [Documentation]
    ...    Invoking ``rfbenchmark`` without a subcommand should print help and
    ...    exit with a non-zero exit code.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}
    ...    stdout=PIPE    stderr=PIPE
    Should Not Be Equal As Integers    ${result.rc}    0
    ...    msg=Expected non-zero exit code when no subcommand is given.

Run Parsing Suite Exits Successfully
    [Documentation]    ``rfbenchmark run --suite parsing`` should exit 0.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    run    --suite    parsing
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --suite parsing failed: ${result.stderr}

Run Parsing Suite Produces Console Output
    [Documentation]
    ...    Console output should mention parsing-related benchmark names.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    run    --suite    parsing
    ...    stdout=PIPE    stderr=PIPE
    Should Contain    ${result.stdout}    parse
    ...    msg=Expected 'parse' in console output but got:\n${result.stdout}

Run Parsing Suite With JSON Format Produces Valid JSON
    [Documentation]
    ...    ``rfbenchmark run --suite parsing --format json`` must output a
    ...    JSON array where each element has at minimum ``name`` and ``mean_ms``.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run    --suite    parsing    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --format json failed: ${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    Should Not Be Empty    ${data}    msg=JSON output array is empty.
    FOR    ${entry}    IN    @{data}
        Dictionary Should Contain Key    ${entry}    name
        Dictionary Should Contain Key    ${entry}    mean_ms
        Dictionary Should Contain Key    ${entry}    min_ms
        Dictionary Should Contain Key    ${entry}    max_ms
    END

Run Execution Suite Exits Successfully
    [Documentation]    ``rfbenchmark run --suite execution`` should exit 0.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    run    --suite    execution
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --suite execution failed: ${result.stderr}

Run Model Suite Exits Successfully
    [Documentation]    ``rfbenchmark run --suite model`` should exit 0.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    run    --suite    model
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --suite model failed: ${result.stderr}

Run Memory Suite Exits Successfully
    [Documentation]    ``rfbenchmark run --suite memory`` should exit 0.
    ${result}=    Run Process    uv    run    ${RFBENCHMARK}    run    --suite    memory
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --suite memory failed: ${result.stderr}

Run Multiple Suites In One Invocation
    [Documentation]
    ...    Passing ``--suite`` multiple times should run all selected suites
    ...    and produce combined output.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run
    ...    --suite    parsing    --suite    execution    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Multi-suite run failed: ${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    ${count}=    Get Length    ${data}
    Should Be True    ${count} >= 2
    ...    msg=Expected at least 2 benchmark results, got ${count}.

Run With Iterations Flag Produces Multi-Run Results
    [Documentation]
    ...    ``--iterations 2`` should produce JSON entries whose ``runs``
    ...    field equals 2.
    ${result}=    Run Process
    ...    uv    run    ${RFBENCHMARK}    run
    ...    --suite    parsing    --iterations    2    --format    json
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=rfbenchmark run --iterations 2 failed: ${result.stderr}
    ${data}=    Evaluate    __import__('json').loads($result.stdout)
    FOR    ${entry}    IN    @{data}
        Should Be Equal As Integers    ${entry}[runs]    2
        ...    msg=Expected runs=2 for '${entry}[name]', got ${entry}[runs].
    END
