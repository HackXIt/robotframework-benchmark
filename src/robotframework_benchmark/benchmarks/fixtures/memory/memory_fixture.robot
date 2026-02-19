*** Settings ***
Library    Collections

*** Test Cases ***
Memory Fixture 1
    ${lst}=    Create List    a    b    c    d    e
    Log    ${lst}

Memory Fixture 2
    ${dct}=    Create Dictionary    key=value    foo=bar
    Log    ${dct}
