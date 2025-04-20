import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext

from app.utils.responses import format_response

# --- Load environment variables ---
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing! Define it in your environment variables.")

# --- Auth setup ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=15)

# --- Password utils ---

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a password matches its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

# --- Token utils ---

def _get_expiration(minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> datetime:
    """Return expiration datetime in UTC."""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generate a signed JWT access token."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Generate a signed JWT refresh token."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    """Decode a JWT and return its payload or formatted error."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def refresh_access_token(refresh_token: str) -> dict:
    """Validate a refresh token and return a new access token if valid."""
    payload = decode_token(refresh_token)
    if not payload or "sub" not in payload:
        return format_response("error", "Invalid refresh token.", code=401)

    access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload.get("role", "user")
    })
    return format_response(
        "success",
        "Token refreshed successfully.",
        data={"access_token": access_token, "token_type": "bearer"},
        code=200
    )

# --- Dependency-based access control ---

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Retrieve and validate the current user from JWT token."""
    payload = decode_token(token)
    if not payload or "role" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token or missing role.")
    
    if payload["role"] not in {"user", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    
    return payload

def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    """Retrieve current user and ensure they are an admin."""
    user = get_current_user(token)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
    return user
