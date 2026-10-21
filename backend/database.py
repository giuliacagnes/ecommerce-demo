from typing import Dict, List, Optional
from datetime import datetime
import uuid

# In-memory storage
_users: Dict[str, dict] = {}
_products: Dict[str, dict] = {}
_carts: Dict[str, dict] = {}  # keyed by user_id
_orders: Dict[str, dict] = {}

# Seed products
def _seed_products():
    items = [
        {"name": "Laptop Pro 15", "description": "High-performance laptop", "price": 1299.99, "category": "electronics", "stock": 10},
        {"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 29.99, "category": "electronics", "stock": 50},
        {"name": "USB-C Hub", "description": "7-in-1 USB-C hub", "price": 49.99, "category": "electronics", "stock": 30},
        {"name": "Mechanical Keyboard", "description": "Tactile mechanical keyboard", "price": 89.99, "category": "electronics", "stock": 20},
        {"name": "Monitor Stand", "description": "Adjustable aluminium monitor stand", "price": 39.99, "category": "accessories", "stock": 15},
        {"name": "Cotton T-Shirt", "description": "100% organic cotton t-shirt", "price": 19.99, "category": "clothing", "stock": 100},
        {"name": "Running Shoes", "description": "Lightweight running shoes", "price": 79.99, "category": "clothing", "stock": 25},
        {"name": "Python Cookbook", "description": "Advanced Python programming recipes", "price": 34.99, "category": "books", "stock": 40},
    ]
    for item in items:
        pid = str(uuid.uuid4())
        _products[pid] = {"id": pid, "created_at": datetime.utcnow().isoformat(), **item}


_seed_products()


# --- Users ---
def get_user_by_email(email: str) -> Optional[dict]:
    return next((u for u in _users.values() if u["email"] == email), None)

def get_user_by_id(user_id: str) -> Optional[dict]:
    return _users.get(user_id)

def create_user(email: str, hashed_password: str, full_name: str) -> dict:
    uid = str(uuid.uuid4())
    user = {"id": uid, "email": email, "hashed_password": hashed_password, "full_name": full_name, "created_at": datetime.utcnow().isoformat()}
    _users[uid] = user
    return user


# --- Products ---
def list_products(category: Optional[str] = None, search: Optional[str] = None) -> List[dict]:
    items = list(_products.values())
    if category:
        items = [p for p in items if p["category"] == category]
    if search:
        s = search.lower()
        items = [p for p in items if s in p["name"].lower() or s in p["description"].lower()]
    return items

def get_product(product_id: str) -> Optional[dict]:
    return _products.get(product_id)


# --- Cart ---
def get_cart(user_id: str) -> dict:
    if user_id not in _carts:
        _carts[user_id] = {"user_id": user_id, "items": []}
    return _carts[user_id]

def upsert_cart_item(user_id: str, product_id: str, quantity: int) -> dict:
    cart = get_cart(user_id)
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            return cart
    cart["items"].append({"product_id": product_id, "quantity": quantity})
    return cart

def remove_cart_item(user_id: str, product_id: str) -> dict:
    cart = get_cart(user_id)
    cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]
    return cart

def clear_cart(user_id: str):
    _carts[user_id] = {"user_id": user_id, "items": []}


# --- Orders ---
def create_order(user_id: str, items: list, total: float) -> dict:
    oid = str(uuid.uuid4())
    order = {"id": oid, "user_id": user_id, "items": items, "total": total, "status": "pending", "created_at": datetime.utcnow().isoformat()}
    _orders[oid] = order
    return order

def list_orders(user_id: str) -> List[dict]:
    return [o for o in _orders.values() if o["user_id"] == user_id]

def get_order(order_id: str) -> Optional[dict]:
    return _orders.get(order_id)
