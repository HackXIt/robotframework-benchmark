*** Settings ***
Documentation
...    Common variables, imports, and keywords shared across all acceptance
...    test suites in ``atests/``.

Library    Collections
Library    OperatingSystem
Library    String
Library    ${CURDIR}/BenchmarkLibrary.py


*** Variables ***
# Minimum iteration count used in multi-run tests.
${DEFAULT_ITERATIONS}    3


*** Keywords ***
Results Should Not Be Empty
    [Documentation]    Fail if the given results dict is empty.
    [Arguments]    ${results}
    Should Not Be Empty    ${results}
    ...    msg=Benchmark run returned an empty results dict.

All Results Should Have Positive Elapsed Time
    [Documentation]
    ...    Iterate over every entry in *results* and fail if any has a
    ...    non-positive elapsed time.
    [Arguments]    ${results}
    ${names}=    Get Dictionary Keys    ${results}
    FOR    ${name}    IN    @{names}
        Result Elapsed Should Be Positive    ${results}    ${name}
    END

Result Mean Should Be Less Than
    [Documentation]
    ...    Fail unless the mean elapsed time for *name* is strictly below
    ...    *threshold_ms* milliseconds.  Useful as a smoke-level sanity check
    ...    that benchmarks are not stuck in an infinite loop.
    [Arguments]    ${results}    ${name}    ${threshold_ms}
    ${elapsed_s}=    Get Result Elapsed Seconds    ${results}    ${name}
    ${elapsed_ms}=    Evaluate    ${elapsed_s} * 1000
    Should Be True    ${elapsed_ms} < ${threshold_ms}
    ...    msg=${name}: elapsed exceeds threshold of ${threshold_ms}ms
