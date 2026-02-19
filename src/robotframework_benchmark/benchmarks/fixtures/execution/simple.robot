*** Settings ***
Library    Collections

*** Test Cases ***
Log Message
    Log    Hello from benchmark

Create List
    ${items}=    Create List    a    b    c
    Should Contain    ${items}    b
