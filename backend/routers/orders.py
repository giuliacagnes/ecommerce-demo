from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import database
import auth as auth_utils

router = APIRouter(prefix="/orders", tags=["Orders"])


class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: str
    status: str
    total: float
    items: List[OrderItemResponse]
    created_at: str


def _enrich_order(order: dict) -> OrderResponse:
    enriched_items = []
    for item in order["items"]:
        enriched_items.append(OrderItemResponse(**item))
    return OrderResponse(
        id=order["id"],
        status=order["status"],
        total=order["total"],
        items=enriched_items,
        created_at=order["created_at"],
    )


@router.post("", response_model=OrderResponse, status_code=201)
def checkout(current_user: dict = Depends(auth_utils.get_current_user)):
    cart = database.get_cart(current_user["id"])
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total = 0.0
    for item in cart["items"]:
        product = database.get_product(item["product_id"])
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item['product_id']} no longer available")
        subtotal = product["price"] * item["quantity"]
        total += subtotal
        order_items.append({
            "product_id": item["product_id"],
            "product_name": product["name"],
            "quantity": item["quantity"],
            "price": product["price"],
            "subtotal": round(subtotal, 2),
        })

    order = database.create_order(current_user["id"], order_items, round(total, 2))
    database.clear_cart(current_user["id"])
    return _enrich_order(order)


@router.get("", response_model=List[OrderResponse])
def list_orders(current_user: dict = Depends(auth_utils.get_current_user)):
    orders = database.list_orders(current_user["id"])
    return [_enrich_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, current_user: dict = Depends(auth_utils.get_current_user)):
    order = database.get_order(order_id)
    if not order or order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Order not found")
    return _enrich_order(order)
