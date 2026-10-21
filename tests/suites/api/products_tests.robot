*** Settings ***
Library     RequestsLibrary
Resource    ../../resources/keywords.robot

Suite Setup     Create Session To API

*** Test Cases ***
List Products Returns Non-Empty List
    ${resp}=    GET On Session    ecommerce    /products    expected_status=200
    ${products}=    Set Variable    ${resp.json()}
    Should Not Be Empty    ${products}

List Products Filtered By Category
    ${resp}=    GET On Session    ecommerce    /products?category=electronics    expected_status=200
    ${products}=    Set Variable    ${resp.json()}
    Should Not Be Empty    ${products}
    FOR    ${p}    IN    @{products}
        Should Be Equal As Strings    ${p['category']}    electronics
    END

Search Products By Name
    ${resp}=    GET On Session    ecommerce    /products?search=laptop    expected_status=200
    ${products}=    Set Variable    ${resp.json()}
    Should Not Be Empty    ${products}

Get Product By Valid ID
    ${product_id}=    Get First Product ID
    ${resp}=          GET On Session    ecommerce    /products/${product_id}    expected_status=200
    Should Not Be Empty    ${resp.json()['name']}

Get Product By Invalid ID Returns 404
    GET On Session    ecommerce    /products/nonexistent-id    expected_status=404

List Product Categories
    ${resp}=    GET On Session    ecommerce    /products/categories    expected_status=200
    ${categories}=    Set Variable    ${resp.json()}
    Should Contain    ${categories}    electronics
