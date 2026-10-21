from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, products, cart, orders

app = FastAPI(
    title="ECommerce Demo API",
    description="Minimal e-commerce API for QA testing demonstrations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
