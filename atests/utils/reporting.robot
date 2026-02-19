*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.utils.reporting.ConsoleReporter` and
...    :class:`~robotframework_benchmark.utils.reporting.JsonReporter`.
...
...    Verifies that both reporters produce the expected output format given
...    real benchmark results.

Library    Collections
Library    String
Library    ${CURDIR}/../resources/BenchmarkLibrary.py


*** Test Cases ***
Console Reporter Produces Non-Empty Output
    [Documentation]
    ...    :class:`~ConsoleReporter` must produce non-empty string output when
    ...    given a populated results dict.
    ${results}=    Run Parsing Benchmark
    ${output}=    Console Report As String    ${results}
    Should Not Be Empty    ${output}
    ...    msg=Console reporter produced empty output.

Console Reporter Output Contains Benchmark Names
    [Documentation]
    ...    Each benchmark name from the parsing suite must appear somewhere in
    ...    the console report.
    ${results}=    Run Parsing Benchmark
    ${output}=    Console Report As String    ${results}
    Should Contain    ${output}    parse small suite
    Should Contain    ${output}    parse medium suite
    Should Contain    ${output}    parse large suite
    Should Contain    ${output}    parse resource file

Console Reporter Output Contains Table Borders
    [Documentation]
    ...    The console reporter uses Unicode box-drawing characters to draw a
    ...    table.  At least the bottom-left corner character ``└`` must appear.
    ${results}=    Run Parsing Benchmark
    ${output}=    Console Report As String    ${results}
    Should Contain    ${output}    └
    ...    msg=Expected table border character '└' in console output.

Console Reporter Output Contains Time Column Header
    [Documentation]
    ...    The table header must include the ``Mean(ms)`` column label.
    ${results}=    Run Parsing Benchmark
    ${output}=    Console Report As String    ${results}
    Should Contain    ${output}    Mean(ms)
    ...    msg=Expected 'Mean(ms)' column header in console output.

JSON Reporter Produces Valid JSON Array
    [Documentation]
    ...    :class:`~JsonReporter` must output a valid, non-empty JSON array.
    ${results}=    Run Parsing Benchmark
    ${json_str}=    Json Report As String    ${results}
    Json Report Should Be Valid    ${json_str}

JSON Reporter Output Contains All Benchmark Names
    [Documentation]
    ...    Every benchmark from the parsing suite must appear in the JSON
    ...    output under the ``name`` key.
    ${results}=    Run Parsing Benchmark
    ${json_str}=    Json Report As String    ${results}
    ${data}=    Evaluate    __import__('json').loads($json_str)
    ${reported_names}=    Evaluate    [entry['name'] for entry in $data]
    Should Contain    ${reported_names}    parse small suite
    Should Contain    ${reported_names}    parse medium suite
    Should Contain    ${reported_names}    parse large suite
    Should Contain    ${reported_names}    parse resource file

JSON Reporter Entry Has Required Fields
    [Documentation]
    ...    Each entry in the JSON output must have ``name``, ``mean_ms``,
    ...    ``min_ms``, ``max_ms``, and ``runs`` fields.
    ${results}=    Run Parsing Benchmark
    ${json_str}=    Json Report As String    ${results}
    ${data}=    Evaluate    __import__('json').loads($json_str)
    FOR    ${entry}    IN    @{data}
        Dictionary Should Contain Key    ${entry}    name
        Dictionary Should Contain Key    ${entry}    mean_ms
        Dictionary Should Contain Key    ${entry}    min_ms
        Dictionary Should Contain Key    ${entry}    max_ms
        Dictionary Should Contain Key    ${entry}    runs
    END

JSON Reporter Multi-Run Entry Has Stdev Field
    [Documentation]
    ...    When a benchmark is run more than once, the JSON entry must include
    ...    a ``stdev_ms`` field alongside the standard timing fields.
    ${results}=    Run Parsing Benchmark    iterations=3
    ${json_str}=    Json Report As String    ${results}
    ${data}=    Evaluate    __import__('json').loads($json_str)
    FOR    ${entry}    IN    @{data}
        Dictionary Should Contain Key    ${entry}    stdev_ms
        ...    msg=Expected 'stdev_ms' in multi-run JSON entry: ${entry}
    END

JSON Reporter Entry With Memory Has Peak Memory Field
    [Documentation]
    ...    When a result has ``peak_memory_bytes`` set, the JSON entry must
    ...    include a ``peak_memory_bytes`` field.  A crafted result is used
    ...    here to avoid running ``MemoryBenchmark`` (which calls
    ...    ``robot.api.TestSuite.run()``) inside the RF execution context.
    ${mem_result}=    Create Result With Memory Info    heap usage during parsing
    ...    elapsed_ms=2.5    peak_bytes=204800
    ${results}=    Create Dictionary    heap usage during parsing=${mem_result}
    ${json_str}=    Json Report As String    ${results}
    ${data}=    Evaluate    __import__('json').loads($json_str)
    ${entry}=    Get From List    ${data}    0
    Dictionary Should Contain Key    ${entry}    peak_memory_bytes
    ...    msg=Expected 'peak_memory_bytes' in JSON entry for a result with memory info.

Console Reporter Empty Results Prints Notice
    [Documentation]
    ...    Passing an empty dict to :class:`~ConsoleReporter` must produce a
    ...    human-readable "no results" message rather than a broken table.
    ${empty}=    Create Dictionary
    ${output}=    Console Report As String    ${empty}
    Should Contain    ${output}    No benchmark results
    ...    msg=Expected 'No benchmark results' notice for empty input.
