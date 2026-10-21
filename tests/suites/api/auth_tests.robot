*** Settings ***
Library     RequestsLibrary
Library     String
Resource    ../../resources/keywords.robot

Suite Setup     Create Session To API

*** Test Cases ***
Register New User Successfully
    ${unique}=    Generate Random String    6    [LOWER]
    ${email}=     Set Variable    test_${unique}@example.com
    ${user}=      Register User    ${email}    Test1234!    QA User
    Should Be Equal As Strings    ${user['email']}    ${email}
    Should Not Be Empty    ${user['id']}

Register With Duplicate Email Returns 400
    ${unique}=    Generate Random String    6    [LOWER]
    ${email}=     Set Variable    dup_${unique}@example.com
    Register User    ${email}    Test1234!    First User
    ${body}=      Create Dictionary    email=${email}    password=Test1234!    full_name=Second User
    ${resp}=      POST On Session    ecommerce    /auth/register    json=${body}    expected_status=400

Login With Valid Credentials Returns Token
    ${unique}=    Generate Random String    6    [LOWER]
    ${email}=     Set Variable    login_${unique}@example.com
    Register User    ${email}    Test1234!    Login Test
    ${token}=     Login And Get Token    ${email}    Test1234!
    Should Not Be Empty    ${token}

Login With Wrong Password Returns 401
    ${form}=    Create Dictionary    username=nobody@example.com    password=wrong
    POST On Session    ecommerce    /auth/login    data=${form}    expected_status=401

Get Current User Requires Auth
    GET On Session    ecommerce    /auth/me    expected_status=401

Get Current User With Valid Token
    ${unique}=    Generate Random String    6    [LOWER]
    ${email}=     Set Variable    me_${unique}@example.com
    Register User    ${email}    Test1234!    Me Test
    ${token}=     Login And Get Token    ${email}    Test1234!
    ${headers}=   Get Auth Headers    ${token}
    ${resp}=      GET On Session    ecommerce    /auth/me    headers=${headers}    expected_status=200
    Should Be Equal As Strings    ${resp.json()['email']}    ${email}
