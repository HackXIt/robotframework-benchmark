*** Settings ***
Library    String

*** Keywords ***
Repeat Uppercase
    [Arguments]    ${text}    ${count}
    FOR    ${_}    IN RANGE    ${count}
        ${upper}=    Convert To Uppercase    ${text}
    END
    RETURN    ${upper}

*** Test Cases ***
Keyword Invocation
    Repeat Uppercase    benchmark    10
