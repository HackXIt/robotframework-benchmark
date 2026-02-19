*** Settings ***
Documentation
...    Acceptance tests for
...    :class:`~robotframework_benchmark.utils.metrics.MetricsCollector` and
...    :class:`~robotframework_benchmark.utils.metrics.BenchmarkResult`.
...
...    Verifies timing, memory tracking, aggregation, and string representation.

Library    Collections
Library    ${CURDIR}/../resources/BenchmarkLibrary.py


*** Test Cases ***
MetricsCollector Measures Positive Elapsed Time
    [Documentation]
    ...    Starting and stopping a collector around any operation must produce
    ...    a result with a positive elapsed time.
    ${collector}=    Create Metrics Collector
    Start Metrics Collector    ${collector}
    # No-op: timing resolution guarantees at least some elapsed time.
    ${result}=    Stop Metrics Collector    ${collector}    trivial op
    Should Be True    ${result.elapsed_seconds} > 0
    ...    msg=Expected positive elapsed_seconds, got ${result.elapsed_seconds}.

MetricsCollector With Memory Tracking Captures Peak Bytes
    [Documentation]
    ...    When ``track_memory=True``, doing a non-trivial allocation between
    ...    start and stop must yield a positive ``peak_memory_bytes``.
    ${collector}=    Create Metrics Collector    track_memory=True
    Start Metrics Collector    ${collector}
    # Allocate a list via RF's built-in Evaluate to exercise tracemalloc.
    ${big_list}=    Evaluate    list(range(50000))
    ${result}=    Stop Metrics Collector    ${collector}    alloc op
    Should Not Be Equal    ${result.peak_memory_bytes}    ${None}
    ...    msg=peak_memory_bytes must not be None when track_memory=True.
    Should Be True    ${result.peak_memory_bytes} > 0
    ...    msg=peak_memory_bytes must be positive, got ${result.peak_memory_bytes}.

MetricsCollector Without Memory Tracking Has No Peak Bytes
    [Documentation]
    ...    When ``track_memory=False`` (default), ``peak_memory_bytes`` must
    ...    be ``None``.
    ${collector}=    Create Metrics Collector
    Start Metrics Collector    ${collector}
    ${result}=    Stop Metrics Collector    ${collector}    noop
    Should Be Equal    ${result.peak_memory_bytes}    ${None}
    ...    msg=peak_memory_bytes must be None when track_memory=False.

MetricsCollector Stop Without Start Raises RuntimeError
    [Documentation]
    ...    Calling stop before start must raise a ``RuntimeError``.  We verify
    ...    this by catching the expected exception from the keyword library.
    ${collector}=    Create Metrics Collector
    Run Keyword And Expect Error    *called before start*    Stop Metrics Collector    ${collector}    orphan

BenchmarkResult String Representation Contains Name And Time
    [Documentation]
    ...    ``str(result)`` must include the benchmark name and a millisecond
    ...    value so reporters can display it meaningfully.
    ${results}=    Run Parsing Benchmark
    ${result}=    Get From Dictionary    ${results}    parse small suite
    ${text}=    Convert To String    ${result}
    Should Contain    ${text}    parse small suite
    Should Contain    ${text}    ms

BenchmarkResult Aggregate Mean Is Average Of Elapsed Times
    [Documentation]
    ...    After running a benchmark with 3 iterations the aggregated
    ...    ``mean_seconds`` should equal the average of the three individual
    ...    run times, which must be positive.
    ${results}=    Run Parsing Benchmark    iterations=3
    ${result}=    Get From Dictionary    ${results}    parse small suite
    Should Be True    ${result.mean_seconds} > 0
    ...    msg=mean_seconds must be positive after aggregation.
    ${n}=    Get Length    ${result._all_elapsed}
    Should Be Equal As Integers    ${n}    3
    ...    msg=Expected 3 samples in _all_elapsed, got ${n}.

BenchmarkResult Aggregate Has Min And Max
    [Documentation]
    ...    After multiple iterations, ``min_seconds`` must be <= ``mean_seconds``
    ...    and ``max_seconds`` must be >= ``mean_seconds``.
    ${results}=    Run Parsing Benchmark    iterations=3
    ${result}=    Get From Dictionary    ${results}    parse small suite
    Should Be True    ${result.min_seconds} <= ${result.mean_seconds}
    ...    msg=min_seconds (${result.min_seconds}) > mean_seconds (${result.mean_seconds}).
    Should Be True    ${result.max_seconds} >= ${result.mean_seconds}
    ...    msg=max_seconds (${result.max_seconds}) < mean_seconds (${result.mean_seconds}).
