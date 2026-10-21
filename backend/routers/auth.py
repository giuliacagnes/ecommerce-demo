from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel, EmailStr
import database
import auth as auth_utils

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    if database.get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth_utils.hash_password(body.password)
    user = database.create_user(body.email, hashed, body.full_name)
    return UserResponse(**{k: v for k, v in user.items() if k != "hashed_password"})


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = database.get_user_by_email(form.username)
    if not user or not auth_utils.verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth_utils.create_access_token(user["id"])
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(auth_utils.get_current_user)):
    return UserResponse(**{k: v for k, v in current_user.items() if k != "hashed_password"})
