# ECommerce Demo

Minimal e-commerce application built with FastAPI + vanilla JS, designed for QA testing demos with Robot Framework.

## Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | FastAPI (Python) |
| Frontend | HTML / CSS / JS |
| Storage  | In-memory (resets on restart) |
| API Docs | Swagger UI at `/docs` |

## Features

- **Auth**: register, login (JWT), get current user
- **Products**: list, filter by category, search, get by ID
- **Cart**: add/update/remove items, clear
- **Orders**: checkout from cart, list orders, get order by ID

---

## Run locally

```bash
# 1. Create virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload
```

The app is available at **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

---

## Run Robot Framework tests

```bash
# 1. Install test dependencies (separate venv recommended)
cd tests
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. (First time only) Install Browser Library browsers
rfbrowser init

# 3. Run all API tests
robot suites/api/

# 4. Run a single suite
robot suites/api/auth_tests.robot

# 5. Run with HTML report
robot --outputdir results suites/api/
```

---

## Project structure

```
ecommerce-demo/
├── backend/
│   ├── main.py              # FastAPI app + router registration
│   ├── database.py          # In-memory storage + seed data
│   ├── auth.py              # JWT helpers + get_current_user dependency
│   ├── routers/
│   │   ├── auth.py          # POST /auth/register, /auth/login, GET /auth/me
│   │   ├── products.py      # GET /products, /products/categories, /products/{id}
│   │   ├── cart.py          # GET/POST/DELETE /cart
│   │   └── orders.py        # POST/GET /orders
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── tests/
    ├── requirements.txt     # robotframework + libraries
    ├── resources/
    │   ├── variables.robot  # BASE_URL and test credentials
    │   └── keywords.robot   # Reusable keywords (session, login, etc.)
    └── suites/
        ├── api/
        │   ├── auth_tests.robot
        │   ├── products_tests.robot
        │   ├── cart_tests.robot
        │   └── orders_tests.robot
        └── ui/              # Ready for Browser Library UI tests
```

---

## API quick reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login → JWT token |
| GET | `/auth/me` | Yes | Current user info |
| GET | `/products` | No | List products (filter: `category`, `search`) |
| GET | `/products/categories` | No | Available categories |
| GET | `/products/{id}` | No | Product detail |
| GET | `/cart` | Yes | Get cart |
| POST | `/cart/items` | Yes | Add/update cart item |
| DELETE | `/cart/items/{id}` | Yes | Remove cart item |
| DELETE | `/cart` | Yes | Clear cart |
| POST | `/orders` | Yes | Checkout → create order |
| GET | `/orders` | Yes | List user orders |
| GET | `/orders/{id}` | Yes | Order detail |
