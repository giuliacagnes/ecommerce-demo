from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
import database
import auth as auth_utils

router = APIRouter(prefix="/cart", tags=["Cart"])


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    product_id: str
    quantity: int
    product_name: str
    price: float
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float


def _enrich_cart(cart: dict) -> CartResponse:
    enriched = []
    total = 0.0
    for item in cart["items"]:
        product = database.get_product(item["product_id"])
        if product:
            subtotal = product["price"] * item["quantity"]
            total += subtotal
            enriched.append(CartItemResponse(
                product_id=item["product_id"],
                quantity=item["quantity"],
                product_name=product["name"],
                price=product["price"],
                subtotal=subtotal,
            ))
    return CartResponse(items=enriched, total=round(total, 2))


@router.get("", response_model=CartResponse)
def get_cart(current_user: dict = Depends(auth_utils.get_current_user)):
    cart = database.get_cart(current_user["id"])
    return _enrich_cart(cart)


@router.post("/items", response_model=CartResponse)
def add_or_update_item(body: CartItemRequest, current_user: dict = Depends(auth_utils.get_current_user)):
    product = database.get_product(body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if body.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Requested quantity exceeds available stock")
    cart = database.upsert_cart_item(current_user["id"], body.product_id, body.quantity)
    return _enrich_cart(cart)


@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_item(product_id: str, current_user: dict = Depends(auth_utils.get_current_user)):
    cart = database.remove_cart_item(current_user["id"], product_id)
    return _enrich_cart(cart)


@router.delete("", status_code=204)
def clear_cart(current_user: dict = Depends(auth_utils.get_current_user)):
    database.clear_cart(current_user["id"])
