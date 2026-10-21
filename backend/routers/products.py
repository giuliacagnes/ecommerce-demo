from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import database

router = APIRouter(prefix="/products", tags=["Products"])


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock: int
    created_at: str


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
):
    return database.list_products(category=category, search=search)


@router.get("/categories", response_model=List[str])
def list_categories():
    products = database.list_products()
    return sorted(set(p["category"] for p in products))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    product = database.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
