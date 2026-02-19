*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.benchmarks.parsing.ParsingBenchmark`.
...
...    Verifies that the benchmark can be run via the Python API and that all
...    expected benchmark names are present with valid measurements.

Resource    ../resources/common.resource


*** Test Cases ***
Parsing Benchmark Returns A Non-Empty Results Dict
    [Documentation]
    ...    Running the parsing benchmark must return a dict with at least one
    ...    entry.
    ${results}=    Run Parsing Benchmark
    Results Should Not Be Empty    ${results}

Parsing Benchmark Contains All Expected Names
    [Documentation]
    ...    The four built-in parsing benchmarks must all be present after a run.
    ${results}=    Run Parsing Benchmark
    Results Should Contain Benchmarks    ${results}
    ...    parse small suite
    ...    parse medium suite
    ...    parse large suite
    ...    parse resource file

All Parsing Benchmarks Have Positive Elapsed Time
    [Documentation]
    ...    Every benchmark in the results must report a strictly positive
    ...    elapsed time, confirming that timing is being captured correctly.
    ${results}=    Run Parsing Benchmark
    All Results Should Have Positive Elapsed Time    ${results}

Larger Suite Takes Longer Than Smaller Suite
    [Documentation]
    ...    Parsing a larger file should take at least as long as parsing a
    ...    smaller one, confirming that suite size affects measured time.
    ${results}=    Run Parsing Benchmark
    ${small_s}=    Get Result Elapsed Seconds    ${results}    parse small suite
    ${large_s}=    Get Result Elapsed Seconds    ${results}    parse large suite
    Should Be True    ${large_s} >= ${small_s}
    ...    msg=Expected large suite (${large_s}s) >= small suite (${small_s}s).

Parsing Benchmark Respects Iterations Parameter
    [Documentation]
    ...    Running with ``iterations=2`` should produce an aggregated result
    ...    whose mean elapsed time is still positive.
    ${results}=    Run Parsing Benchmark    iterations=2
    Results Should Contain Benchmarks    ${results}    parse small suite
    Result Elapsed Should Be Positive    ${results}    parse small suite

Small Suite Parse Time Is Within Reasonable Bounds
    [Documentation]
    ...    A sanity-check that the small suite parses in under 5 seconds, so
    ...    we detect if the benchmark is hanging or extremely slow.
    ${results}=    Run Parsing Benchmark
    Result Mean Should Be Less Than    ${results}    parse small suite    5000
