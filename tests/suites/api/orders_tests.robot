*** Settings ***
Library     RequestsLibrary
Library     String
Resource    ../../resources/keywords.robot

Suite Setup     Run Keywords    Create Session To API    AND    Setup Order Test User

*** Variables ***
${ORDER_HEADERS}    ${EMPTY}

*** Keywords ***
Setup Order Test User
    ${unique}=      Generate Random String    6    [LOWER]
    ${email}=       Set Variable    order_${unique}@example.com
    Register User   ${email}    Test1234!    Order User
    ${token}=       Login And Get Token    ${email}    Test1234!
    ${headers}=     Get Auth Headers    ${token}
    Set Suite Variable    ${ORDER_HEADERS}    ${headers}
    # Add item to cart so checkout tests have something to work with
    ${pid}=         Get First Product ID
    ${body}=        Create Dictionary    product_id=${pid}    quantity=1
    POST On Session    ecommerce    /cart/items    json=${body}    headers=${ORDER_HEADERS}    expected_status=200

*** Test Cases ***
Checkout Creates Order And Clears Cart
    ${resp}=    POST On Session    ecommerce    /orders    headers=${ORDER_HEADERS}    expected_status=201
    ${order}=   Set Variable    ${resp.json()}
    Should Not Be Empty    ${order['id']}
    Should Be Equal As Strings    ${order['status']}    pending
    # Cart should now be empty
    ${cart}=    GET On Session    ecommerce    /cart    headers=${ORDER_HEADERS}    expected_status=200
    Should Be Empty    ${cart.json()['items']}

Checkout With Empty Cart Returns 400
    POST On Session    ecommerce    /orders    headers=${ORDER_HEADERS}    expected_status=400

List Orders Returns Created Order
    ${resp}=    GET On Session    ecommerce    /orders    headers=${ORDER_HEADERS}    expected_status=200
    ${orders}=  Set Variable    ${resp.json()}
    Should Not Be Empty    ${orders}

Get Order By ID
    ${list_resp}=   GET On Session    ecommerce    /orders    headers=${ORDER_HEADERS}    expected_status=200
    ${order_id}=    Set Variable    ${list_resp.json()[0]['id']}
    ${resp}=        GET On Session    ecommerce    /orders/${order_id}    headers=${ORDER_HEADERS}    expected_status=200
    Should Be Equal As Strings    ${resp.json()['id']}    ${order_id}

Orders Require Authentication
    GET On Session    ecommerce    /orders    expected_status=401
