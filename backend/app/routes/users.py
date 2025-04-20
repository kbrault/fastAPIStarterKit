import os
import json
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config.auth import (
    get_current_admin,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    hash_password,
    verify_password
)
from app.config.database import get_db
from app.models.models import User
from app.models.schemas import UserCreate
from app.utils.responses import format_response

# Load environment variables
load_dotenv()

RATE_LIMIT_LOGIN = os.getenv("RATE_LIMIT_LOGIN", "5/10minutes")
RATE_LIMIT_REGISTER = os.getenv("RATE_LIMIT_REGISTER", "3/minute")

# Setup
router = APIRouter(tags=["Authentication", "Users"])
limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Domain Filtering Utility ---

def load_blocked_domains(filepath: str = "data/blocked_emails.json") -> set:
    with open(filepath, "r") as file:
        return set(json.load(file)["blocked_domains"])

BLOCKED_DOMAINS = load_blocked_domains()

def is_email_valid(email: str) -> bool:
    """Rejects emails from known disposable/blocked domains."""
    domain = email.split("@")[-1].lower()
    return domain not in BLOCKED_DOMAINS

# --- Endpoints ---

@router.post("/api/register")
@limiter.limit(RATE_LIMIT_REGISTER)
async def register_user(
    request: Request,
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user. Email domain is validated. Email must be unique.
    """
    user.email = user.email.lower()
    user.username = user.username.lower()

    if not is_email_valid(user.email):
        return format_response(
            "error",
            "Invalid email address.",
            errors=[{"field": "email", "issue": "Blocked domain"}],
            code=403
        )

    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar_one_or_none():
        return format_response("error", "Email already in use.", code=400)

    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role="user"
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        return format_response("error", "Database error.", code=500)

    return format_response(
        "success",
        "Registration successful.",
        data={
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        },
        code=200
    )

@router.post("/api/login")
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user using username and password. Returns access and refresh tokens.
    """
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        return format_response("error", "Invalid credentials.", code=400)

    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.username})

    return format_response(
        "success",
        "Login successful.",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        code=200
    )

@router.get("/api/users", dependencies=[Depends(get_current_admin)])
async def get_users(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all users (Admin only).
    """
    result = await db.execute(select(User.id, User.username, User.email, User.role))
    users = result.all()

    users_list = [
        {"id": uid, "username": uname, "email": uemail, "role": urole}
        for uid, uname, uemail, urole in users
    ]

    return format_response(
        "success",
        "Users retrieved successfully.",
        data=users_list,
        code=200
    )

@router.get("/api/user/{user_id}", dependencies=[Depends(get_current_admin)])
async def get_user(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a single user by ID (Admin only).
    """
    result = await db.execute(
        select(User.id, User.username, User.email, User.role).where(User.id == user_id)
    )
    user = result.fetchone()

    if not user:
        return format_response("error", "User not found.", code=404)

    return format_response(
        "success",
        "User retrieved successfully.",
        data={
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[3]
        },
        code=200
    )

@router.post("/api/refresh-token")
async def refresh_token(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """
    Refresh access token using a valid refresh token.
    """
    response = refresh_access_token(token)

    if response["status"] == "error":
        raise HTTPException(status_code=401, detail=response)

    return format_response(
        "success",
        "Token refreshed successfully.",
        data={
            "access_token": response["data"]["access_token"],
            "token_type": "bearer"
        },
        code=200
    )
