*** Settings ***
Library     RequestsLibrary
Library     Collections
Library     String
Resource    variables.robot

*** Keywords ***
Create Session To API
    Create Session    ecommerce    ${API_URL}    verify=True

Register User
    [Arguments]    ${email}    ${password}    ${full_name}
    ${body}=    Create Dictionary    email=${email}    password=${password}    full_name=${full_name}
    ${resp}=    POST On Session    ecommerce    /auth/register    json=${body}    expected_status=201
    RETURN    ${resp.json()}

Login And Get Token
    [Arguments]    ${email}    ${password}
    ${form}=    Create Dictionary    username=${email}    password=${password}
    ${resp}=    POST On Session    ecommerce    /auth/login    data=${form}    expected_status=200
    RETURN    ${resp.json()['access_token']}

Get Auth Headers
    [Arguments]    ${token}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    RETURN    ${headers}

Get First Product ID
    ${resp}=    GET On Session    ecommerce    /products    expected_status=200
    ${products}=    Set Variable    ${resp.json()}
    RETURN    ${products[0]['id']}
