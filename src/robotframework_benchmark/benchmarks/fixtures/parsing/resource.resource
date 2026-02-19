*** Settings ***
Documentation    A resource file for parsing benchmarks.

*** Variables ***
${GREETING}    Hello

*** Keywords ***
Greet
    [Arguments]    ${name}
    Log    ${GREETING}, ${name}!
