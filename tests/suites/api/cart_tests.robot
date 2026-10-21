*** Settings ***
Library     RequestsLibrary
Library     String
Resource    ../../resources/keywords.robot

Suite Setup     Run Keywords    Create Session To API    AND    Setup Cart Test User

*** Variables ***
${CART_TOKEN}    ${EMPTY}
${CART_HEADERS}    ${EMPTY}
${PRODUCT_ID}    ${EMPTY}

*** Keywords ***
Setup Cart Test User
    ${unique}=      Generate Random String    6    [LOWER]
    ${email}=       Set Variable    cart_${unique}@example.com
    Register User   ${email}    Test1234!    Cart User
    ${token}=       Login And Get Token    ${email}    Test1234!
    ${headers}=     Get Auth Headers    ${token}
    Set Suite Variable    ${CART_TOKEN}      ${token}
    Set Suite Variable    ${CART_HEADERS}    ${headers}
    ${pid}=         Get First Product ID
    Set Suite Variable    ${PRODUCT_ID}    ${pid}

*** Test Cases ***
Get Empty Cart
    ${resp}=    GET On Session    ecommerce    /cart    headers=${CART_HEADERS}    expected_status=200
    Should Be Empty    ${resp.json()['items']}

Add Item To Cart
    ${body}=    Create Dictionary    product_id=${PRODUCT_ID}    quantity=2
    ${resp}=    POST On Session    ecommerce    /cart/items    json=${body}    headers=${CART_HEADERS}    expected_status=200
    Should Not Be Empty    ${resp.json()['items']}
    Should Be Equal As Numbers    ${resp.json()['items'][0]['quantity']}    2

Update Item Quantity In Cart
    ${body}=    Create Dictionary    product_id=${PRODUCT_ID}    quantity=3
    ${resp}=    POST On Session    ecommerce    /cart/items    json=${body}    headers=${CART_HEADERS}    expected_status=200
    Should Be Equal As Numbers    ${resp.json()['items'][0]['quantity']}    3

Remove Item From Cart
    ${resp}=    DELETE On Session    ecommerce    /cart/items/${PRODUCT_ID}    headers=${CART_HEADERS}    expected_status=200
    Should Be Empty    ${resp.json()['items']}

Cart Requires Authentication
    GET On Session    ecommerce    /cart    expected_status=401
